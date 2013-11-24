import datetime
import os
import threading
import time
from Queue import LifoQueue

from definitions import FileDefinition, LocalDefinitionHelper
from download import DownloadThread
from errors import BadEventException
import events
from realtime import RealtimeSync
from upload import UploadThread
from watcher import Watcher


class SyncThread(threading.Thread):  # pragma: no cover
    def __init__(self, api):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.api = api

    def run(self):
        self.syncEngine = SyncEngine(self.api)

        # Start the transfer threads to wait for tasks
        self.syncEngine.startTransferThreads()

        # Watch the file system
        self.localWatcher = Watcher(self.syncEngine, self.syncEngine.api,
                                    self.syncEngine.syncDir)
        self.localWatcher.start()

        # Start the realtime engine
        self.realtime = RealtimeSync(self.syncEngine)
        self.realtime.start()
        # Synchronize with SmartFile
        self.syncEngine.synchronize()


class SyncEngine(object):
    """
    Handles file synchronization, including local and remote filesystem
    events, transfer queues, and conflict resolution.
    """
    def __init__(self, api):
        self.api = api

        # Simple task queue
        self.simpleTasks = LifoQueue()
        # Upload task queue
        self.uploadQueue = LifoQueue()
        # Download task queue
        self.downloadQueue = LifoQueue()

    def startTransferThreads(self):  # pragma: no cover
        """ Initialize the upload and download threads. """

        upload = 4  # Specify amount of upload threads
        download = 5  # Specify amount of download threads

        self.uploadThreads = []
        for i in range(upload):
            uploader = UploadThread(self.uploadQueue, self.api,
                                    self.syncDir, self)
            uploader.start()
            self.uploadThreads.append(uploader)

        self.downloadThreads = []
        for i in range(download):
            downloader = DownloadThread(self.downloadQueue, self.api,
                                        self.syncDir)
            downloader.start()
            self.downloadThreads.append(downloader)

    def synchronize(self):  # pragma: no cover
        """ Compare local files with the SmartFile servers. """
        # Wait time in between indexing remote
        wait_time = 5
        while True:
            # Index remote files
            remoteIndexer = RemoteIndexer(self.api)
            remote_files = remoteIndexer.collected_files

            # Index local files
            localIndexer = LocalIndexer(self.syncFS)
            local_files = localIndexer.collected_files

            # Compare the lists and populate task queues
            self.compare(remote=remote_files, local=local_files)

            # Wait 5 minutes, then check with SmartFile again
            time.sleep(wait_time * 60)

    def compare(self, remote, local):
        """ Compare the local and remote file lists. """
        objectsOnBoth = []

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

        # Check which remote SmartFile files dont exist locally
        for remoteObject in remote:
            found = False
            for localObject in local:
                if remoteObject.path == localObject.path:
                    found = True
            if not found:
                self.downloadQueue.put(remoteObject)
            found = False

        # Check which way to synchronize files
        for item in objectsOnBoth:
            localObject = item[0]
            remoteObject = item[1]
            if localObject.checksum != remoteObject.checksum:
                if localObject.modified_local > remoteObject.modified:
                    self.uploadQueue.put(localObject)
                elif localObject.modified_local < remoteObject.modified:
                    self.downloadQueue.put(remoteObject)

        # Clear the array
        objectsOnBoth = []

    def addEvent(self, event):
        #TODO: use a dictionary here
        """ Add a single event to the appropriate queue. """
        if (isinstance(event, events.FileMovedEvent) or
          isinstance(event, events.RemoteMovedEvent)):
            self.simpleTasks.put(event)
        elif isinstance(event, events.FileCreatedEvent):
            self.uploadQueue.put(event)
        elif isinstance(event, events.RemoteCreatedEvent):
            self.downloadQueue.put(event)
        elif (isinstance(event, events.FileDeletedEvent) or
          isinstance(event, events.RemoteDeletedEvent)):
            self.simpleTasks.put(event)
        elif isinstance(event, events.FileModifiedEvent):
            self.uploadQueue.put(event)
        elif isinstance(event, events.RemoteModifiedEvent):
            self.downloadQueue.put(event)
        else:
            raise BadEventException("Not a valid event: ", event.__name__)

    def _checkRedundantEvents(self, event):
        #TODO: write this method
        """ Check for r)dundant events in the various queues. """
        pass


class Indexer(object):
    """
    Indexer objects inherit this object to build an array of indexed files.
    Later, we can use this to get directory listings for P2P.
    """
    def __init__(self):
        self.results = []
        self.index()

    def collect(self, file_object):
        """ Collect each file definition. """
        self.results.append(file_object)

    def index(self):
        """ Override this function to perform indexing. """
        raise NotImplementedError


class LocalIndexer(Indexer):
    """ Index the local filesystem. """
    def __init__(self, syncFS):
        self.syncFS = syncFS
        Indexer.__init__(self)

    def index(self):
        _default_startswith_filter = lambda x: not x.startswith(".")
        _default_endswith_filter = lambda x: not x.endswith("~")
        filters = [_default_startswith_filter, _default_endswith_filter]

        for path in self.syncFS.walkfiles():
            filename = os.path.basename(path)
            # Do some filtering
            for _filter in filters:
                if callable(_filter):
                    if not _filter(filename):
                        continue
            # Create a file definition and generate some properties
            helper = LocalDefinitionHelper(path, self.syncFS)
            local_file = helper.create_definition()
            # Collect the local file in the indexer
            self.collect(local_file)


class RemoteIndexer(Indexer):
    """
    Index the files on SmartFile and dive into directories when necessary.
    """
    def __init__(self, api):
        self.api = api
        Indexer.__init__(self)

    def index(self, remotePath=None):
        filesIndexed = False
        while not filesIndexed:
            if remotePath is None:
                remotePath = "/"
            apiPath = '/path/info%s' % remotePath

            #TODO: check other errors here later
            dir_listing = self.api.get(apiPath, children=True)

            if "children" not in dir_listing:
                break
            for json_data in dir_listing['children']:
                path = json_data['path']
                isDir = json_data['isfile']
                # Check if modified is in attributes and use that
                if "modified" in json_data['attributes']:
                    modifiedstr = json_data['attributes']['modified']
                    modified = datetime.datetime.strptime(modifiedstr,
                                                        '%Y-%m-%d %H:%M:%S')
                # Or else, just use the modified time set by the api
                else:
                    modifiedstr = json_data['time']
                    modified = datetime.datetime.strptime(modifiedstr,
                                                          '%Y-%m-%dT%H:%M:%S')
                if not isDir:
                    checksum = None
                    size = None
                else:
                    if 'checksum' in json_data['attributes']:
                        checksum = json_data['attributes']['checksum']
                    else:
                        checksum = None
                    size = int(json_data['size'])

                # Add the folder to the list of files
                remotefile = FileDefinition(path, checksum, modified, size,
                                            isDir)

                # Collect the remote file in the indexer
                self.collect(remotefile)

                # If the file is a directory, dive in and look for more
                if isDir:
                    self.index(json_data['path'])
            filesIndexed = True
