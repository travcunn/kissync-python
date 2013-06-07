import datetime
import os
import threading
import time
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler


class Watcher(threading.Thread):
    def __init__(self, parent, smartfile, syncDir):
        threading.Thread.__init__(self)
        self.parent = parent
        self.smartfile = smartfile
        self.syncDir = syncDir

    def run(self):
        self.event_handler = EventHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.syncDir, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()


class EventHandler(FileSystemEventHandler):
    def __init__(self, parent=None):
        self.parent = parent
        self.syncDir = self.parent.syncDir

    def on_moved(self, event):
        serverPath = self.localToServerPath(event.src_path)
        serverPathNew = self.localToServerPath(event.src_path)
        try:
            self.parent.smartfile.post('/path/oper/move/', src=serverPath, dst=serverPathNew)
        except:
            raise

    def on_created(self, event):
        file = event.src_path
        serverPath = self.localToServerPath(file)
        if not event.is_directory:
            modifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(file))
            fileHash = self.parent.parent._getFileHash(file)
            task = (serverPath, modifiedTime, fileHash)
            self.parent.parent.uploadQueue.put(task)
        else:
            try:
                self.parent.smartfile.post('/path/oper/mkdir/', path=serverPath)
            except:
                raise

    def on_deleted(self, event):
        try:
            self.parent.smartfile.post('/path/oper/remove', path=event.src_path)
        except:
            raise

    def on_modified(self, event):
        if not event.is_directory:
            #TODO: add file to the synchronize queue here
            pass

    def localToServerPath(self, path):
        pathOnServer = path.replace(self.syncDir, '')
        if pathOnServer.startswith("/"):
            pathOnServer = pathOnServer.strip("/")
        elif pathOnServer.startswith("\\"):
            pathOnServer = pathOnServer.strip("\\")
        return pathOnServer
