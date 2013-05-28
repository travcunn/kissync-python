import errno
import os
import shutil
import threading


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
        if path.startswith("/"):
            path = path.replace("/", "", 1)
        elif path.startswith("\\"):
            path = path.replace("\\", "", 1)
        absolutePath = os.path.join(self.syncDir, path)
        self.checkDirsToCreate(os.path.dirname(os.path.realpath(absolutePath)))
        try:
            f = self.smartfile.get('/path/data/', serverPath)
            with file(absolutePath, 'wb') as o:
                shutil.copyfileobj(f, o)
        except:
            raise

    def checkDirsToCreate(self, path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
