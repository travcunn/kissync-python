import logging
import os
import threading
import time

import fs.path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import events


log = logging.getLogger(__name__)


class Watcher(threading.Thread):
    def __init__(self, sync_dir, moved_callback=None, created_callback=None,
                 deleted_callback=None, modified_callback=None):
        self.sync_dir = sync_dir

        self.event_handler = EventHandler(sync_dir=sync_dir,
                moved_callback=moved_callback,
                created_callback=created_callback,
                deleted_callback=deleted_callback,
                modified_callback=modified_callback)

        super(Watcher, self).__init__()

    def run(self):
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.sync_dir,
                               recursive=True)
        log.debug("Starting the local filesystem watcher.")
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()


class EventHandler(FileSystemEventHandler):
    def __init__(self, sync_dir, moved_callback=None, created_callback=None,
                 deleted_callback=None, modified_callback=None):
        self.sync_dir = sync_dir

        self.moved_callback = moved_callback
        self.created_callback = created_callback
        self.deleted_callback = deleted_callback
        self.modified_callback = modified_callback

    def on_moved(self, event):
        log.info("Local file was moved. src_path=" + event.src_path +
                ", dest_path=" + event.dest_path)
        src_path = fs.path.normpath(event.src_path.replace(self.sync_dir, ''))
        dest_path = fs.path.normpath(event.dest_path.replace(self.sync_dir,
                                                             ''))
        # Check if the path exists
        if os.path.exists(event.dest_path):
            if self.moved_callback is not None:
                log.debug("Sending a LocalMovedEvent to the callback.")
                moved_event = events.LocalMovedEvent(src_path, dest_path)
                self.moved_callback(moved_event)

    def on_created(self, event):
        log.info("Local file was created. src_path=" + event.src_path)
        src_path = fs.path.normpath(event.src_path.replace(self.sync_dir, ''))

        # Check if the path exists
        if os.path.exists(event.src_path):
            isDir = event.is_directory
            created_event = events.LocalCreatedEvent(src_path, isDir=isDir)

            if self.created_callback is not None:
                log.debug("Sending a LocalCreatedEvent to the callback.")
                self.created_callback(created_event)

    def on_deleted(self, event):
        log.info("Local file was deleted. src_path=" + event.src_path)
        src_path = fs.path.normpath(event.src_path.replace(self.sync_dir, ''))

        deleted_event = events.LocalDeletedEvent(src_path)

        if self.deleted_callback is not None:
            log.debug("Sending a LocalDeletedEvent to the callback.")
            self.deleted_callback(deleted_event)

    def on_modified(self, event):
        log.info("Local file was modified. src_path=" + event.src_path)
        src_path = fs.path.normpath(event.src_path.replace(self.sync_dir, ''))

        # Check if the path exists
        if os.path.exists(event.src_path) and not event.is_directory:
            modified_event = events.LocalModifiedEvent(src_path)

            if self.created_callback is not None:
                log.debug("Sending a LocalModifiedEvent to the callback.")
                self.modified_callback(modified_event)
