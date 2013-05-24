import errno
import os
import shutil
import threading


class Download(threading.Thread):
    def __init__(self, parent, queue):
        threading.Thread.__init__(self)
        self.parent = parent
        self.queue = queue

    def run(self):
        while True:
            path = self.queue.get()
            self.downloadFile(path)
            self.queue.task_done()

    def downloadFile(self, filepath):
        absolutePath = os.path.join(self.parent.parent.configuration.get('LocalSettings', 'sync-dir'), filepath)
        self.checkDirsToCreate(absolutePath)
        try:
            f = self.parent.parent.smartfile.get('/path/data/', filepath)
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
