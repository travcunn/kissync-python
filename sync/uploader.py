import os
import threading
from baseclient import BaseClient


class Uploader(threading.Thread, BaseClient):
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
        path = self.basePath(path)
        absolutePath = os.path.join(self.syncDir, path)
        if not (os.path.isdir(absolutePath)):
            print "Uploading to %s from %s" % (path, absolutePath)
            fileName = os.path.basename(path)
            apiPath = "/path/data/%s" % path.replace(fileName, '')
            #TODO: Add a method to check if upload directories exist before uploading
            self.smartfile.post(apiPath, file=file(absolutePath, 'rb'))
        else:
            self.smartfile.post('/path/oper/mkdir/', serverPath)
            self.uploadFile(path)
