import os
import threading

import common


class Uploader(object):
    def __init__(self, api, syncDir):
        self.api = api
        self.syncDir = syncDir
        self._timeoffset = None
        if self._timeoffset is None:
            self._timeoffset = common.calculate_time_offset()

    def upload(self, object):
        path = common.basePath(object.path)
        absolutePath = os.path.join(self.syncDir, path)

        print "[UPLOAD]: (", path, ") ", absolutePath

        if not (os.path.isdir(absolutePath)):
            fileName = os.path.basename(path)
            inDir = path.replace(fileName, '').replace("\\", "/")
            apiPath = "/path/data/%s" % inDir

            #TODO: Check if this is actually doing what it should do
            # create directory before uploading
            self.api.put('/path/oper/mkdir/', inDir)

            # upload the file
            self.api.post(apiPath, file=file(absolutePath, 'rb'))

            # set the new attributes
            self.setAttributes(object)
        else:
            self.api.put('/path/oper/mkdir/', path)

    def setAttributes(self, object):
        checksum = object.checksum
        #TODO: Change this back to modified and implement proper time checking
        modified = object.modified_local.replace(microsecond=0)

        fileChecksum = "checksum=%s" % checksum
        fileModified = "modified=%s" % modified
        apiPath = "/path/info%s" % object.path

        #TODO: reduce this to one request
        self.api.post(apiPath, attributes=fileChecksum)
        self.api.post(apiPath, attributes=fileModified)


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
