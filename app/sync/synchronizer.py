import datetime
import os
import threading

import common

from Queue import Queue

from download import DownloadThread
from upload import UploadThread
from sync import SyncUp, SyncDown
from watcher import Watcher

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from definitions import Base, RemoteFile, LocalFile, TempLocalFile


class Synchronizer(threading.Thread):
    def __init__(self, parent=None):
        threading.Thread.__init__(self)
        self.parent = parent
        # Initialize the database
        self.dbInit()

        self.uploadQueue = Queue()
        self.downloadQueue = Queue()
        self.syncUpQueue = Queue()
        self.syncDownQueue = Queue()

        self.uploader = UploadThread(self.uploadQueue, self.parent.smartfile, self.parent.syncDir)
        self.downloader = DownloadThread(self.downloadQueue, self.parent.smartfile, self.parent.syncDir)
        self.syncUp = SyncUp(self.syncUpQueue, self.parent.smartfile, self.parent.sync, self.parent.syncDir)
        self.syncDown = SyncDown(self.syncDownQueue, self.parent.smartfile, self.parent.sync, self.parent.syncDir)

        self._timeoffset = None

        # Set the thread to run as a daemon
        self.setDaemon(True)

    def run(self):
        self.synchronize()

    def dbInit(self):
        engine = create_engine('sqlite:///files.db', echo=False)
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()

    def synchronize(self):
        if self._timeoffset is None:
            self._timeoffset = common.calculate_time_offset()
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
        #self.watchFileSystem()

    def addRemoteFile(self, path, checksum, modified, size, isDir):
        remotefile = RemoteFile(path, checksum, modified, size, isDir)
        self.session.add(remotefile)

    def addLocalFile(self, path, checksum, modified, modified_local, size, isDir):
        localfile = LocalFile(path, checksum, modified, modified_local, size, isDir)
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
        self.localFileWatcher = Watcher(self, self.parent.smartfile, self.parent.syncDir)
        self.localFileWatcher.start()

    def compare(self):
        local = self.session.query(LocalFile).all()
        remote = self.session.query(RemoteFile).all()

        objectsOnBoth = []

        # Eventually this will be done with more SQL queries...

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

        print "Objects on both"
        print objectsOnBoth
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
            localPath = self.parent.syncDir
        for (paths, dirs, files) in os.walk(localPath):
            for item in files:
                path = os.path.join(paths, item)
                checksum = common.getFileHash(path)
                modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0) - self._timeoffset
                size = int(os.path.getsize(path))
                isDir = os.path.isdir(path)
                path = path.replace(localPath, '')

                self.addLocalFile(path, checksum, None, modified, size, isDir)

    def indexRemote(self, remotePath=None):
        """
        Recursively indexes the remote directory since we cannot see the directories all at once
        """
        if remotePath is None:
            remotePath = "/"
        apiPath = '/path/info%s' % remotePath
        dirListing = self.parent.smartfile.get(apiPath, children=True)
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
