import datetime
import os
import threading

import common

from Queue import Queue

from downloader import Downloader
from uploader import Uploader
from sync import SyncUp, SyncDown
from watcher import Watcher

from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from definitions import *


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

        # Specialized queue for downloading files and setting attributes
        # It handles files that werent uploaded using kissync
        self.downSyncQueue = Queue()

        self.uploader = Uploader(self.uploadQueue, self.parent.smartfile, self.parent.syncDir)
        self.downloader = Downloader(self.downloadQueue, self.parent.smartfile, self.parent.syncDir)
        self.syncUp = SyncUp(self.syncUpQueue, self.parent.smartfile, self.parent.sync, self.parent.syncDir)
        self.syncDown = SyncDown(self.syncDownQueue, self.parent.smartfile, self.parent.sync, self.parent.syncDir)

        #self.downSync = DownSync(self, self.downSyncQueue, self.parent.smartfile, self.parent.sync, self.parent.syncDir)

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
        self.clearTables()
        self.indexRemote()
        self.dbCommit()
        self.indexLocal()
        self.dbCommit()

        # Now compare the lists and populate task queues for differences
        self.compare()

        self.uploader.start()
        self.downloader.start()

    def addRemoteFile(self, path, checksum, modified, size, isDir):
        remotefile = RemoteFile(path, checksum, modified, size, isDir)
        self.session.add(remotefile)

    def addLocalFile(self, path, checksum, modified, modified_local, size, isDir):
        localfile = LocalFile(path, checksum, modified, modified_local, size, isDir)
        self.session.add(localfile)

    def addTempLocalFile(path, checksum, modified, isDir):
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

        objectsNotRemote = []
        objectsNotLocal = []

        # Check which files exist on both and which local files dont exist on remote
        for localObject in local:
            found = False
            for remoteObject in remote:
                if localObject.path == remoteObject.path:
                    found = True
            if found:
                objectsOnBoth.append((localObject, remoteObject))
            else:
                objectsNotRemote.append(localObject)
            found = False

        # Check which remote files dont exist on local
        for remoteObject in remote:
            found = False
            for localObject in local:
                if remoteObject.path == localObject.path:
                    found = True
            if not found:
                objectsNotLocal.append(remoteObject)
            found = False

        # TODO: iterate through each object in objectsOnBoth and add to the queues

        for object in objectsNotLocal:
            print "Need to download: ", object.path
            self.downloadQueue.put(object)

        for object in objectsNotRemote:
            print "Need to upload: ", object.path
            self.uploadQueue.put(object)

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
                modified = datetime.datetime.fromtimestamp(os.path.getmtime(path))
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
                    modified = i['time'].encode("utf-8")
                    modified = datetime.datetime.strptime(modified, '%Y-%m-%dT%H:%M:%S')

                    if 'checksum' in i['attributes']:
                        checksum = i['attributes']['checksum'].encode("utf-8")
                    else:
                        checksum = None
                    # Add that bad boy file to the database!
                    self.addRemoteFile(path, checksum, modified, size, isDir)

