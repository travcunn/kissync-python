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

from sqlalchemy.orm import sessionmaker
from definitions import *

import pprint


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

        self.uploader = Uploader(self.uploadQueue, self.parent.smartfile, self.parent.syncDir)
        self.downloader = Downloader(self.downloadQueue, self.parent.smartfile, self.parent.syncDir)
        self.syncUp = SyncUp(self.syncUpQueue, self.parent.smartfile, self.parent.sync, self.parent.syncDir)
        self.syncDown = SyncDown(self.syncDownQueue, self.parent.smartfile, self.parent.sync, self.parent.syncDir)

        # Set the thread to run as a daemon
        self.setDaemon(True)

    def run(self):
        self.synchronize()

    def dbInit(self):
        engine = create_engine('sqlite:///files.db', echo=True)
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()

    def synchronize(self):
        # Get the local and remote file information
        self.remoteFilesList()
        self.dbCommit()
        self.localFilesList()
        self.dbCommit()

        #Now compare the lists and populate task queues for differences
        #self.compareListing()

        #self.uploader.start()
        #self.downloader.start()
        #self.syncUp.start()
        #self.syncDown.start()

        #Wait for the uploading and downloading tasks to finish
        #self.uploadQueue.join()
        #self.downloadQueue.join()
        #self.syncUpQueue.join()
        #self.syncDownQueue.join()
        #print "Synchronizing done"
    
    def addRemoteFile(self, path, checksum, modified, size, isDir):
        remotefile = RemoteFile(path, checksum, modified, size, isDir)
        self.session.add(remotefile)

    def addLocalFile(self, path, checksum, modified, modified_local, size):
        localfile = LocalFile(path, checksum, modified, modified_local, size)
        self.session.add(localfile)

    def dbCommit(self):
        self.session.commit()

    def watchFileSystem(self):
        #after uploading, downloading, and synchronizing are finished, start the watcher thread
        self.localFileWatcher = Watcher(self, self.parent.smartfile, self.parent.syncDir)
        self.localFileWatcher.start()

    def compareListing(self):
        for file, properties in self.localFiles.iteritems():
            #If local file is not in the remote files dict, add upload task
            if not file in self.remoteFiles.iterkeys():
                modifiedTime = properties[0]
                fileHash = properties[1]
                task = (file, modifiedTime, fileHash)
                self.uploadQueue.put(task)
            else:
                #Otherwise, determine which way we should synchronize the file
                #...and add a task accordingly...
                remoteItem = self.remoteFiles.get(file)
                localItem = properties
                status = self.compareFile(remoteItem, localItem)
                if status is FileStatus.newerRemote:
                    self.syncDownQueue.put(file)
                elif status is FileStatus.newerLocal:
                    self.syncUpQueue.put(file)

        for file, properties in self.remoteFiles.iteritems():
             #If remote file is not in the local files dict, add download task
            if not file in self.localFiles.iterkeys():
                self.downloadQueue.put(file)
            else:
                #Otherwise, determine which way we should synchronize the file
                #...and add a task accordingly...
                remoteItem = properties
                localItem = self.localFiles.get(file)
                status = self.compareFile(remoteItem, localItem)
                if status is FileStatus.newerRemote:
                    self.syncDownQueue.put(file)
                elif status is FileStatus.newerLocal:
                    self.syncUpQueue.put(file)

    def compareFile(self, remoteItem, localItem):
        remoteHash = remoteItem[1]
        localHash = localItem[1]
        badChars = ':-. '
        if remoteItem[0] is None:
            return FileStatus.newerRemote
        remoteTime = int(str(remoteItem[0]).translate(None, badChars))
        localTime = int(str(localItem[0]).translate(None, badChars))
        if remoteHash is not localHash:
            if remoteTime > localTime:
                return FileStatus.newerRemote
            elif remoteTime < localTime:
                return FileStatus.newerLocal
            else:
                return FileStatus.doNothing

    def localFilesList(self, localPath=None):
        """
        Indexes the local files and populates the self.localFiles dictionary
        """
        if localPath is None:
            localPath = self.parent.syncDir
        for (paths, dirs, files) in os.walk(localPath):
            for item in files:
                discoveredFilePath = os.path.join(paths, item)
                checksum = self._getFileHash(diiscoveredFilePath)
                modifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(discoveredFilePath))
                size = int(os.path.getsize(discoveredFilePath))
                isDir = os.path.isdir(discoveredFilePath)
                diskLocation = discoveredFilePath.replace(localPath, '')

                self.addLocalFile(diskLocation, checksum, modifiedTime, None, size, isDir)

    def remoteFilesList(self, remotePath=None):
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
                    if path.startswith("/"):
                        path = path.replace("/", "", 1)
                    absolutePath = os.path.join(self.parent.syncDir, path)
                    common.createLocalDirs(absolutePath)
                    self.remoteFilesList(i['path'])
                else:
                    # If the path is a file
                    path = i['path'].encode("utf-8")
                    isDir = i['isdir']
                    size = int(i['size'])

                    if 'modified' in i['attributes']:
                        modifiedTime = i['attributes']['modified'].encode("utf-8").replace('T', ' ')
                    else:
                        modifiedTime = None

                    if 'checksum' in i['attributes']:
                        checksum = i['attributes']['checksum'].encode("utf-8")
                    else:
                        checksum = None

                    self.addRemoteFile(path, checksum, modifiedTime, size, isDir)

    def _getFileHash(self, filepath):
        """Returns the MD5 hash of a local file"""
        fileToHash = open(filepath)
        md5 = hashlib.md5()
        while True:
            currentLine = fileToHash.readline()
            if not currentLine:
                break
            md5.update(currentLine)
        return md5.hexdigest()


class FileStatus:
    newerRemote = 1
    newerLocal = 2
    notOnRemote = 3
    notOnLocal = 4
    doNothing = 5
