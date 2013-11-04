import datetime
import history
import os
import threading

import common

from errors import DownloadException
from errors import FileNameException


class Downloader(object):
    def __init__(self, api, syncDir):
        self.api = api
        self.syncDir = syncDir
        self._timeoffset = common.calculate_time_offset()

        self.cancelled = False

    def download(self, syncObject):
        serverPath = syncObject.path
        path = common.basePath(syncObject.path)
        absolutePath = os.path.join(self.syncDir, path)

        common.createLocalDirs(os.path.dirname(os.path.realpath(absolutePath)))

        if syncObject.isDir is False:
            try:
                with open(absolutePath, 'wb') as f:
                    r = self.api.get('/path/data/', serverPath)
                    for chunk in r.iter_content(chunk_size=1024):
                        if not self.cancelled and chunk:
                            f.write(chunk)
                            f.flush()
                if self.cancelled:
                    self.cancelled = False
            except IOError as err:
                if err.errno == 22:
                    # Depending on the OS, there may be filename restrictions
                    raise FileNameException(err)
                else:
                    raise DownloadException(err)
            except Exception as err:
                raise DownloadException(err)

            if syncObject.checksum is None:
                self._setAttributes(syncObject)

    def _setAttributes(self, syncObject):
        if not self.cancelled:
            path = os.path.join(self.syncDir, syncObject.system_path)
            syncObject.checksum = common.getFileHash(path)
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0) - self._timeoffset

            checksumString = "checksum=%s" % syncObject.checksum
            modifiedString = "modified=%s" % modified

            requestAttr = [checksumString, modifiedString]

            apiPath = "/path/info%s" % syncObject.path
            self.api.post(apiPath, attributes=requestAttr)

    def _cancel(self):
        self.cancelled = True


class DownloadThread(Downloader, threading.Thread):
    def __init__(self, queue, api, syncDir):
        threading.Thread.__init__(self)
        Downloader.__init__(self, api, syncDir)
        self.queue = queue

    def run(self):
        while True:
            syncObject = self.queue.get()
            try:
                if history.isLatest(syncObject):
                    # Tell the history we are about to download the file
                    history.update(syncObject)
                    self.download(syncObject)
            except:
                # Set the history to None, since it failed
                history._history[syncObject.path] = None
                # Put the syncObject back into the queue and try later
                self.queue.put(syncObject)
            self.queue.task_done()

    def cancel(self):
        self._cancel()
        self.queue.task_done()
