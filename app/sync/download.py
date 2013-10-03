import datetime
import history
import os
import shutil
import threading

import common


class Downloader(object):
    def __init__(self, api, syncDir):
        self._api = api
        self._syncDir = syncDir
        self._timeoffset = common.calculate_time_offset()

    def download(self, object):
        serverPath = object.path
        path = common.basePath(object.path)
        absolutePath = os.path.join(self._syncDir, path)

        common.createLocalDirs(os.path.dirname(os.path.realpath(absolutePath)))
        if object.isDir is False:
            print "[DOWNLOAD-QUEUE]", path, absolutePath
            try:
                f = self._api.get('/path/data/', serverPath)
                with open(absolutePath, 'wb') as o:
                    shutil.copyfileobj(f, o)
            except IOError, err:
                if err.errno == 22:
                    # Windows has file name restrictions. These types of files
                    # are to be ignored
                    pass
                else:
                    raise
            except:
                raise

            if object.checksum is None:
                self._setAttributes(object)

    def _setAttributes(self, object):
        path = os.path.join(self._syncDir, common.basePath(object.path))
        object.checksum = common.getFileHash(path)
        modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0) - self._timeoffset

        checksumString = "checksum=%s" % object.checksum
        modifiedString = "modified=%s" % modified
        apiPath = "/path/info%s" % object.path

        #TODO: reduce this to one request
        self._api.post(apiPath, attributes=checksumString)
        self._api.post(apiPath, attributes=modifiedString)


class DownloadThread(Downloader, threading.Thread):
    def __init__(self, queue, api, syncDir):
        threading.Thread.__init__(self)
        Downloader.__init__(self, api, syncDir)
        self.queue = queue

    def run(self):
        while True:
            object = self.queue.get()
            try:
                if history.isLatest(object):
                    # Tell the history we are about to download the file
                    history.update(object)
                    self.download(object)
            except:
                # Set the history to None, since it failed
                history._history[object.path] = None
                # Put the object back into the queue and try later
                self.queue.put(object)
            self.queue.task_done()
