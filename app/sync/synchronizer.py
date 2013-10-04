import datetime
import os
import threading
import time
from Queue import Queue

from download import DownloadThread
from upload import UploadThread
from watcher import Watcher

from fs.osfs import OSFS

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from definitions import Base, RemoteFile, LocalFile, TempLocalFile

import common


class Synchronizer(threading.Thread):
    def __init__(self, parent=None):
        threading.Thread.__init__(self)
        self.parent = parent
        self.api = self.parent.smartfile
        self._syncDir = self.parent.syncDir
        # Set the thread to run as a daemon
        self.setDaemon(True)
        # Initialize the database
        self.dbInit()
        # Setup queues for tasks
        self.uploadQueue = Queue()
        self.downloadQueue = Queue()
        # Queue for events to send to the realtime sync server
        self.changesQueue = Queue()
        # List of files that the watcher should ignore
        self.ignoreFiles = []
        # Get the time offset to use in time calculations
        self._timeoffset = common.calculate_time_offset()

        self.watcherRunning = False

    def run(self):
        # Start the transfer threads to wait for tasks
        self.startTransferThreads()
        # Watch the file system
        self.watchFileSystem()
        # Synchronize with SmartFile
        self.synchronize()

    def startTransferThreads(self):
        # Initialize the upload and download threads

        upload = 4  # Specify amount of upload threads
        download = 5  # Specify amount of download threads

        self.uploadThreads = []
        for i in range(upload):
            uploader = UploadThread(self.uploadQueue, self.api, self._syncDir, self)
            uploader.start()
            self.uploadThreads.append(uploader)

        self.downloadThreads = []
        for i in range(download):
            downloader = DownloadThread(self.downloadQueue, self.api, self._syncDir)
            downloader.start()
            self.downloadThreads.append(downloader)

    def dbInit(self):
        engine = create_engine('sqlite:///files.db', echo=False)
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        self.__session = Session()

    def synchronize(self):
        while True:
            # Clear the remote tables from DB
            self.clearTables()
            # Index the remote files and store in DB
            self.indexRemote()
            self.dbCommit()
            # Index the local files and store in DB
            self.indexLocal()
            self.dbCommit()
            # Now compare the tables and populate task queues
            self.compare()

            # Wait 5 minutes, then check with SmartFile again
            wait_time = 5
            time.sleep(wait_time * 60)

    def addRemoteFile(self, path, checksum, modified, size, isDir):
        remotefile = RemoteFile(path, checksum, modified, size, isDir)
        self.__session.add(remotefile)

    def addLocalFile(self, path, system_path, checksum, modified, modified_local, size, isDir):
        localfile = LocalFile(path, system_path, checksum, modified, modified_local, size, isDir)
        self.__session.add(localfile)

    def addTempLocalFile(self, path, checksum, modified, isDir):
        tempfile = TempLocalFile(path, checksum, modified, isDir)
        self.__session.add(tempfile)

    def clearTables(self):
        for row in self.__session.query(RemoteFile):
            self.__session.delete(row)

        for row in self.__session.query(LocalFile):
            self.__session.delete(row)

    def dbCommit(self):
        self.__session.commit()

    def watchFileSystem(self):
        self.localWatcher = Watcher(self, self.api, self._syncDir)
        self.localWatcher.start()
        self.watcherRunning = True

    def compare(self):
        local = self.__session.query(LocalFile).all()
        remote = self.__session.query(RemoteFile).all()

        objectsOnBoth = []

        # Check which files exist on both and which local files dont exist on remote
        for localObject in local:
            found = False
            foundObject = None
            for remoteObject in remote:
                if localObject.path == remoteObject.path:
                    found = True
                    foundObject = remoteObject
            if found:
                objectsOnBoth.append((localObject, foundObject))
            else:
                self.uploadQueue.put(localObject)
            found = False
            foundObject = None

        # Check which remote files dont exist on local
        for remoteObject in remote:
            found = False
            for localObject in local:
                if remoteObject.path == localObject.path:
                    found = True
            if not found:
                ignorePath = os.path.join(self._syncDir, remoteObject.path)
                self.ignoreFiles.append(ignorePath)
                self.downloadQueue.put(remoteObject)
            found = False

        # Check which way to synchronize files
        for object in objectsOnBoth:
            localObject = object[0]
            remoteObject = object[1]
            if localObject.checksum != remoteObject.checksum:
                if localObject.modified_local > remoteObject.modified:
                    self.uploadQueue.put(localObject)
                elif localObject.modified_local < remoteObject.modified:
                    ignorePath = os.path.join(self._syncDir, remoteObject.path)
                    self.ignoreFiles.append(ignorePath)
                    self.downloadQueue.put(remoteObject)

        # Clear objects on both
        objectsOnBoth = None

    def indexLocal(self, localPath=None):
        """
        Indexes the local files
        """
        if localPath is None:
            localPath = self._syncDir

        syncFS = OSFS(localPath)

        for path in syncFS.walkfiles():
            systemPath = syncFS.getsyspath(path).strip("\\\\?\\")
            checksum = common.getFileHash(systemPath)
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(systemPath)).replace(microsecond=0) - self._timeoffset
            size = syncFS.getsize(path)
            isDir = syncFS.isdir(path)

            if not path.endswith("~"):
                # Add the file to the database
                self.addLocalFile(path, systemPath, checksum, None, modified, size, isDir)

    def indexRemote(self, remotePath=None):
        #TODO: keep a database on kissync.com to keep track of directories
        # SmartFile has enough caching on both the /path/info and the logs
        # endpoint, that it cannot be relied upon for real time updates
        """
        Index the files on SmartFile and dive into directories when necessary
        """
        filesIndexed = False
        while filesIndexed is not True:
            if remotePath is None:
                remotePath = "/"
            apiPath = '/path/info%s' % remotePath
            try:
                dirListing = self.api.get(apiPath, children=True)
            except:
                continue
            if "children" in dirListing:
                for i in dirListing['children']:
                    if i['isfile'] is False:
                        # If the path is a directory
                        path = i['path']
                        isDir = True
                        size = None
                        # Check if modified is in attributes and use that
                        try:
                            if "modified" in i['attributes']:
                                modified = i['attributes']['modified']
                                modified = datetime.datetime.strptime(modified, '%Y-%m-%d %H:%M:%S')
                            # Or else, just use the modified time set by the api
                            else:
                                modified = i['time']
                                modified = datetime.datetime.strptime(modified, '%Y-%m-%dT%H:%M:%S')
                        except:
                            modified = i['time']
                            modified = datetime.datetime.strptime(modified, '%Y-%m-%dT%H:%M:%S')
                        checksum = None

                        # Add the folder to the database
                        self.addRemoteFile(path, checksum, modified, size, isDir)
                        # Dive into the directory and look for more
                        self.indexRemote(i['path'])
                    else:
                        # If the path is a file
                        path = i['path']
                        isDir = False
                        size = int(i['size'])
                        # Check if modified is in attributes and use that
                        try:
                            if "modified" in i['attributes']:
                                modified = i['attributes']['modified']
                                modified = datetime.datetime.strptime(modified, '%Y-%m-%d %H:%M:%S')
                            # Or else, just use the modified time set by the api
                            else:
                                modified = i['time']
                                modified = datetime.datetime.strptime(modified, '%Y-%m-%dT%H:%M:%S')
                        except:
                            modified = i['time']
                            modified = datetime.datetime.strptime(modified, '%Y-%m-%dT%H:%M:%S')
                        if 'checksum' in i['attributes']:
                            checksum = i['attributes']['checksum']
                        else:
                            checksum = None

                        # Add the file to the database
                        self.addRemoteFile(path, checksum, modified, size, isDir)
            filesIndexed = True
