import datetime
import os
import threading
import time
from Queue import LifoQueue

from download import DownloadThread
from upload import UploadThread
from watcher import Watcher

from fs.osfs import OSFS

from definitions import File

import common


class SyncObject(object):
    """ Inherit this for any object that performs synchronization """
    def __init__(self):
        self._timeOffset = common.calculate_time_offset()
        self._syncDir = os.path.join(os.path.expanduser("~"), "Smartfile")

    @property
    def syncDir(self):
        """ Get the sync directory """
        return self._syncDir

    @property
    def timeOffset(self):
        """ Get the time offset to use in time calculations """
        return self._timeOffset


class SyncThread(threading.Thread):
    def __init__(self, api):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.api = api

    def run(self):
        self.syncEngine = SyncEngine(self.api)

        # Start the transfer threads to wait for tasks
        self.syncEngine.startTransferThreads()
        # Watch the file system
        self.syncEngine.watchFileSystem()
        # Synchronize with SmartFile
        self.syncEngine.synchronize()


class SyncEngine(SyncObject):
    def __init__(self, api):
        SyncObject.__init__(self)

        self.api = api

        # Setup arrays for local and remote file comparison
        self.localFiles = []
        self.remoteFiles = []

        # Setup queues for tasks
        self.uploadQueue = LifoQueue()
        self.downloadQueue = LifoQueue()

        # Queue for events to send to the realtime sync server
        self.changesQueue = LifoQueue()

        # List of files that the watcher should ignore
        self.ignoreFiles = []

        self.watcherRunning = False

    def startTransferThreads(self):
        # Initialize the upload and download threads

        upload = 4  # Specify amount of upload threads
        download = 5  # Specify amount of download threads

        self.uploadThreads = []
        for i in range(upload):
            uploader = UploadThread(self.uploadQueue, self.api, self.syncDir, self)
            uploader.start()
            self.uploadThreads.append(uploader)

        self.downloadThreads = []
        for i in range(download):
            downloader = DownloadThread(self.downloadQueue, self.api, self.syncDir)
            downloader.start()
            self.downloadThreads.append(downloader)

    def synchronize(self):
        while True:
            # Index the remote files and store in DB
            self.indexRemote()
            # Index the local files and store in DB
            self.indexLocal()
            # Now compare the tables and populate task queues
            self.compare()

            # Wait 5 minutes, then check with SmartFile again
            wait_time = 5
            time.sleep(wait_time * 60)

    def addRemoteFile(self, path, checksum, modified, size, isDir):
        remotefile = File(path, checksum, modified, size, isDir)
        self.remoteFiles.append(remotefile)

    def addLocalFile(self, path, checksum, modified, size, isDir):
        localfile = File(path, checksum, modified, size, isDir)
        self.localFiles.append(localfile)

    def watchFileSystem(self):
        self.localWatcher = Watcher(self, self.api, self.syncDir)
        self.localWatcher.start()
        self.watcherRunning = True

    def compare(self):
        local = self.localFiles
        remote = self.remoteFiles

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
                ignorePath = os.path.join(self.syncDir, remoteObject.path)
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
                    ignorePath = os.path.join(self.syncDir, remoteObject.path)
                    self.ignoreFiles.append(ignorePath)
                    self.downloadQueue.put(remoteObject)

        # Clear objects on both
        objectsOnBoth = None

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
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(systemPath)).replace(microsecond=0) - self.timeOffset
            size = syncFS.getsize(path)
            isDir = syncFS.isdir(path)

            if not path.endswith("~"):
                # Add the file to the database
                self.addLocalFile(path, checksum, modified, size, isDir)

    def indexRemote(self, remotePath=None):
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
