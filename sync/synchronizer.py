import datetime
import hashlib
import os
from Queue import Queue


class Synchronizer(object):
    def __init__(self, parent=None):
        object.__init__(self)
        self.parent = parent

        self.localFiles = {}
        self.remoteFiles = {}
        self.taskQueue = Queue()

    def start(self):
        self.localFilesList()
        self.remoteFilesList()
        for key, value in self.localFiles.iteritems():
            print key
        for key, value in self.remoteFiles.iteritems():
            print key

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
                size = os.path.getsize(discoveredFilePath)
                self.localFiles[discoveredFilePath.replace(localPath, '')] = modifiedTime, fileHash, size

    def remoteFilesList(self, remotePath=None):
        '''
        Recursively indexes the remote directory since we cannot see the directories all at once
        '''
        if remotePath is None:
            remotePath = "/"
        apiPath = '/path/info%s' % remotePath
        dirListing = self.parent.smartfile.get(apiPath, children=True)
        for i in dirListing['children']:
            if(i['isdir']):
                self.remoteFilesList(i['path'])
            else:
                path = i['path'].encode("utf-8")
                size = int(i['size'])
                permissions = i['acl']
                if 'kissyncmodified' in i['attributes']:
                    modifiedTime = i['attributes']['kissyncmodified'].encode("utf-8")
                else:
                    modifiedTime = None
                if 'md5' in i['attributes']:
                    fileHash = i['attributes']['md5'].encode("utf-8")
                else:
                    fileHash = None
                self.remoteFiles[path] = modifiedTime, fileHash, size, permissions

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
