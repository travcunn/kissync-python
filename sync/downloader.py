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
            path = self.queue.get()
            self.downloadFile(path)
            self.queue.task_done()

    def downloadFile(self, path):
        serverPath = path
        path = common.basePath(path)
        absolutePath = os.path.join(self.syncDir, path)
        common.createLocalDirs(os.path.dirname(os.path.realpath(absolutePath)))
        try:
            f = self.smartfile.get('/path/data/', serverPath)
            with file(absolutePath, 'wb') as o:
                shutil.copyfileobj(f, o)
        except:
            raise
