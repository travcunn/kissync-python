import datetime
import hashlib
import os
import threading
from Queue import Queue

from downloader import Downloader
from uploader import Uploader
from watcher import Watcher


class Synchronizer(threading.Thread):
    def __init__(self, parent=None):
        threading.Thread.__init__(self)
        self.parent = parent

        self.localFiles = {}
        self.remoteFiles = {}

        self.uploadQueue = Queue()
        self.downloadQueue = Queue()
        self.syncUpQueue = Queue()
        self.syncDownQueue = Queue()

        self.uploader = Uploader(self.uploadQueue, self.parent.smartfile, self.parent.syncDir)
        self.downloader = Downloader(self.downloadQueue, self.parent.smartfile, self.parent.syncDir)

        self.setDaemon(True)

    def run(self):
        #Initially, get the local and remote file listing
        self.localFilesList()
        self.remoteFilesList()
        #Now compare the lists and populate task queues for differences
        self.compareListing()

        self.uploader.start()
        self.downloader.start()
        #Wait for the uploading and downloading tasks to finish
        self.uploadQueue.join()
        self.downloadQueue.join()

        #after uploading, downloading, and synchronizing are finished, start the watcher thread
        self.localFileWatcher = Watcher(self)
        self.localFileWatcher.start()

    def compareListing(self):
        for file, properties in self.localFiles.iteritems():
            #If local file is not in the remote files dict, add upload task
            if not file in self.remoteFiles.iterkeys():
                self.uploadQueue.put(file)
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
        badChars = ':- '
        remoteTime = int(str(remoteItem[0]).translate(None, badChars))
        localTime = int(str(localItem[0]).translate(None, badChars))
        if remoteHash is not localHash:
            if remoteTime > localTime:
                return FileStatus.newerRemote
            elif remoteItem.date() > localItem.date():
                return FileStatus.newerLocal
            else:
                return FileStatus.doNothing

    def localFilesList(self, localPath=None):
        '''
        Indexes the local files and populates the self.localFiles dictionary
        '''
        if localPath is None:
            localPath = self.parent.syncDir
        for (paths, dirs, files) in os.walk(localPath):
            for item in files:
                discoveredFilePath = os.path.join(paths, item)
                fileHash = self._getFileHash(discoveredFilePath)
                modifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(discoveredFilePath))
                size = int(os.path.getsize(discoveredFilePath))
                isDir = os.path.isdir(discoveredFilePath)
                self.localFiles[discoveredFilePath.replace(localPath, '')] = modifiedTime, fileHash, isDir, size

    def remoteFilesList(self, remotePath=None):
        '''
        Recursively indexes the remote directory since we cannot see the directories all at once
        '''
        if remotePath is None:
            remotePath = "/"
        apiPath = '/path/info%s' % remotePath
        dirListing = self.parent.smartfile.get(apiPath, children=True)
        if "children" in dirListing:
            for i in dirListing['children']:
                path = i['path'].encode("utf-8")
                isDir = i['isdir']
                size = int(i['size'])
                permissions = i['acl']
                if 'modified' in i['attributes']:
                    modifiedTime = i['attributes']['modified'].encode("utf-8").replace('T', ' ')
                else:
                    modifiedTime = None
                if 'md5' in i['attributes']:
                    fileHash = i['attributes']['md5'].encode("utf-8")
                else:
                    fileHash = None
                self.remoteFiles[path] = modifiedTime, fileHash, isDir, size, permissions
                if(i['isdir']):
                    self.remoteFilesList(i['path'])

    def _getFileHash(self, filepath):
        '''
        Returns the MD5 hash of a local file
        '''
        fileToHash = open(filepath)
        md5 = hashlib.md5()
        while(True):
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
