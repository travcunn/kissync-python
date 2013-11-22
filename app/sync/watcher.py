import datetime
import os
import re
import threading
import time

import fs.path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import common
from definitions import FileDefinition
import events


def checkPath():
    """ Ignore certain types of files and folders"""
    def _decorating_wrapper(func):
        def _wrapper(*args, **kwargs):
            path = args[1].src_path
            # Ignore temp files and repositories
            try:
                _default_startswith_filter = lambda x: not x.startswith(".")
                _default_endswith_filter = lambda x: not x.endswith("~")
                filters = [_default_startswith_filter, _default_endswith_filter]

                path_list = path.split(os.sep)
                for filename in path_list:
                    for _filter in filters:
                        if callable(_filter):
                            if not _filter(filename):
                                return
                        elif not re.search(_filter, filename, re.UNICODE):
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

    @checkPath()
    def on_moved(self, event):
        serverPath = fs.path.normpath(event.src_path.replace(self._syncDir, ''))
        serverPathNew = fs.path.normpath(event.dest_path.replace(self._syncDir, ''))

        # First, check if the path exists
        if os.path.exists(event.dest_path):
            isDir = os.path.isdir(event.dest_path)
            if serverPath not in self.parent.parent.ignoreFiles and serverPathNew not in self.parent.parent.ignoreFiles:
                try:
                    #TODO: allow the event handler to make this api call
                    # Delete the file from SmartFile
                    self._api.post('/path/oper/remove/', path=serverPath)

                    moveEvent = events.LocalMovedEvent(event.dest_path, event.src_path)

                    self._synchronizer.addEvent(moveEvent)

                    #TODO: allow the event handler to notify the realtime engine
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
                    createdEvent = events.LocalCreatedEvent(event.src_path)

                    self._synchronizer.addEvent(createdEvent)
                else:
                    try:
                        #TODO: convert this into an event in events.py
                        self._api.post('/path/oper/mkdir/', path=serverPath)
                    except:
                        pass
            else:
                self.parent.parent.ignoreFiles.remove(serverPath)

    @checkPath()
    def on_deleted(self, event):
        serverPath = fs.path.normpath(event.src_path.replace(self._syncDir, ''))

        deletedEvent = events.LocalDeletedEvent(event.src_path)
        self._synchronizer.addEvent(deletedEvent)

        if serverPath not in self.parent.parent.ignoreFiles:
            try:
                #TODO: allow the event handler to make this api call
                self._api.post('/path/oper/remove/', path=serverPath)
                #TODO: allow the event handler to notify the realtime engine
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

                modifiedEvent = events.LocalModifiedEvent(event.src_path)
                self._synchronizer.addEvent(modifiedEvent)

                if not event.is_directory:
                    modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0) - self._timeoffset
                    try:
                        checksum = common.getFileHash(path)
                    except:
                        checksum = None
                    size = int(os.path.getsize(path))
                    isDir = os.path.isdir(path)

                    localfile = FileDefinition(serverPath, checksum, modified, size, isDir)

                    self._synchronizer.uploadQueue.put(localfile)
            else:
                self.parent.parent.ignoreFiles.remove(serverPath)
