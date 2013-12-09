import datetime
import logging
import os
import threading

import common
from errors import DownloadException
from errors import FileNameException
from worker import Worker


log = logging.getLogger(__name__)


class Downloader(Worker):
    def __init__(self, api, sync_dir):
        self._api = api
        self._sync_dir = sync_dir
        self._timeoffset = common.calculate_time_offset()

        super(Downloader, self).__init__()

    def _process_task(self, task):
        basepath = os.path.normpath(task.path)
        if basepath.startswith("/"):
            basepath = basepath.strip("/")
        absolute_path = os.path.join(self._sync_dir, basepath)

        task_directory = os.path.dirname(absolute_path)

        if not os.path.exists(task_directory):
            # Create the directories necessary to download the file
            log.debug("Creating the directory: " + task_directory)
            common.createLocalDirs(task_directory)

        if task.isDir is False:
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
                    raise DownloadException(err)
            except Exception as err:
                raise DownloadException(err)

            if not self.cancelled:
                if not hasattr(task, 'checksum'):
                    self._setAttributes(task)

            # Notify the worker the task is complete
            self.task_done()

    def _setAttributes(self, task):
        """ Set attributes for the file on the SmartFile API. """
        path = os.path.join(self._sync_dir, task.path)
        task.checksum = common.getFileHash(path)
        # Get the local modified time
        file_time = os.path.getmtime(path)
        # Generate a timestamp
        modified_local = datetime.datetime.fromtimestamp(file_time)
        # Strip off microseconds. We only care about seconds.
        local_time = modified_local.replace(microsecond=0)
        # Shift the time accordingly to the time server offset
        shifted_time = local_time - self._timeoffset

        checksum_string = "checksum=%s" % task.checksum
        modified_string = "modified=%s" % shifted_time

        request_properties = [checksum_string, modified_string]

        apiPath = "/path/info%s" % task.path
        self._api.post(apiPath, attributes=request_properties)

    def _cancel(self):
        self.cancelled = True


class DownloadThread(threading.Thread):
    def __init__(self, queue, api, sync_dir):
        threading.Thread.__init__(self)
        self._downloader = Downloader(api, sync_dir)
        self._queue = queue

        self._current_task = None

    def run(self):
        while True:
            log.debug("Getting a new task.")
            self._current_task = self._queue.get()
            try:
                log.debug("Processing: " + self._current_task.path)
                self._downloader.process_task(self._current_task)
            except FileNameException:
                # Files that have invalid names should not be downloaded
                log.warning("The file to be downloaded had a bad filename.")
                pass
            except:
                raise
                # Put the task back into the queue and try later
                log.debug("Putting the task in the queue to try later.")
                self._queue.put(self._current_task)
            log.debug("Task complete.")
            self._queue.task_done()

    def cancel(self):
        log.debug("Task canceled: " + self._current_task.path)
        self._downloader.cancel_task()
        self._queue.task_done()

    @property
    def current_task(self):
        return self._current_task
