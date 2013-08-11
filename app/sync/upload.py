import os
import threading

import common


class Uploader(object):
    def __init__(self, api, syncDir):
        self.api = api
        self.syncDir = syncDir

    def upload(self, object):
        path = common.basePath(object.path)
        absolutePath = os.path.join(self.syncDir, path)

        print "[UPLOAD]: (", path, ") ", absolutePath

        if not (os.path.isdir(absolutePath)):
            fileName = os.path.basename(path)
            inDir = path.replace(fileName, '').replace("\\", "/")
            apiPath = "/path/data/%s" % inDir

            #make sure the directory exists before uploading
            self.api.put('/path/oper/mkdir/', inDir)

            #the actual uploading of the file
            self.api.post(apiPath, file=file(absolutePath, 'rb'))

            #TODO: Add modifiedTime and fileHash attributes here
        else:
            self.api.put('/path/oper/mkdir/', path)


class UploadThread(Uploader, threading.Thread):
    def __init__(self, queue, api, syncDir):
        threading.Thread.__init__(self)
        Uploader.__init__(self, api, syncDir)
        self.queue = queue

    def run(self):
        while True:
            object = self.queue.get()
            self.upload(object)
            self.queue.task_done()

