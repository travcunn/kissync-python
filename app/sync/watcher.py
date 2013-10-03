import datetime
import os
import threading
import time

import fs.path
from fs.osfs import OSFS

from watchdog.observers import Observer
# Move events arent called on Windows using the PollingObserver
#from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

import common
from definitions import LocalFile
from realtime import RealtimeSync


def checkPath():
    """ Ignore certain types of files """
    def _decorating_wrapper(func):
        def _wrapper(*args, **kwargs):
            path = args[1].src_path
            # Ignore temp files and repositories
            if not path.endswith("~"):
                folder_list = path.split(os.sep)
                for folder in folder_list:
                    if folder.startswith(".svn") or folder.startswith(".git"):
                        return
                return func(*args, **kwargs)
        return _wrapper
    return _decorating_wrapper


class Watcher(threading.Thread):
    def __init__(self, parent, api, syncDir):
        threading.Thread.__init__(self)
        self.parent = parent
        self.api = api
        self.syncDir = syncDir

    def run(self):
        self.event_handler = EventHandler(self, self.parent, self.api)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.syncDir, recursive=True)
        self.observer.start()

        # realtime sync thread
        self.realtime = RealtimeSync(self.parent)
        self.realtime.start()

        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()


class EventHandler(FileSystemEventHandler):
    def __init__(self, parent, synchronizer, api):
        self.parent = parent
        self._synchronizer = synchronizer
        self._api = api
        self._syncDir = self.parent.syncDir
        self._timeoffset = common.calculate_time_offset()

        self._syncFS = OSFS(self._syncDir)

        # This helps the modifiedFix workaround
        self.__modifiedFix = []

    @checkPath()
    def on_moved(self, event):
        serverPath = fs.path.normpath(event.src_path.replace(self._syncDir, ''))
        serverPathNew = fs.path.normpath(event.dest_path.replace(self._syncDir, ''))

        # First, check if the path exists
        if os.path.exists(event.dest_path):
            isDir = os.path.isdir(event.dest_path)
            if serverPath not in self.parent.parent.ignoreFiles and serverPathNew not in self.parent.parent.ignoreFiles:
                print "#######MOVE EVENT########"
                try:
                    #TODO: This doesnt work
                    # According to the logs, /cloud.png gets moved to
                    # /logo.png/cloud.png, where instead it should be moved to
                    # /logo.png.
                    # post created: http://smartfile.forumbee.com/t/19b28
                    self._api.post('/path/oper/move/', src=serverPath, dst=serverPathNew)

                    # Notify the realtime sync of the change
                    self.parent.realtime.update(serverPath, 'moved', 0, isDir, serverPathNew)
                except:
                    pass
            else:
                self.parent.parent.ignoreFiles.remove(serverPath)
                self.parent.parent.ignoreFiles.remove(serverPathNew)

    @checkPath()
    def on_created(self, event):
        path = event.src_path
        serverPath = fs.path.normpath(event.src_path.replace(self._syncDir, ''))
        # First, check if the path exists
        if os.path.exists(path):
            if serverPath not in self.parent.parent.ignoreFiles:
                if not event.is_directory:
                    modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0) - self._timeoffset
                    try:
                        checksum = common.getFileHash(path)
                    except:
                        checksum = None
                    size = int(os.path.getsize(path))
                    isDir = os.path.isdir(path)
                    localfile = LocalFile(serverPath, path, checksum, None, modified, size, isDir)

                    self._synchronizer.uploadQueue.put(localfile)

                    # No realtime notification occurs since this operation
                    # takes place in the upload thread
                else:
                    try:
                        self._api.post('/path/oper/mkdir/', path=serverPath)
                    except:
                        pass
            else:
                self.parent.parent.ignoreFiles.remove(serverPath)

    @checkPath()
    def on_deleted(self, event):
        serverPath = fs.path.normpath(event.src_path.replace(self._syncDir, ''))
        if serverPath not in self.parent.parent.ignoreFiles:
            try:
                self._api.post('/path/oper/remove/', path=serverPath)
                # Notify the realtime sync of the change
                self.parent.realtime.update(serverPath, 'deleted', 0, False)
            except:
                pass
        else:
            self.parent.parent.ignoreFiles.remove(serverPath)

    @checkPath()
    def on_modified(self, event):
        #TODO: put everything in a try catch, in case a file is not available
        # at the time of access. Some apps create temp files and delete them
        # quickly, which can be a problem if we try to read them
        path = event.src_path
        serverPath = fs.path.normpath(event.src_path.replace(self._syncDir, ''))
        # First, check if the path exists
        if os.path.exists(path):
            if serverPath not in self.parent.parent.ignoreFiles:
                if not event.is_directory:
                    modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0) - self._timeoffset
                    try:
                        checksum = common.getFileHash(path)
                    except:
                        checksum = None
                    size = int(os.path.getsize(path))
                    isDir = os.path.isdir(path)
                    localfile = LocalFile(serverPath, path, checksum, None, modified, size, isDir)

                    if self._synchronizer.syncLoaded:
                        self._synchronizer.syncUpQueue.put(localfile)
                    else:
                        self._synchronizer.uploadQueue.put(localfile)
                """
                else:
                    try:
                        self.parent.smartfile.post('/path/oper/mkdir/', path=serverPath)
                    except:
                        raise
                """
            else:
                self.parent.parent.ignoreFiles.remove(serverPath)

    def modifiedOnce(self, path):
        """
        This is a hack to workaround a bug in watchdog.
        When a file is modified, watchdog calls on_modified twice instead of
        only once. This method keeps track of both events and returns true
        if the event has been previously called
        """
        if path in self.__modifiedFix:
            self.__modifiedFix.remove(path)
            return True
        else:
            self.__modifiedFix.append(path)
            return False
