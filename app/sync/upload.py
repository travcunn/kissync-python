import os
import threading
import time

import fs.path
from smartfile.errors import ResponseError

import common
from errors import FileNotAvailableException


class Uploader(object):
    def __init__(self, api, sync_dir):
        self._api = api
        self._sync_dir = sync_dir
        self._timeoffset = common.calculate_time_offset()

    def _process_task(self, task):
        basepath = fs.path.normpath(task.path)
        absolute_path = os.path.join(self._sync_dir, basepath)

        # If the object is a file
        if not os.path.isdir(absolute_path):

            if task.checksum is None:
                try:
                    task.checksum = common.getFileHash(absolute_path)
                except:
                    raise FileNotAvailableException

            inDir = os.path.dirname(object.path).replace("\\", "/").rstrip('/')
            if not inDir.startswith("/"):
                inDir = os.path.join("/", inDir)
            apiPath = "/path/data/%s" % inDir

            # create the directory to make sure it exists
            self._api.post('/path/oper/mkdir/', path=inDir)
            # upload the file
            self._api.post(apiPath, file=file(absolute_path, 'rb'))
            # set the new attributes
            self._setAttributes(task)

            """
            # Notify the realtime sync of the change
            if self.parent.watcherRunning:
                self.parent.localWatcher.realtime.update(task.path, 'created_file', 0, False)
            """
        else:
            # If the task path is a folder
            create_dir = task.path
            self._api.post('/path/oper/mkdir/', path=create_dir)

            """
            # Notify the realtime sync of the change
            if self.parent.watcherRunning:
                self.parent.localWatcher.realtime.update(create_dir, 'created_dir', 0, True)
            """

    def _setAttributes(self, task):
        checksum = task.checksum
        modified = task.modified_local.replace(microsecond=0)

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
            else:
                raise
        except:
            raise

    def __setAttributes(self, apiPath, checksum_string, modified_string):
        request_properties = [checksum_string, modified_string]
        self._api.post(apiPath, attributes=request_properties)


class UploadThread(Uploader, threading.Thread):
    def __init__(self, queue, api, sync_dir):
        threading.Thread.__init__(self)
        self._uploader = Uploader(api, sync_dir)
        self._queue = queue

        self._current_task = None

    def run(self):
        while True:
            self._current_task = self._queue.get()
            try:
                self._uploader.processTask(self._current_task)
            except FileNotAvailableException:
                # The file was not available when uploading it
                self._queue.put(self._current_task)
            self._queue.task_done()
