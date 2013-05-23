import threading
import time
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler


class Watcher(threading.Thread):
    def __init__(self, parent=None):
        threading.Thread.__init__(self)
        self.parent = parent

    def run(self):
        self.path = self.parent.configuration.get('LocalSettings', 'sync-dir')
        self.event_handler = EventHandler(self.parent)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=True)
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
        self.syncdirPath = self.parent.configuration.get('LocalSettings', 'sync-dir')

    def on_moved(self, event):
        serverPath = self.localToServerPath(event.src_path)
        serverPathNew = self.localToServerPath(event.src_path)
        try:
            #TODO: add file to the queue for smartifle operations
            #self.parent.smartfile.post('/path/oper/move/', src=serverPath, dst=serverPathNew)
            pass
        except:
            raise

    def on_created(self, event):
        serverPath = self.localToServerPath(event.src_path)
        if not (event.is_directory):
            #TODO: add file to the upload queue here
            pass
        else:
            try:
                #TODO: add file to the queue for smartifle operations
                #self.parent.smartfile.post('/path/oper/mkdir/', path=serverPath)
                pass
            except:
                raise

    def on_deleted(self, event):
        serverPath = self.localToServerPath(event.src_path)
        try:
            #TODO: add file to the queue for smartifle operations
            #self.parent.smartfile.post('/path/oper/remove', path=event.src_path)
            pass
        except:
            pass

    def on_modified(self, event):
        serverPath = self.localToServerPath(event.src_path)
        if not (event.is_directory):
            #TODO: add file to the synchronize queue here
            pass

    def localToServerPath(self, path):
        pathOnServer = path.replace(self.syncdirPath, '')
        if(pathOnServer.startswith("/")):
            pathOnServer = pathOnServer.strip("/")
        elif(pathOnServer.startswith("\\")):
            pathOnServer = pathOnServer.strip("\\")
        return pathOnServer
