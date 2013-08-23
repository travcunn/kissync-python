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


class Synchronizer(threading.Thread):
    def __init__(self, parent=None):
        threading.Thread.__init__(self)
        self.parent = parent
        self.api = self.parent.smartfile
        self.syncDir = self.parent.syncDir

        # Set the thread to run as a daemon
        self.setDaemon(True)

        # Initialize the database
        self.dbInit()

        self.uploadQueue = Queue()
        self.downloadQueue = Queue()
        self.syncUpQueue = Queue()
        self.syncDownQueue = Queue()

        self.uploader = UploadThread(self.uploadQueue, self.api, self.syncDir)
        self.downloader = DownloadThread(self.downloadQueue, self.api, self.syncDir)
        self.syncUp = SyncUpThread(self.syncUpQueue, self.api, self.parent.sync, self.syncDir)
        self.syncDown = SyncDownThread(self.syncDownQueue, self.api, self.parent.sync, self.syncDir)

        self._timeoffset = common.calculate_time_offset()

    def run(self):
        self.synchronize()

    def dbInit(self):
        engine = create_engine('sqlite:///files.db', echo=False)
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()

    def synchronize(self):
        self.clearTables()
        self.indexRemote()
        self.dbCommit()
        self.indexLocal()
        self.dbCommit()

        # Now compare the lists and populate task queues for differences
        self.compare()

        self.uploader.start()
        self.downloader.start()
        self.syncUp.start()
        self.syncDown.start()

        self.uploadQueue.join()
        self.downloadQueue.join()
        self.syncUpQueue.join()
        self.syncDownQueue.join()

        print "Joined all the queues"
        # Now watch the file system for changes
        self.watchFileSystem()

    def addRemoteFile(self, path, checksum, modified, size, isDir):
        remotefile = RemoteFile(path, checksum, modified, size, isDir)
        self.session.add(remotefile)

    def addLocalFile(self, path, system_path, checksum, modified, modified_local, size, isDir):
        localfile = LocalFile(path, system_path, checksum, modified, modified_local, size, isDir)
        self.session.add(localfile)

    def addTempLocalFile(self, path, checksum, modified, isDir):
        tempfile = TempLocalFile(path, checksum, modified, isDir)
        self.session.add(tempfile)

    def clearTables(self):
        for row in self.session.query(RemoteFile):
            self.session.delete(row)

        for row in self.session.query(LocalFile):
            self.session.delete(row)

    def dbCommit(self):
        self.session.commit()

    def watchFileSystem(self):
        #after uploading, downloading, and synchronizing are finished, start the watcher thread
        self.localFileWatcher = Watcher(self, self.api, self.syncDir)
        self.localFileWatcher.start()

    def compare(self):
        local = self.session.query(LocalFile).all()
        remote = self.session.query(RemoteFile).all()

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
            if localObject.checksum is not remoteObject.checksum:
                if localObject.modified_local > remoteObject.modified:
                    self.syncUpQueue.put(object)
                elif localObject.modified_local < remoteObject.modified:
                    self.syncDownQueue.put(object)

    def indexLocal(self, localPath=None):
        """
        Indexes the local files
        """
        if localPath is None:
            localPath = self.syncDir

        syncFS = OSFS(localPath)

        for path in syncFS.walkfiles():
            systemPath = syncFS.getsyspath(path).strip("\\\\?\\")
            checksum = common.getFileHash(systemPath)
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(systemPath)).replace(microsecond=0) - self._timeoffset
            size = syncFS.getsize(path)
            isDir = syncFS.isdir(path)

            self.addLocalFile(path, systemPath, checksum, None, modified, size, isDir)

    def indexRemote(self, remotePath=None):
        """
        Recursively indexes the remote directory since we cannot see the directories all at once
        """
        if remotePath is None:
            remotePath = "/"
        apiPath = '/path/info%s' % remotePath
        dirListing = self.api.get(apiPath, children=True)
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

                    # Add that bad boy file to the database!
                    self.addRemoteFile(path, checksum, modified, size, isDir)
