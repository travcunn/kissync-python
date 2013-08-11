import os
import shutil
import threading

import common


class Downloader(threading.Thread):
    def __init__(self, queue, smartfile, syncDir):
        threading.Thread.__init__(self)
        self.queue = queue
        self.smartfile = smartfile
        self.syncDir = syncDir

    def run(self):
        while True:
            object = self.queue.get()
            self.downloadFile(object)
            self.queue.task_done()

    def downloadFile(self, object):
        serverPath = object.path
        path = common.basePath(object.path)
        absolutePath = os.path.join(self.syncDir, path)

        print "[DOWNLOAD-QUEUE]", path, absolutePath

        common.createLocalDirs(os.path.dirname(os.path.realpath(absolutePath)))
        if object.isDir is False:
            try:
                f = self.smartfile.get('/path/data/', serverPath)
                with open(absolutePath, 'wb') as o:
                    shutil.copyfileobj(f, o)
                #TODO: if the object didnt have a checksum, calculate it, then
                # set the checksum attribute in the api
            except:
                raise
