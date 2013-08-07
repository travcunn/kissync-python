import datetime
import hashlib
import os
import threading
import time

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

    def addRemoteFile(self, path, checksum, modified, size, isDir):
        remotefile = RemoteFile(path, checksum, modified, size, isDir)
        self.session.add(remotefile)

    def addLocalFile(self, path, checksum, modified, modified_local, size, isDir):
        localfile = LocalFile(path, checksum, modified, modified_local, size, isDir)
        self.session.add(localfile)

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
        # Query to list all localfile paths
        localpaths = self.session.query(LocalFile).all()
        remotepaths = self.session.query(RemoteFile).all()

        """
        for item in localpaths:
            print item.path
        """
        itemsOnBoth = set(localpaths) & set(remotepaths)
        itemsNotRemote = set(localpaths) - set(remotepaths)
        itemsNotLocal = set(remotepaths) - set(localpaths)

        for item in itemsNotLocal:
            print item.path

    def indexLocal(self, localPath=None):
        """
        Indexes the local files
        """
        if localPath is None:
            localPath = self.parent.syncDir
        for (paths, dirs, files) in os.walk(localPath):
            for item in files:
                path = os.path.join(paths, item)
                checksum = self._getFileHash(path)
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
                if i['isdir']:
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
                    isDir = i['isdir']
                    size = int(i['size'])
                    modified = i['time'].encode("utf-8")
                    modified = datetime.datetime.strptime(modified, '%Y-%m-%dT%H:%M:%S')

                    if 'checksum' in i['attributes']:
                        checksum = i['attributes']['checksum'].encode("utf-8")
                    else:
                        checksum = None

                    # Add that bad boy file to the database!
                    self.addRemoteFile(path, checksum, modified, size, isDir)

    def _getFileHash(self, filepath):
        """
        Returns the MD5 hash of a local file
        """
        fileToHash = open(filepath)
        md5 = hashlib.md5()
        while True:
            currentLine = fileToHash.readline()
            if not currentLine:
                break
            md5.update(currentLine)
        return md5.hexdigest()

