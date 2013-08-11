import os
import shutil
import threading

import common


class Downloader(object):
    def __init__(self, api, syncDir):
        self.api = api
        self.syncDir = syncDir

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

