import datetime
import logging
import os
import threading
import time
from Queue import LifoQueue

from fs.osfs import OSFS
import fs.path
from smartfile.errors import RequestError, ResponseError

from definitions import FileDefinition, LocalDefinitionHelper
from download import DownloadThread
from errors import BadEventException
import events
#from realtime import RealtimeMessages
from upload import UploadThread
from watcher import Watcher


log = logging.getLogger(__name__)


class SyncThread(threading.Thread):
    def __init__(self, api, sync_dir):
        self.api = api
        self.sync_dir = sync_dir

        super(SyncThread, self).__init__()
        self.setDaemon(True)

    def run(self):
        self.sync_engine = SyncEngine(self.api, self.sync_dir)

        # Watch the local file system
        self.local_watcher = Watcher(
                processing=self.sync_engine.isDownloading,
                sync_dir=self.sync_dir,
                moved_callback=self.sync_engine.movedEvent,
                created_callback=self.sync_engine.createdEvent,
                deleted_callback=self.sync_engine.deletedEvent,
                modified_callback=self.sync_engine.modifiedEvent)
        self.local_watcher.start()

        """
        # Start the realtime messaging system
        self.realtime = RealtimeMessages(api=self.api,
                on_moved=self.sync_engine.movedEvent,
                on_created=self.sync_engine.createdEvent,
                on_deleted=self.sync_engine.deletedEvent,
                on_modified=self.sync_engine.modifiedEvent)
        self.realtime.start()

        # Setup messaging for the sync engine
        self.sync_engine.setupMessaging(self.realtime)
        """

        # Start the sync engine
        self.sync_engine.start()


class SyncEngine(object):
    """
    Handles file synchronization, including local and remote filesystem
    events, transfer queues, and conflict resolution.
    """
    def __init__(self, api, sync_dir):
        self.api = api
        self.sync_dir = sync_dir
        self.syncFS = OSFS(sync_dir)

        self.realtime = False

        self.uploadWorkers = []
        self.downloadWorkers = []

        self.local_files = {}
        self.remote_files = {}

        # Simple task queue
        self.simpleTasks = LifoQueue()
        # Upload task queue
        self.uploadQueue = LifoQueue()
        # Download task queue
        self.downloadQueue = LifoQueue()

    def setupMessaging(self, realtime):
        """ For some tasks, messages should be sent to other clients. """
        self.realtime = realtime

    def start(self):
        """ Initialize the upload and download workers. """

        upload = 4  # Specify amount of upload threads
        download = 5  # Specify amount of download threads

        log.debug("Creating " + str(upload) + " upload workers.")
        for i in range(upload):
            uploader = UploadThread(self.uploadQueue, self.api,
                                    self.sync_dir, self.remote_files,
                                    self.realtime)
            uploader.start()
            self.uploadWorkers.append(uploader)

        log.debug("Creating " + str(download) + " download workers.")
        for i in range(download):
            downloader = DownloadThread(self.downloadQueue, self.api,
                                        self.sync_dir, self.local_files)
            downloader.start()
            self.downloadWorkers.append(downloader)

        # Synchronize with SmartFile
        self.synchronize()

    def synchronize(self):
        """ Compare local files with the SmartFile servers. """
        # Wait time in between indexing remote
        wait_time = 5

        remote_indexer = RemoteIndexer(self.api)
        local_indexer = LocalIndexer(self.syncFS)
        while True:
            # Index remote files
            log.debug("Indexing the files on SmartFile.")
            remote_indexer.results.clear()
            remote_indexer.index()

            # Index local files
            log.debug("Indexing the files on the local system.")
            local_indexer.results.clear()
            local_indexer.index()

            # WARNING: this takes a lot of requests
            # Set the local and remote file dictionaries
            self.local_files = local_indexer.results
            self.remote_files = remote_indexer.results

            # Compare the lists and populate task queues
            log.debug("Comparing the results of remote and local.")
            self.compare_results(remote=remote_indexer.results,
                                 local=local_indexer.results)

            # Wait 5 minutes, then check with SmartFile again
            log.debug("Synchronize sleep for " + str(wait_time * 60))
            time.sleep(wait_time * 60)

    def compare_results(self, remote, local):
        """ Compare the local and remote file dictionaries. """
        #TODO: make sure tasks are not already in the queues.
        #TODO: Dont put a task in the queue if it is already in it

        remote_files = set(remote.keys())
        local_files = set(local.keys())

        matching_files = list(remote_files.intersection(local_files))
        remote_only_files = list(remote_files - local_files)
        local_only_files = list(local_files - remote_files)

        # For files that exist in both locations, a creation event is created 
        # depending on which file definition is newer
        for match in matching_files:
            if local[match].checksum != remote[match].checksum:
                if local[match].modified > remote[match].modified:
                    event = events.LocalCreatedEvent(local[match].path,
                                                     local[match].isDir)
                    self.createdEvent(event)
                elif local[match].modified < remote[match].modified:
                    event = events.RemoteCreatedEvent(local[match].path,
                                                      local[match].isDir)
                    self.createdEvent(event)

        # Put remote only files into the download queue
        for remote_file in remote_only_files:
            event = events.RemoteCreatedEvent(remote[remote_file].path,
                                              remote[remote_file].isDir)
            self.createdEvent(event)

        # Put local only files into the upload queue
        for local_file in local_only_files:
            event = events.LocalCreatedEvent(local[local_file].path,
                                             local[local_file].isDir)
            self.createdEvent(event)

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
                    break
            else:
                if not self.isUploading(event.path):
                    # Put the task in the queue
                    log.info("Putting a task into the upload queue.")
                    self.uploadQueue.put(event)
        elif isinstance(event, events.RemoteCreatedEvent):
            # Check the download queue for redundant events
            for task in self.downloadQueue.queue:
                if task.path == event.path:
                    break
            else:
                if not self.isDownloading(event.path):
                    # Put the task in the queue
                    log.info("Putting a task into the download queue.")
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
                    break
            else:
                if not self.isUploading(event.path):
                    # Put the task in the queue
                    self.uploadQueue.put(event)
        elif isinstance(event, events.RemoteModifiedEvent):
            # Check the download queue for redundant events
            for task in self.downloadQueue.queue:
                if task.path == event.path:
                    break
            else:
                if not self.isDownloading(event.path):
                    # Put the task in the queue
                    self.downloadQueue.put(event)
        else:
            raise BadEventException("Not a valid event: ",
                    event.__class__.__name__)

    def cancelUploadTask(self, path):
        """ Cancels an upload task given a file path. """
        for worker in self.uploadWorkers:
            if worker.current_task is not None:
                if worker.current_task.path == path:
                    worker.cancel()

    def cancelDownloadTask(self, path):
        """ Cancels a download task given a file path. """
        for worker in self.downloadWorkers:
            if worker.current_task is not None:
                if worker.current_task.path == path:
                    worker.cancel()

    def isDownloading(self, path):
        """ Returns whether or not a file is being downloaded. """
        for worker in self.downloadWorkers:
            if worker.current_task is not None:
                if worker.current_task.path == path:
                    return True
        else:
            return False

    def isUploading(self, path):
        """ Returns whether or not a file is being uploaded. """
        for worker in self.uploadWorkers:
            if worker.current_task is not None:
                if worker.current_task.path == path:
                    return True
        else:
            return False


