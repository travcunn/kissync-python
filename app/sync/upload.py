import os
import threading
import time

from smartfile.errors import ResponseError

import common


class Uploader(object):
    def __init__(self, api, syncDir, parent):
        self._api = api
        self._syncDir = syncDir
        self._timeoffset = common.calculate_time_offset()

        self.parent = parent

    def upload(self, object):
        print "[UPLOAD]: (", object.path, ") ", object.system_path

        # If the object is a file
        if not os.path.isdir(object.system_path):
            inDir = os.path.dirname(object.path).replace("\\", "/").rstrip('/')
            if not inDir.startswith("/"):
                inDir = os.path.join("/", inDir)
            apiPath = "/path/data/%s" % inDir
            # create the directory to make sure it exists
            self._api.post('/path/oper/mkdir/', path=inDir)
            # upload the file
            self._api.post(apiPath, file=file(object.system_path, 'rb'))
            # set the new attributes
            self._setAttributes(object)

            # Notify the realtime sync of the change
            if self.parent.watcherRunning:
                self.parent.localWatcher.realtime.update(object.path, 'created_file', 0, False)
        # If the object is a folder
        else:
            createDir = object.path
            self._api.post('/path/oper/mkdir/', path=createDir)

            # Notify the realtime sync of the change
            if self.parent.watcherRunning:
                self.parent.localWatcher.realtime.update(createDir, 'created_dir', 0, True)

    def _setAttributes(self, object):
        checksum = object.checksum
        modified = object.modified_local.replace(microsecond=0)

        checksumString = "checksum=%s" % checksum
        modifiedString = "modified=%s" % modified
        apiPath = "/path/info%s" % object.path

        try:
            self.__setAttributes(apiPath, checksumString, modifiedString)
        except ResponseError, err:
            if err.status_code == 404:
                """
                If we try setting attributes to a file too soon, SmartFile
                gives us an error, so sleep the thread for a bit
                """
                time.sleep(1)
                # Now try setting the attributes again
                self.__setAttributes(apiPath, checksumString, modifiedString)
            elif err.status_code == 500:
                self.__setAttributes(apiPath, checksumString, modifiedString)
            else:
                raise
        except:
            raise

    def __setAttributes(self, apiPath, fileChecksum, fileModified):
        #TODO: reduce this to one request
        self._api.post(apiPath, attributes=fileChecksum)
        self._api.post(apiPath, attributes=fileModified)


class UploadThread(Uploader, threading.Thread):
    def __init__(self, queue, api, syncDir, parent):
        threading.Thread.__init__(self)
        Uploader.__init__(self, api, syncDir, parent)
        self.queue = queue

    def run(self):
        while True:
            object = self.queue.get()
            self.upload(object)
            self.queue.task_done()
