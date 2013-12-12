import logging
import os
import threading

from fs.osfs import OSFS
from smartfile.errors import RequestError

import common
from definitions import LocalDefinitionHelper
from errors import DownloadException, FileNameException
from errors import FileNotAvailableException, MaxTriesException
from worker import Worker


log = logging.getLogger(__name__)


class Downloader(Worker):
    def __init__(self, api, sync_dir):
        self._api = api
        self._sync_dir = sync_dir
        self._timeoffset = common.calculate_time_offset()
        self.syncFS = OSFS(self._sync_dir)

        super(Downloader, self).__init__()

    def _process_task(self, task):
        # Create a system specific path relative to the sync dir
        basepath = os.path.normpath(task.path)
        if basepath.startswith("/"):
            basepath = basepath.strip("/")
        if basepath.startswith('\\'):
            basepath = basepath.lstrip('\\')
        # Full system path
        absolute_path = os.path.join(self._sync_dir, basepath)

        task_directory = os.path.dirname(absolute_path)

        if task.isDir:
            if not os.path.exists(absolute_path):
                log.debug("Creating the directory: " + absolute_path)
                common.createLocalDirs(absolute_path)
        else:
            if not os.path.exists(task_directory):
                # Create the directories necessary to download the file
                log.debug("Creating the directory: " + task_directory)
                common.createLocalDirs(task_directory)

        if not task.isDir:
            basepath = basepath.replace('\\', '/')
            if not basepath.startswith("/"):
                basepath = os.path.join("/", basepath)
            print basepath
            try:
                with open(absolute_path, 'wb') as f:
                    response = self._api.get('/path/data', basepath)
                    for chunk in response.iter_content(chunk_size=1024):
                        if not self.cancelled and chunk:
                            f.write(chunk)
                            f.flush()
            except IOError as err:
                if err.errno == 22:
                    # Depending on the OS, there may be filename restrictions
                    raise FileNameException(err)
                else:
                    raise FileNotAvailableException(err)
            except RequestError as err:
                if err.detail.startswith('HTTPConnectionPool'):
                    raise MaxTriesException
            except Exception as err:
                if err.status_code == 415:
                    # Ignore error 415:
                    # 'Unsupported media - You may have mixed up file/folder.'
                    pass
                else:
                    raise DownloadException(err)
            else:
                if not self.cancelled:
                    if not hasattr(task, 'checksum'):
                        return self._setAttributes(task)

            # Notify the worker the task is complete
            self.task_done()

            return None

    def _setAttributes(self, task):
        """ Set attributes for the file on the SmartFile API. """
        path = os.path.join(self._sync_dir, task.path)

        helper = LocalDefinitionHelper(path, self.syncFS)
        definition = helper.create_definition()

        checksum_string = "checksum=%s" % definition.checksum
        modified_string = "modified=%s" % definition.modified

        request_properties = [checksum_string, modified_string]

        apiPath = "/path/info%s" % task.path

        try:
            self._api.post(apiPath, attributes=request_properties)
        except RequestError, err:
            if err.detail.startswith('HTTPConnectionPool'):
                raise MaxTriesException(err)

        return definition


class DownloadThread(threading.Thread):
    def __init__(self, queue, api, sync_dir, local_files):
        threading.Thread.__init__(self)
        self._downloader = Downloader(api, sync_dir)
        self._queue = queue
        self._local_files = local_files

    def run(self):
        while True:
            log.debug("Getting a new task.")
            self._current_task = None
            self._current_task = self._queue.get()
            try:
                log.debug("Processing: " + self._current_task.path)
                result = self._downloader.process_task(self._current_task)
                # Update the local files dictionary to reflect the new file
                if result is not None:
                    self._local_files[result.path] = result
            except FileNameException:
                # Files that have invalid names should not be downloaded
                log.warning("The file to be downloaded had a bad filename.")
                pass
            except FileNotAvailableException:
                log.warning("The local file was not available.")
            except:
                raise
                # Put the task back into the queue and try later
                log.debug("Putting the task in the queue to try later.")
                self._queue.put(self._current_task)
            log.debug("Task complete.")
            self._queue.task_done()

    def cancel(self):
        log.debug("Task cancelled: " + self._current_task.path)
        self._downloader.cancel_task()

    @property
    def current_task(self):
        return self._current_task