class LocalIndexer(object):
    """
    Index the local filesystem.
    Read the results from LocalIndex.results.
    """
    def __init__(self, syncFS, *args):
        self.syncFS = syncFS
        self.results = {}

    def index(self):
        for dir, path in self.syncFS.walk('/'):
            self._process_path(dir)
            for name in path:
                discovered_path = fs.path.join(dir, name)
                self._process_path(discovered_path)

    def _process_path(self, path):
        #startswith_filter = lambda x: not x.startswith(".")
        #endswith_filter = lambda x: not x.endswith("~")
        filters = [(lambda x: not x.startswith(".")),
                   (lambda x: not x.endswith("~")),
                   (lambda x: not x == '/')]

        filename = os.path.basename(path)
        for _filter in filters:
            if callable(_filter):
                # Filter the file name
                if not _filter(filename) or not _filter(path):
                    # The discovered file is invalid
                    break
        else:
            # The discovered file is valid
            # Create a file definition and generate some properties
            helper = LocalDefinitionHelper(path, self.syncFS)
            local_file = helper.create_definition()

            # Collect the local file in the indexer
            self.results[local_file.path] = local_file


class RemoteIndexer(object):
    """
    Index the files on SmartFile and dive into directories when necessary.
    Read the results from RemoteIndexer.results
    """
    def __init__(self, api):
        self.api = api
        self.results = {}

    def index(self, remotePath=None):
        filesIndexed = False
        while not filesIndexed:
            if remotePath is None:
                remotePath = "/"
            apiPath = '/path/info%s' % remotePath

            #TODO: check other errors here later
            try:
                dir_listing = self.api.get(apiPath, children=True)
            except ResponseError as e:
                # If the error code is 404, ignore the file.
                if e.status_code == 404:
                    dir_listing = []
            except RequestError, err:
                if err.detail.startswith('HTTPConnectionPool'):
                    # Connection error. Wait 2 seconds then try again.
                    time.sleep(2)
                    dir_listing = self.api.get(apiPath, children=True)

            if "children" not in dir_listing:
                break
            for json_data in dir_listing['children']:
                path = json_data['path']
                isDir = not json_data['isfile']
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
                remote_file = FileDefinition(path, checksum, modified, size,
                                             isDir)

                # Collect the remote file in the indexer
                self.results[remote_file.path] = remote_file

                # If the file is a directory, dive in and look for more
                if isDir:
                    self.index(json_data['path'])
            filesIndexed = True
