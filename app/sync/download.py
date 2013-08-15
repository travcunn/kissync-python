import datetime
import os
import shutil
import threading

import common


class Downloader(object):
    def __init__(self, api, syncDir):
        self.api = api
        self.syncDir = syncDir
        self._timeoffset = None
        if self._timeoffset is None:
            self._timeoffset = common.calculate_time_offset()

    def download(self, object):
        serverPath = object.path
        path = common.basePath(object.path)
        absolutePath = os.path.join(self.syncDir, path)

        print "[DOWNLOAD-QUEUE]", path, absolutePath

        common.createLocalDirs(os.path.dirname(os.path.realpath(absolutePath)))
        if object.isDir is False:
            try:
                f = self.api.get('/path/data/', serverPath)
                with open(absolutePath, 'wb') as o:
                    shutil.copyfileobj(f, o)
                #TODO: if the object didnt have a checksum, calculate it, then
                # set the checksum attribute in the api
            except:
                raise

            if object.checksum is None:
                self.setAttributes(object)

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


class DownloadThread(Downloader, threading.Thread):
    def __init__(self, queue, api, syncDir):
        threading.Thread.__init__(self)
        Downloader.__init__(self, api, syncDir)
        self.queue = queue

    def run(self):
        while True:
            object = self.queue.get()
            self.download(object)
            self.queue.task_done()
