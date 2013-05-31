import os
import threading

import common


class SyncUp(threading.Thread):
    def __init__(self, queue, smartfile, sync, syncDir):
        threading.Thread.__init__(self)
        self.queue = queue
        self.smartfile = smartfile
        self.sync = sync
        self.syncDir = syncDir

    def run(self):
        while True:
            path = self.queue.get()
            self.syncUp(path)
            self.queue.task_done()

    def syncUp(self, path):
        serverPath = path
        path = common.basePath(path)
        absolutePath = os.path.join(self.syncDir, path)
        try:
            self.sync.upload(absolutePath, serverPath)
            #TODO: Add modifiedTime and fileHash attributes here
        except:
            raise


class SyncDown(threading.Thread):
    def __init__(self, queue, smartfile, sync, syncDir):
        threading.Thread.__init__(self)
        self.queue = queue
        self.smartfile = smartfile
        self.sync = sync
        self.syncDir = syncDir

    def run(self):
        while True:
            path = self.queue.get()
            self.syncDown(path)
            self.queue.task_done()

    def syncDown(self, path):
        serverPath = path
        path = common.basePath(path)
        absolutePath = os.path.join(self.syncDir, path)
        try:
            self.sync.download(absolutePath, serverPath)
        except:
            raise
