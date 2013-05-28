import os
import threading


class Uploader(threading.Thread):
    def __init__(self, queue, smartfile, syncDir):
        threading.Thread.__init__(self)
        self.queue = queue
        self.smartfile = smartfile
        self.syncDir = syncDir

    def run(self):
        while True:
            path = self.queue.get()
            self.uploadFile(path)
            self.queue.task_done()

    def uploadFile(self, path):
        serverPath = path
        if path.startswith("/"):
            path = path.replace("/", "", 1)
        absolutePath = os.path.join(self.syncDir, path)
        if not (os.path.isdir(absolutePath)):
            print "Uploading to %s from %s" % (path, absolutePath)
            self.smartfile.post("/path/data/", file=file(absolutePath, 'rb'))
        else:
            self.smartfile.post('/path/oper/mkdir/', serverPath)
            self.uploadFile(path)
