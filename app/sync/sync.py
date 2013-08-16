import datetime
import os
import threading
from smartfile.errors import ResponseError

import common


class SyncUp(object):
    def __init__(self, api, sync, syncDir):
        self.api = api
        self.sync = sync
        self.syncDir = syncDir
        self._timeoffset = None
        if self._timeoffset is None:
            self._timeoffset = common.calculate_time_offset()

    def syncUp(self, object):
        serverPath = object[0].path
        path = common.basePath(serverPath)
        absolutePath = os.path.join(self.syncDir, path)

        print "[SYNC-UP-QUEUE]", path, absolutePath

        try:
            self.sync.upload(absolutePath, serverPath)
        except ResponseError, err:
            if err.status_code == 500:
                # The server gives a 500 when the sync is successful. bug?
                self.setAttributes(object[0])
        except:
            raise
        else:
            self.setAttributes(object[0])


    def setAttributes(self, object):
        #TODO: Change this back to modified and implement proper time checking
        path = os.path.join(self.syncDir, common.basePath(object.path))
        checksum = common.getFileHash(path)
        modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0) - self._timeoffset
        fileChecksum = "checksum=%s" % checksum
        fileModified = "modified=%s" % modified
        apiPath = "/path/info%s" % object.path

        #TODO: reduce this to one request
        self.api.post(apiPath, attributes=fileChecksum)
        self.api.post(apiPath, attributes=fileModified)


class SyncUpThread(SyncUp, threading.Thread):
    def __init__(self, queue, api, sync, syncDir):
        threading.Thread.__init__(self)
        SyncUp.__init__(self, api, sync, syncDir)
        self.queue = queue

    def run(self):
        while True:
            object = self.queue.get()
            self.syncUp(object)
            self.queue.task_done()


class SyncDown(object):
    def __init__(self, api, sync, syncDir):
        self.api = api
        self.sync = sync
        self.syncDir = syncDir
        self._timeoffset = None
        if self._timeoffset is None:
            self._timeoffset = common.calculate_time_offset()

    def syncDown(self, object):
        serverPath = object[0].path
        path = common.basePath(serverPath)
        absolutePath = os.path.join(self.syncDir, path)
        try:
            self.sync.download(absolutePath, serverPath)
        except:
            raise
        else:
            self.setAttributes(object[0])

    def setAttributes(self, object):
        #TODO: Change this back to modified and implement proper time checking
        path = os.path.join(self.syncDir, common.basePath(object.path))
        checksum = common.getFileHash(path)
        modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0) - self._timeoffset
        fileChecksum = "checksum=%s" % checksum
        fileModified = "modified=%s" % modified
        apiPath = "/path/info%s" % object.path

        #TODO: reduce this to one request
        self.api.post(apiPath, attributes=fileChecksum)
        self.api.post(apiPath, attributes=fileModified)


class SyncDownThread(SyncDown, threading.Thread):
    def __init__(self, queue, api, sync, syncDir):
        threading.Thread.__init__(self)
        self.queue = queue
        self.api = api
        self.sync = sync
        self.syncDir = syncDir

    def run(self):
        while True:
            path = self.queue.get()
            self.syncDown(path)
            self.queue.task_done()
