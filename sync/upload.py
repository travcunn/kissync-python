import os
import threading


class Upload(threading.Thread):
    def __init__(self, parent, queue):
        threading.Thread.__init__(self)
        self.parent = parent
        self.queue = queue
        self.syncdirPath = self.parent.parent.configuration.get('LocalSettings', 'sync-dir')

    def run(self):
        while True:
            path = self.queue.get()
            self.uploadFile(path)
            self.queue.task_done()

    def uploadFile(self, filepath):
        filepath = self.syncdirPath + filepath
        if not (os.path.isdir(filepath)):
            #Todo: Upload the files here
            pass
        else:
            self.parent.parent.smartfile.post('/path/oper/mkdir/', filepath.replace(self.syncdirPath, ''))
