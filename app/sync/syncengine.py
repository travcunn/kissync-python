from collections import namedtuple
import datetime
import os
import threading
import time
from Queue import LifoQueue

from definitions import FileDefinition, LocalDefinitionHelper
from download import DownloadThread
from errors import BadEventException
import events
from realtime import RealtimeMessages
from upload import UploadThread
from watcher import Watcher


class SyncThread(threading.Thread):
    def __init__(self, api, sync_dir):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.api = api
        self.sync_dir = sync_dir

    def run(self):
        self.sync_engine = SyncEngine(self.api, self.sync_dir)

        # Start the workers to wait for tasks
        self.sync_engine.startWorkers()

        # Watch the file system
        self.local_watcher = Watcher(sync_dir=self.sync_dir,
                moved_callback=self.sync_engine.movedEvent,
                created_callback=self.sync_engine.createdEvent,
                deleted_callback=self.sync_engine.deletedEvent,
                modified_callback=self.sync_engine.modifiedEvent)
        self.local_watcher.start()

        # Start the realtime engine
        self.realtime = RealtimeMessages(self.sync_engine)
        self.realtime.start()
        # Synchronize with SmartFile
        self.sync_engine.synchronize()


class SyncEngine(object):
    """
    Handles file synchronization, including local and remote filesystem
    events, transfer queues, and conflict resolution.
    """
    def __init__(self, api, sync_dir):
        self.api = api
        self.sync_dir = sync_dir

        # Simple task queue
        self.simpleTasks = LifoQueue()
        # Upload task queue
        self.uploadQueue = LifoQueue()
        # Download task queue
        self.downloadQueue = LifoQueue()

    def startWorkers(self):
        """ Initialize the upload and download workers. """

        upload = 4  # Specify amount of upload threads
        download = 5  # Specify amount of download threads

        self.uploadWorkers = []
        for i in range(upload):
            uploader = UploadThread(self.uploadQueue, self.api,
                                    self.sync_dir)
            uploader.start()
            self.uploadWorkers.append(uploader)

        self.downloadWorkers = []
        for i in range(download):
            downloader = DownloadThread(self.downloadQueue, self.api,
                                        self.sync_dir)
            downloader.start()
            self.downloadWorkers.append(downloader)

    def synchronize(self):
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
            self.compare_results(remote=remote_files, local=local_files)

            # Wait 5 minutes, then check with SmartFile again
            time.sleep(wait_time * 60)

    def compare_results(self, remote, local):
        """ Compare the local and remote file lists. """
        matching_files = []

        # Used for pairs of files that need compared
        FileMatch = namedtuple('FileMatch', ['local', 'remote'])

        for local_file in local:
            match_found = False
            matching_file = None
            for remoteObject in remote:
                if local_file.path == remoteObject.path:
                    match_found = True
                    matching_file = remoteObject
            if match_found:
                match = FileMatch(local_file, matching_file)
                matching_files.append(match)
            else:
                self.uploadQueue.put(local_file)
            match_found = False
            matching_file = None

        # Check which remote SmartFile files dont exist locally
        for remote_file in remote:
            found_on_local = False
            for localObject in local:
                if remote_file.path == localObject.path:
                    found_on_local = True
            if not found_on_local:
                self.downloadQueue.put(remote_file)
            found_on_local = False

        # Check which way to synchronize files
        for item in matching_files:
            if item.local.checksum != item.remote.checksum:
                if item.local.modified > item.remote.modified:
                    self.uploadQueue.put(item.local)
                elif item.local.modified < item.remote.modified:
                    self.downloadQueue.put(item.remote)

        # Clear the array
        matching_files = []

    def movedEvent(self, event):
        if (isinstance(event, events.LocalMovedEvent) or
                isinstance(event, events.RemoteMovedEvent)):
            moved_tasks = []
            for task in self.simpleTasks.queue:
                # if the task is not a move task
                if not (isinstance(task, events.LocalMovedEvent) or
                        isinstance(task, events.RemoteMovedEvent)):
                    if task.path == event.src:
                        moved_task = task
                        moved_task.path = event.path
                        moved_tasks.append(moved_task)
                        self.simpleTasks.queue.remove(task)
                else:
                    # if the task is a move task, get rid of tasks that move
                    # the same file
                    if task.src == event.src:
                        self.simpleTasks.queue.remove(task)
            # tasks that were moved should be put back into the queue
            for task in moved_tasks:
                self.simpleTasks.put(task)
            # Put the task in the queue
            self.simpleTasks.put(event)
        else:
            raise BadEventException("Not a valid event: ",
                    event.__class__.__name__)

    def createdEvent(self, event):
        if isinstance(event, events.LocalCreatedEvent):
            # Check the upload queue for redundant events
            for task in self.uploadQueue.queue:
                if task.path == event.path:
                    self.uploadQueue.queue.remove(task)
            # Put the task in the queue
            self.uploadQueue.put(event)
        elif isinstance(event, events.RemoteCreatedEvent):
            # Check the download queue for redundant events
            for task in self.downloadQueue.queue:
                if task.path == event.path:
                    self.downloadQueue.queue.remove(task)
            # Put the task in the queue
            self.downloadQueue.put(event)
        else:
            raise BadEventException("Not a valid event: ",
                    event.__class__.__name__)

    def deletedEvent(self, event):
        if (isinstance(event, events.LocalDeletedEvent) or
                isinstance(event, events.RemoteDeletedEvent)):
            # Cancel any task in the simpleTasks queues since it was deleted
            for task in self.simpleTasks.queue:
                if task.path == event.path:
                    self.simpleTasks.queue.remove(task)
            # The file wont need to be downloaded since it was deleted
            for task in self.downloadQueue.queue:
                if task.path == event.path:
                    self.downloadQueue.queue.remove(task)
            # The file wont need to be uploaded since it was deleted
            for task in self.uploadQueue.queue:
                if task.path == event.path:
                    self.uploadQueue.queue.remove(task)

            # Cancel any upload task on the event path
            self.cancelUploadTask(event.path)
            # Cancel any download task on the event path
            self.cancelDownloadTask(event.path)

            # Put the task in the queue
            self.simpleTasks.put(event)
        else:
            raise BadEventException("Not a valid event: ",
                    event.__class__.__name__)

    def modifiedEvent(self, event):
        if isinstance(event, events.LocalModifiedEvent):
            # Check the upload queue for redundant events
            for task in self.uploadQueue.queue:
                if task.path == event.path:
                    self.uploadQueue.queue.remove(task)
            # Put the task in the queue
            self.uploadQueue.put(event)
        elif isinstance(event, events.RemoteModifiedEvent):
            # Check the download queue for redundant events
            for task in self.downloadQueue.queue:
                if task.path == event.path:
                    self.downloadQueue.queue.remove(task)
            # Put the task in the queue
            self.downloadQueue.put(event)
        else:
            raise BadEventException("Not a valid event: ",
                    event.__class__.__name__)

    def cancelUploadTask(self, path):
        """ Cancels an upload task given a file path. """
        for worker in self.uploadWorkers:
            if worker.current_task.path == path:
                worker.cancel()

    def cancelDownloadTask(self, path):
        """ Cancels a download task given a file path. """
        for worker in self.downloadWorkers:
            if worker.current_task.path == path:
                worker.cancel()


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
            isValid = True
            filename = os.path.basename(path)
            for _filter in filters:
                if callable(_filter):
                    if not _filter(filename):
                        # Make the discovered file invalid
                        isValid = False
            if isValid:
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
