import datetime
import os
import threading
from Queue import Queue

from download import DownloadThread
from upload import UploadThread
from sync import SyncUpThread, SyncDownThread
from watcher import Watcher

from fs.osfs import OSFS

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from definitions import Base, RemoteFile, LocalFile, TempLocalFile

import common

# Sync should be implemented in a later version
# -- for now, just use download/upload
# Attempt loading the SyncClient
try:
    from smartfile.sync import SyncClient
except:
    _syncLoaded = False
else:
    _syncLoaded = True
# Turn off SyncClient for now
_syncLoaded = False


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

        self.uploadQueue = Queue()
        self.downloadQueue = Queue()
        self.syncUpQueue = Queue()
        self.syncDownQueue = Queue()
        # Queue for events to send to the realtime sync server
        self.changesQueue = Queue()

        # List of files that the watcher should ignore
        self.ignoreFiles = []

        self._timeoffset = common.calculate_time_offset()

        if _syncLoaded:
            self.syncLoaded = True
        else:
            self.syncLoaded = False

        self.watcherRunning = False

    def run(self):
        self.synchronize()

    def startTransferThreads(self):
        # Initialize the uploader and downloader
        self.uploader = UploadThread(self.uploadQueue, self.api,
                self._syncDir, self)
        self.downloader = DownloadThread(self.downloadQueue, self.api,
                self._syncDir)
        self.uploader.start()
        self.downloader.start()
        if _syncLoaded:
            self._sync = SyncClient(self.api)
            self.syncUp = SyncUpThread(self.syncUpQueue, self.api,
                    self._sync, self._syncDir, self)
            self.syncDown = SyncDownThread(self.syncDownQueue, self.api,
                    self._sync, self._syncDir)
            self.syncUp.start()
            self.syncDown.start()

    def dbInit(self):
        engine = create_engine('sqlite:///files.db', echo=False)
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        self.__session = Session()

    def synchronize(self):
        # Start the transfer threads to wait for tasks
        self.startTransferThreads()
        # Clear the remote tables
        self.clearTables()
        # Index the remote files
        self.indexRemote()
        self.dbCommit()
        # Index the local files
        self.indexLocal()
        self.dbCommit()

        # Now compare the lists and populate task queues
        self.compare()

        self.uploadQueue.join()
        self.downloadQueue.join()

        if _syncLoaded:
            self.syncUpQueue.join()
            self.syncDownQueue.join()

        print "Initial sync finished"

        # Now watch the file system for changes
        # TODO: start this alongside the file comparisons
        self.watchFileSystem()

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
        #after uploading, downloading, and synchronizing are finished, start the watcher thread
        self.localWatcher = Watcher(self, self.api, self._syncDir)
        self.localWatcher.start()
        self.watcherRunning = True

    def compare(self):
        local = self.__session.query(LocalFile).all()
        remote = self.__session.query(RemoteFile).all()

        objectsOnBoth = []

        # Eventually this will be done with more SQLAlchemy queries...

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
                self.downloadQueue.put(remoteObject)
            found = False

        # Check which way to synchronize files
        for object in objectsOnBoth:
            localObject = object[0]
            remoteObject = object[1]
            print("Objects in both:")
            print("Local Object:", localObject)
            print("   path:", localObject.path)
            print("   checksum:", localObject.checksum)
            print("Remote Object:", remoteObject)
            print("   path:", remoteObject.path)
            print("   checksum:", remoteObject.checksum)
            if localObject.checksum != remoteObject.checksum:
                if localObject.modified_local > remoteObject.modified:
                    if self.syncLoaded:
                        self.syncUpQueue.put(localObject)
                    else:
                        self.uploadQueue.put(localObject)
                elif localObject.modified_local < remoteObject.modified:
                    if self.syncLoaded:
                        self.syncDownQueue.put(localObject)
                    else:
                        self.downloadQueue.put(remoteObject)

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
                        path = i['path'].encode("utf-8")
                        isDir = True
                        size = None
                        # Check if modified is in attributes and use that
                        if "modified" in i['attributes']:
                            modified = i['attributes']['modified'].encode("utf-8")
                            modified = datetime.datetime.strptime(modified, '%Y-%m-%d %H:%M:%S')
                        # Or else, just use the modified time set by the api
                        else:
                            modified = i['time'].encode("utf-8")
                            modified = datetime.datetime.strptime(modified, '%Y-%m-%dT%H:%M:%S')
                        checksum = None

                        # Add the folder to the database
                        self.addRemoteFile(path, checksum, modified, size, isDir)
                        # Dive into the directory and look for more
                        self.indexRemote(i['path'])
                    else:
                        # If the path is a file
                        path = i['path'].encode("utf-8")
                        isDir = False
                        size = int(i['size'])
                        # Check if modified is in attributes and use that
                        if "modified" in i['attributes']:
                            modified = i['attributes']['modified'].encode("utf-8")
                            modified = datetime.datetime.strptime(modified, '%Y-%m-%d %H:%M:%S')
                        # Or else, just use the modified time set by the api
                        else:
                            modified = i['time'].encode("utf-8")
                            modified = datetime.datetime.strptime(modified, '%Y-%m-%dT%H:%M:%S')
                        if 'checksum' in i['attributes']:
                            checksum = i['attributes']['checksum'].encode("utf-8")
                        else:
                            checksum = None

                        # Add the file to the database
                        self.addRemoteFile(path, checksum, modified, size, isDir)
            filesIndexed = True
