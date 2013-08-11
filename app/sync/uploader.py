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
            object = self.queue.get()
            self.uploadFile(object)
            self.queue.task_done()

    def uploadFile(self, object):
        path = common.basePath(object.path)
        absolutePath = os.path.join(self.syncDir, path)

        print "[UPLOAD]: (", path, ") ", absolutePath
        if not (os.path.isdir(absolutePath)):
            fileName = os.path.basename(path)
            inDir = path.replace(fileName, '').replace("\\", "/")
            apiPath = "/path/data/%s" % inDir
            print "putting: %s" % inDir

            #make sure the directory exists before uploading
            self.smartfile.put('/path/oper/mkdir/', inDir)

            #the actual uploading of the file
            self.smartfile.post(apiPath, file=file(absolutePath, 'rb'))
            #TODO: Add modifiedTime and fileHash attributes here
        else:
            self.smartfile.put('/path/oper/mkdir/', path)

