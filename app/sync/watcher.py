import datetime
import os
import threading
import time

import fs.path
from fs.osfs import OSFS

from watchdog.observers import Observer
#from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

import common
from definitions import LocalFile


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

        # This helps the modifiedFix hack
        self.__modifiedFix = []

    def on_moved(self, event):
        print "destination path:::::::", event.dest_path
        print "Item Moved:", event.src_path, event.dest_path
        serverPath = fs.path.normpath(event.src_path.replace(self._syncDir, ''))
        serverPathNew = fs.path.normpath(event.dest_path.replace(self._syncDir, ''))
        #serverPathNew = self._syncFS.unsyspath(event.dest_path.replace(self._syncDir, '')).strip("\\\\?\\")
        print "Old Server Path:", serverPath
        print "New Server Path:", serverPathNew

        try:
            #TODO: This doenst work
            # According to the logs, /cloud.png gets moved to
            # /logo.png/cloud.png, where instead it should be moved to
            # /logo.png.
            # post created: http://smartfile.forumbee.com/t/19b28
            self._api.post('/path/oper/move/', src=serverPath, dst=serverPathNew)
        except:
            raise

    def on_created(self, event):
        path = event.src_path
        print "item created:", path
        serverPath = fs.path.normpath(event.src_path.replace(self._syncDir, ''))
        if not event.is_directory:
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0) - self._timeoffset
            checksum = common.getFileHash(path)
            size = int(os.path.getsize(path))
            isDir = os.path.isdir(path)
            localfile = LocalFile(serverPath, path, checksum, None, modified, size, isDir)

            self._synchronizer.uploadQueue.put(localfile)
        else:
            try:
                self._api.post('/path/oper/mkdir/', path=serverPath)
            except:
                raise

    def on_deleted(self, event):
        print "item deleted:", event.src_path
        serverPath = fs.path.normpath(event.src_path.replace(self._syncDir, ''))
        try:
            self._api.post('/path/oper/remove/', path=serverPath)
        except:
            raise

    def on_modified(self, event):
        path = event.src_path
        if self.modifiedOnce(path):
            print "item modified:", path
            serverPath = fs.path.normpath(event.src_path.replace(self._syncDir, ''))
            print "server path modified:", serverPath
            if not event.is_directory:
                print "its not a directory"
                modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0) - self._timeoffset
                checksum = common.getFileHash(path)
                size = int(os.path.getsize(path))
                isDir = os.path.isdir(path)
                localfile = LocalFile(serverPath, path, checksum, None, modified, size, isDir)

                print "okay lets sync it"

                if self._synchronizer.syncLoaded:
                    self._synchronizer.syncUpQueue.put(localfile)
                    print "It was put in the sync up queue"
                else:
                    self._synchronizer.uploadQueue.put(localfile)
                    print "it was put up in the upload queue"
            """
            else:
                try:
                    self.parent.smartfile.post('/path/oper/mkdir/', path=serverPath)
                except:
                    raise
            """

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
