import logging
import os
import threading
import time

from fs.osfs import OSFS
from smartfile.errors import RequestError, ResponseError

import common
from definitions import LocalDefinitionHelper
from errors import FileNotAvailableException, MaxTriesException
from errors import UploadException
from worker import Worker


log = logging.getLogger(__name__)


class Uploader(Worker):
    def __init__(self, api, sync_dir):
        self._api = api
        self._sync_dir = sync_dir
        self._timeoffset = common.calculate_time_offset()
        self._syncFS = OSFS(sync_dir)

    def _process_task(self, task):
        helper = LocalDefinitionHelper(task.path, self._syncFS)
        task = helper.create_definition()
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
            apiPath = "/path/data%s" % basepath
            apiPathBase = os.path.dirname(apiPath)

            try:
                # create the directory to make sure it exists
                self._api.post('/path/oper/mkdir/', path=task_directory)
                # upload the file
                self._api.post(apiPathBase, file=file(absolute_path, 'rb'))
                # set the new attributes
            except ResponseError, err:
                if err.status_code == 404:
                    # If the file becomes suddenly not available, just ignore
                    # trying to set its attributes.
                    pass
                elif err.status_code == 409:
                    # Conflict - Can only upload to an existing directory.
                    raise UploadException(err)
                elif err.status_code == 500:
                    # Ignore server errors for now. The indexer will pick
                    # this file up later on.
                    pass
            except RequestError, err:
                if err.detail.startswith('HTTPConnectionPool'):
                    raise MaxTriesException(err)
            else:
                self._setAttributes(task)
        else:
            # If the task path is a folder
            task_directory = basepath
            if not task_directory.startswith("/"):
                task_directory = os.path.join("/", task_directory)

            self._api.post('/path/oper/mkdir/', path=task_directory)

        return task

    def _setAttributes(self, task):
        checksum = task.checksum
        modified = task.modified.replace(microsecond=0)

        checksum_string = "checksum=%s" % checksum
        modified_string = "modified=%s" % modified
        apiPath = "/path/info%s" % task.path

        try:
            self.__setAttributes(apiPath, checksum_string, modified_string)
        except ResponseError, err:
            if err.status_code == 404:
                """
                If we try setting attributes to a file too soon, SmartFile
                gives us an error, so sleep the thread for a bit.
                """
                time.sleep(1)
                # Now try setting the attributes again
                self.__setAttributes(apiPath, checksum_string,
                                     modified_string)
            elif err.status_code == 500:
                self.__setAttributes(apiPath, checksum_string,
                                     modified_string)

    def __setAttributes(self, apiPath, checksum_string, modified_string):
        request_properties = [checksum_string, modified_string]
        try:
            self._api.post(apiPath, attributes=request_properties)
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
                raise MaxTriesException(err)


class UploadThread(Uploader, threading.Thread):
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
            except FileNotAvailableException:
                # The file was not available when uploading it
                log.warning("File is not yet available.")
                self.try_task_later()
            except MaxTriesException:
                log.warning("Connection error occured during the upload.")
                self.try_task_later()
            except UploadException:
                log.warning("The parent folders were not created properly.")
                self.try_task_later()
            else:
                # Notify the realtime messaging system of the upload
                if self._realtime:
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
