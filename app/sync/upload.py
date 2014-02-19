import logging
import os
import threading
import time

from fs.osfs import OSFS
from smartfile.errors import RequestError, ResponseError

import common
from definitions import FileDefinition, LocalDefinitionHelper
from errors import FileNotAvailableError, FileDeletedError, MaxTriesError
from errors import UploadError
from worker import Worker


log = logging.getLogger(__name__)


class Uploader(Worker):
    def __init__(self, api, sync_dir):
        self._api = api
        self._sync_dir = sync_dir
        self._timeoffset = common.calculate_time_offset()
        self._syncFS = OSFS(sync_dir)

    def _process_task(self, task):
        # Check if the task is already a file definition
        if not isinstance(task, FileDefinition):
            helper = LocalDefinitionHelper(task.path, self._syncFS)
            try:
                task = helper.create_definition()
            except WindowsError, err:
                raise FileDeletedError(err)
        # Create a system specific path relative to the sync dir
        basepath = os.path.normpath(task.path)
        if basepath.startswith("/"):
            basepath = basepath.strip("/")
        if basepath.startswith('\\'):
            basepath = basepath.lstrip('\\')
        # Full system path
        absolute_path = os.path.join(self._sync_dir, basepath)

        # If the task is a file
        if not os.path.isdir(absolute_path):
            basepath = basepath.replace('\\', '/')
            if not basepath.startswith("/"):
                basepath = os.path.join("/", basepath)

            task_directory = os.path.dirname(basepath)
            api_path = "/path/data%s" % basepath
            api_path_base = os.path.dirname(api_path)

            try:
                # create the directory to make sure it exists
                self._api.post('/path/oper/mkdir/', path=task_directory)
                # upload the file
                self._api.post(api_path_base, file=file(absolute_path, 'rb'))
                # set the new attributes
            except IOError, err:
                if err.errno == 2:
                    raise FileNotAvailableError(err)
            except ResponseError, err:
                if err.status_code == 404:
                    # If the file becomes suddenly not available, just ignore
                    # trying to set its attributes.
                    pass
                elif err.status_code == 409:
                    # Conflict - Can only upload to an existing directory.
                    raise UploadError(err)
            except RequestError, err:
                if err.detail.startswith('HTTPConnectionPool'):
                    raise MaxTriesError(err)
            else:
                self._set_attributes(task)
        else:
            # If the task path is a folder
            task_directory = basepath
            if not task_directory.startswith("/"):
                task_directory = os.path.join("/", task_directory)
            task_directory = task_directory.replace('\\', '/')
            try:
                self._api.post('/path/oper/mkdir/', path=task_directory)
            except RequestError, err:
                raise MaxTriesError(err)
            except Exception, err:
                raise UploadError(err)

        return task

    def _set_attributes(self, task):
        checksum = task.checksum
        modified = task.modified.replace(microsecond=0)

        checksum_string = "checksum=%s" % checksum
        modified_string = "modified=%s" % modified
        apiPath = "/path/info%s" % task.path

        try:
            self.__set_attributes(apiPath, checksum_string, modified_string)
        except ResponseError, err:
            if err.status_code == 404:
                """
                If we try setting attributes to a file too soon, SmartFile
                gives us an error, so sleep the thread for a bit.
                """
                time.sleep(1)
                # Now try setting the attributes again
                self.__set_attributes(apiPath, checksum_string,
                                      modified_string)
            elif err.status_code == 500:
                self.__set_attributes(apiPath, checksum_string,
                                      modified_string)

    def __set_attributes(self, api_path, checksum_string, modified_string):
        request_properties = [checksum_string, modified_string]
        try:
            self._api.post(api_path, attributes=request_properties)
        except ResponseError, err:
            if err.status_code == 404:
                # If the file becomes suddenly not available, just ignore
                # trying to set its attributes
                pass
            if err.status_code == 500:
                # Ignore server errors since they shouldnt happen anyways
                pass
        except RequestError, err:
            if err.detail.startswith('HTTPConnectionPool'):
                raise MaxTriesError(err)


class UploadWorker(threading.Thread):
    def __init__(self, queue, api, sync_dir, remote_files, realtime=False):
        threading.Thread.__init__(self)
        self._uploader = Uploader(api, sync_dir)
        self._queue = queue
        self._remote_files = remote_files

        self._realtime = realtime

    def run(self):
        while True:
            log.debug("Getting a new task.")
            self._current_task = None
            self._current_task = self._queue.get()
            try:
                log.debug("Processing: " + self._current_task.path)
                result = self._uploader.process_task(self._current_task)
                # Update the remote files dictionary to reflect the new file
                self._remote_files[result.path] = result
            except FileNotAvailableError:
                # The file was not available when uploading it
                log.warning("File is not yet available: " +
                            self._current_task.path)
                self.try_task_later()
            except MaxTriesError:
                log.warning("Connection error occured while uploading: " +
                            self._current_task.path)
                self.try_task_later()
            except UploadError:
                log.warning("Folders were not created properly for: " +
                            self._current_task.path)
                self.try_task_later()
            except FileDeletedError:
                log.warning("The file was deleted before trying to upload:" +
                            self._current_task.path)
            else:
                # Notify the realtime messaging system of the upload
                if self._realtime:
                    log.debug("Sending an update message about: " +
                              self._current_task.path)
                    self._realtime.update(self._current_task)
            log.debug("Task complete.")
            self._queue.task_done()

    def try_task_later(self):
        self._queue.put(self._current_task)

    def cancel(self):
        log.debug("Task cancelled: " + self._current_task.path)
        self._uploader.cancel_task()

    @property
    def current_task(self):
        return self._current_task
