import datetime
import os
import threading
import time

import fs.path
from fs.osfs import OSFS

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import common
from definitions import File
import history
from realtime import RealtimeSync


def checkPath():
    """ Ignore certain types of files """
    def _decorating_wrapper(func):
        def _wrapper(*args, **kwargs):
            path = args[1].src_path
            # Ignore temp files and repositories
            try:
                if not path.endswith("~"):
                    folder_list = path.split(os.sep)
                    for folder in folder_list:
                        if folder.startswith(".svn") or folder.startswith(".git"):
                            return
                    return func(*args, **kwargs)
            except:
                return
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

    @checkPath()
    def on_moved(self, event):
        serverPath = fs.path.normpath(event.src_path.replace(self._syncDir, ''))
        serverPathNew = fs.path.normpath(event.dest_path.replace(self._syncDir, ''))

        # First, check if the path exists
        if os.path.exists(event.dest_path):
            isDir = os.path.isdir(event.dest_path)
            if serverPath not in self.parent.parent.ignoreFiles and serverPathNew not in self.parent.parent.ignoreFiles:
                try:
                    # Delete the file from SmartFile
                    self._api.post('/path/oper/remove/', path=serverPath)

                    # Prepare some data for the file object
                    modified = datetime.datetime.fromtimestamp(os.path.getmtime(event.dest_path)).replace(microsecond=0) - self._timeoffset
                    try:
                        checksum = common.getFileHash(event.dest_path)
                    except:
                        checksum = None
                    size = int(os.path.getsize(event.dest_path))
                    isDir = os.path.isdir(event.dest_path)

                    # Create the file object to send to the queue
                    localfile = File(serverPathNew, checksum, modified, size, isDir)

                    self._synchronizer.uploadQueue.put(localfile)
                    history.fileMoved(event.src_path)

                    # Notify the realtime sync of the change
                    self.parent.realtime.update(serverPath, 'moved', 0, isDir, serverPathNew)
                except:
                    pass
            else:
                self.parent.parent.ignoreFiles.remove(serverPath)
                self.parent.parent.ignoreFiles.remove(serverPathNew)

    #### The Move API is broken, but when it is fixed, uncomment this
    """
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
                    print self._api.post('/path/oper/move/', src=serverPath, dst=serverPathNew)
                    history.fileMoved(event.src_path)
                    # Notify the realtime sync of the change
                    self.parent.realtime.update(serverPath, 'moved', 0, isDir, serverPathNew)
                except:
                    pass
            else:
                self.parent.parent.ignoreFiles.remove(serverPath)
                self.parent.parent.ignoreFiles.remove(serverPathNew)
    """

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

                    localfile = File(serverPath, checksum, modified, size, isDir)

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

                    localfile = File(serverPath, checksum, modified, size, isDir)

                    self._synchronizer.uploadQueue.put(localfile)
            else:
                self.parent.parent.ignoreFiles.remove(serverPath)
