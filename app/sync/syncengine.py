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
from download import DownloadWorker
from errors import BadEventError
import events
from realtime import RealtimeMessages
from simpletasks import SimpleTaskWorker
from upload import UploadWorker
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
            processing=self.sync_engine.is_downloading,
            sync_dir=self.sync_dir,
            moved_callback=self.sync_engine.moved_event,
            created_callback=self.sync_engine.created_event,
            deleted_callback=self.sync_engine.deleted_event,
            modified_callback=self.sync_engine.modified_event)
        self.local_watcher.start()

        # Start the realtime messaging system
        self.realtime = RealtimeMessages(api=self.api,
                on_moved=self.sync_engine.moved_event,
                on_created=self.sync_engine.created_event,
                on_deleted=self.sync_engine.deleted_event,
                on_modified=self.sync_engine.modified_event)
        self.realtime.start()

        # Setup messaging for the sync engine
        self.sync_engine.setup_messaging(self.realtime)

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
        self.sync_fs = OSFS(sync_dir)

        self.realtime = False

        self.simple_task_workers = []
        self.upload_workers = []
        self.download_workers = []

        self.local_files = {}
        self.remote_files = {}

        # Simple task queue
        self.simple_tasks = LifoQueue()
        # Upload task queue
        self.upload_queue = LifoQueue()
        # Download task queue
        self.download_queue = LifoQueue()

    def setup_messaging(self, realtime):
        """ For some tasks, messages should be sent to other clients. """
        self.realtime = realtime

    def start(self):
        """ Initialize the workers. """

        simple = 2  # Specify amount of simple workers
        upload = 2  # Specify amount of upload workers
        download = 2  # Specify amount of download workers

        log.debug("Creating " + str(upload) + " simple task workers.")
        for i in range(upload):
            simple = SimpleTaskWorker(self.simple_tasks, self.api,
                                    self.sync_dir, self.remote_files,
                                    self.realtime)
            simple.start()
            self.simple_task_workers.append(simple)

        log.debug("Creating " + str(upload) + " upload workers.")
        for i in range(upload):
            uploader = UploadWorker(self.upload_queue, self.api,
                                    self.sync_dir, self.remote_files,
                                    self.realtime)
            uploader.start()
            self.upload_workers.append(uploader)

        log.debug("Creating " + str(download) + " download workers.")
        for i in range(download):
            downloader = DownloadWorker(self.download_queue, self.api,
                                        self.sync_dir, self.local_files)
            downloader.start()
            self.download_workers.append(downloader)

        # Synchronize with SmartFile
        self.synchronize()

    def synchronize(self):
        """ Compare local files with the SmartFile servers. """
        remote_indexer = RemoteIndexer(self.api)
        local_indexer = LocalIndexer(self.sync_fs)

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

    def compare_results(self, remote, local):
        """ Compare the local and remote file dictionaries. """
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
                                                     local[match].is_dir)
                    self.created_event(event)
                elif local[match].modified < remote[match].modified:
                    event = events.RemoteCreatedEvent(local[match].path,
                                                      local[match].is_dir)
                    self.created_event(event)

        # Put remote only files into the download queue
        for remote_file in remote_only_files:
            event = events.RemoteCreatedEvent(remote[remote_file].path,
                                              remote[remote_file].is_dir)
            self.created_event(event)

        # Put local only files into the upload queue
        for local_file in local_only_files:
            event = events.LocalCreatedEvent(local[local_file].path,
                                             local[local_file].is_dir)
            self.created_event(event)

    def moved_event(self, event):
        if (isinstance(event, events.LocalMovedEvent) or
                isinstance(event, events.RemoteMovedEvent)):

            moved_tasks = []
            for task in self.simple_tasks.queue:
                # if the task is not a move task
                if not (isinstance(task, events.LocalMovedEvent) or
                        isinstance(task, events.RemoteMovedEvent)):
                    if task.path == event.src:
                        moved_task = task
                        moved_task.path = event.path
                        moved_tasks.append(moved_task)
                        self.simple_tasks.queue.remove(task)
                else:
                    # if the task is a move task, get rid of tasks that move
                    # the same file
                    if task.src == event.src:
                        self.simple_tasks.queue.remove(task)
            # tasks that were moved should be put back into the queue
            for task in moved_tasks:
                self.simple_tasks.put(task)
            # Put the task in the simple tasks queue
            self.simple_tasks.put(event)

            # Move any files being currently uploaded
            moved_upload_tasks = []
            for worker in self.upload_workers:
                if worker.current_task is not None:
                    if worker.current_task.path == event.src:
                        moved_upload_tasks.append(worker.current_task)
                        worker.cancel()
            # Put moved upload tasks back into the upload queue
            for task in moved_upload_tasks:
                task.path = event.path
                self.upload_queue.put(task)

            # Move any files being currently downloaded
            moved_download_tasks = []
            for worker in self.download_workers:
                if worker.current_task is not None:
                    if worker.current_task.path == event.src:
                        moved_download_tasks.append(worker.current_task)
                        worker.cancel()
            # Put moved download tasks back into the download queue
            for task in moved_download_tasks:
                task.path = event.path
                self.download_queue.put(task)

            # Move any file paths in the queues
            moved_upload_queue_tasks = []
            for task in self.upload_queue.queue:
                if task.path == event.src:
                    moved_upload_queue_tasks.append(task)
                    self.upload_queue.queue.remove(task)
            moved_download_queue_tasks = []
            for task in self.download_queue.queue:
                if task.path == event.src:
                    moved_download_queue_tasks.append(task)
                    self.download_queue.queue.remove(task)
            # Put moved download tasks back into the download queue
            for task in moved_download_queue_tasks:
                task.path = event.path
                self.download_queue.put(task)
            # Put moved upload tasks back into the upload queue
            for task in moved_upload_queue_tasks:
                task.path = event.path
                self.upload_queue.put(task)
        else:
            raise BadEventError("Not a valid event: ",
                    event.__class__.__name__)

    def created_event(self, event):
        if isinstance(event, events.LocalCreatedEvent):
            # Check the upload queue for redundant events
            for task in self.upload_queue.queue:
                if task.path == event.path:
                    break
            else:
                if not self.is_uploading(event.path):
                    # Put the task in the queue
                    log.info("Putting a task into the upload queue.")
                    self.upload_queue.put(event)
        elif isinstance(event, events.RemoteCreatedEvent):
            # Check the download queue for redundant events
            for task in self.download_queue.queue:
                if task.path == event.path:
                    break
            else:
                if not self.is_downloading(event.path):
                    # Put the task in the queue
                    log.info("Putting a task into the download queue.")
                    self.download_queue.put(event)
        else:
            raise BadEventError("Not a valid event: ",
                    event.__class__.__name__)

    def deleted_event(self, event):
        if (isinstance(event, events.LocalDeletedEvent) or
                isinstance(event, events.RemoteDeletedEvent)):
            # Cancel any task in the simpleTasks queues since it was deleted
            for task in self.simple_tasks.queue:
                if task.path == event.path:
                    self.simple_tasks.queue.remove(task)
            # The file wont need to be downloaded since it was deleted
            for task in self.download_queue.queue:
                if task.path == event.path:
                    self.download_queue.queue.remove(task)
            # The file wont need to be uploaded since it was deleted
            for task in self.upload_queue.queue:
                if task.path == event.path:
                    self.upload_queue.queue.remove(task)

            # Cancel any upload task on the event path
            self.cancel_upload_task(event.path)
            # Cancel any download task on the event path
            self.cancel_download_task(event.path)

            # Put the task in the queue
            self.simple_tasks.put(event)
        else:
            raise BadEventError("Not a valid event: ",
                    event.__class__.__name__)

    def modified_event(self, event):
        if isinstance(event, events.LocalModifiedEvent):
            # Check the upload queue for redundant events
            for task in self.upload_queue.queue:
                if task.path == event.path:
                    break
            else:
                if not self.is_uploading(event.path):
                    # Put the task in the queue
                    self.upload_queue.put(event)
        elif isinstance(event, events.RemoteModifiedEvent):
            # Check the download queue for redundant events
            for task in self.download_queue.queue:
                if task.path == event.path:
                    break
            else:
                if not self.is_downloading(event.path):
                    # Put the task in the queue
                    self.download_queue.put(event)
        else:
            raise BadEventError("Not a valid event: ",
                    event.__class__.__name__)

    def cancel_upload_task(self, path):
        """ Cancels an upload task given a file path. """
        for worker in self.upload_workers:
            if worker.current_task is not None:
                if worker.current_task.path == path:
                    worker.cancel()

    def cancel_download_task(self, path):
        """ Cancels a download task given a file path. """
        for worker in self.download_workers:
            if worker.current_task is not None:
                if worker.current_task.path == path:
                    worker.cancel()

    def is_downloading(self, path):
        """ Returns whether or not a file is being downloaded. """
        if len(self.download_workers) is 0:
            return False
        for worker in self.download_workers:
            if worker.current_task is not None:
                if worker.current_task.path == path:
                    return True
        else:
            return False

    def is_uploading(self, path):
        """ Returns whether or not a file is being uploaded. """
        if len(self.upload_workers) is 0:
            return False
        for worker in self.upload_workers:
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
    def __init__(self, sync_fs):
        self.sync_fs = sync_fs
        self.results = {}

    def index(self):
        for dir, path in self.sync_fs.walk('/'):
            self._process_path(dir)
            for name in path:
                discovered_path = fs.path.join(dir, name)
                self._process_path(discovered_path)

    def _process_path(self, path):
        filters = [(lambda x: not x == '/')]

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
            helper = LocalDefinitionHelper(path, self.sync_fs)
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

    def index(self, remote_path=None):
        files_indexed = False
        while not files_indexed:
            if remote_path is None:
                remote_path = "/"
            api_path = '/path/info%s' % remote_path

            #TODO: check other errors here later
            try:
                dir_listing = self.api.get(api_path, children=True)
            except ResponseError as e:
                # If the error code is 404, ignore the file.
                if e.status_code == 404:
                    dir_listing = []
            except RequestError, err:
                if err.detail.startswith('HTTPConnectionPool'):
                    # Connection error. Wait 2 seconds then try again.
                    time.sleep(2)
                    try:
                        dir_listing = self.api.get(api_path, children=True)
                    except:
                        dir_listing = []

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
            files_indexed = True
