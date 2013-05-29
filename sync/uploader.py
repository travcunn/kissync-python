import os
import threading

import common


class Uploader(threading.Thread):
    def __init__(self, queue, smartfile, syncDir):
        threading.Thread.__init__(self)
        self.queue = queue
        self.smartfile = smartfile
        self.syncDir = syncDir

    def run(self):
        while True:
            path, modifiedTime, fileHash = self.queue.get()
            self.uploadFile(path, modifiedTime, fileHash)
            self.queue.task_done()

    def uploadFile(self, path, modifiedTime, fileHash):
        path = common.basePath(path)
        absolutePath = os.path.join(self.syncDir, path)
        if not (os.path.isdir(absolutePath)):
            fileName = os.path.basename(path)
            inDir = path.replace(fileName, '')
            apiPath = "/path/data/%s" % inDir

            #make sure the directory exists before uploading
            self.smartfile.put('/path/oper/mkdir/', inDir)

            #the actual uploading of the file
            self.smartfile.post(apiPath, file=file(absolutePath, 'rb'))
            #TODO: Add modifiedTime and fileHash attributes here
        else:
            self.smartfile.put('/path/oper/mkdir/', path)
