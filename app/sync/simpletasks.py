import logging
import os
import shutil
import threading

from fs.osfs import OSFS
from smartfile.errors import ResponseError

import common
import events
from worker import Worker


log = logging.getLogger(__name__)


class SimpleTask(Worker):
    def __init__(self, api, sync_dir):
        self._api = api
        self._sync_dir = sync_dir
        self._timeoffset = common.calculate_time_offset()
        self._syncFS = OSFS(sync_dir)

    def _process_task(self, task):
        # Create a system specific path relative to the sync dir
        basepath = os.path.normpath(task.path)
        if basepath.startswith("/"):
            basepath = basepath.strip("/")
        if basepath.startswith('\\'):
            basepath = basepath.lstrip('\\')
        # Full system path
        absolute_path = os.path.join(self._sync_dir, basepath)

        # The task is a remote deleted event
        if isinstance(task, events.RemoteDeletedEvent):
            self.deleteLocal(absolute_path)

        # The task is a remote moved event
        elif isinstance(task, events.RemoteMovedEvent):
            # Create a system specific src path relative to the sync dir
            src_path = os.path.normpath(task.src)
            if src_path.startswith("/"):
                src_path = src_path.strip("/")
            if src_path.startswith('\\'):
                src_path = src_path.lstrip('\\')
            # Full src system path
            absolute_src_path = os.path.join(self._sync_dir, src_path)

            self.moveLocal(absolute_src_path, absolute_path)

        # The task is a local deleted event
        elif isinstance(task, events.LocalDeletedEvent):
            self.deleteRemote(task.path)

        # The task is a local moved event
        elif isinstance(task, events.LocalMovedEvent):
            self.moveRemote(task.src, task.path)

        return task

    def moveLocal(self, src, dest):
        """ Moves a local path, given system paths. """
        try:
            # try creating directories for the destination
            dir = os.path.dirname(dest)
            os.makedirs(dir)
        except OSError:
            # The folder already exists.
            pass
        # move the file or folder
        os.rename(src, dest)

    def moveRemote(self, src, dest):
        """
        Moves a remote path, given a path relative to the sync directory.
        """
        #TODO: test this
        try:
            self._api.post('/path/oper/rename', src=src, dst=dest)
        except ResponseError, err:
            # ignore 404 errors, as the containing folder was probably moved
            if err.status_code == 404:
                pass

    def deleteLocal(self, path):
        """ Deletes a local path, given a system path. """
        # such delete, much wow
        try:
            os.remove(path)
        except:
            pass
        try:
            shutil.rmtree(path)
        except:
            pass
        try:
            os.rmdir(path)
        except:
            pass

    def deleteRemote(self, path):
        """
        Deletes a remote path, given a path relative to the sync directory.
        """
        #TODO: add some error handling (404, etc...)
        self._api.post('/path/oper/remove', path=path)


class SimpleTaskWorker(threading.Thread):
    def __init__(self, queue, api, sync_dir, remote_files, realtime=False):
        threading.Thread.__init__(self)
        self._simpletask = SimpleTask(api, sync_dir)
        self._queue = queue
        self._remote_files = remote_files

        self._realtime = realtime

    def run(self):
        while True:
            log.debug("Getting a new task.")
            self._current_task = None
            self._current_task = self._queue.get()
            try:
                log.debug("Processing: " + self._current_task.path)
                result = self._simpletask.process_task(self._current_task)
                # Update the remote files dictionary to reflect the new file
                self._remote_files[result.path] = result
            except:
                raise
            else:
                # Notify the realtime messaging system of the simple task
                if self._realtime:
                    self._realtime.update(self._current_task)
            log.debug("Task complete.")
            self._queue.task_done()

    def try_task_later(self):
        self._queue.put(self._current_task)

    def cancel(self):
        log.debug("Task cancelled: " + self._current_task.path)
        self._simpletask.cancel_task()

    @property
    def current_task(self):
        return self._current_task
