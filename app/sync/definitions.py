import datetime
import os

import fs

import common
from syncobject import SyncObject


class FileDefinition(SyncObject):
    def __init__(self, path, checksum=None, modified=None, size=None,
            isDir=None):
        SyncObject.__init__(self)
        self.__path = path
        self.system_path = self.syncFS.getsyspath(path).strip("\\\\?\\")
        self.checksum = checksum
        self.modified = modified
        self.size = size
        self.isDir = isDir

    @property
    def path(self):
        """ Return the path relative to the sync directory. """
        path = fs.path.normpath(self.__path.replace(self.syncDir, ''))
        return path

    @path.setter
    def path(self, new_path):
        """ Change the path of the file. """
        self.__path = fs.path.normpath(new_path.replace(self.syncDir, ''))

    def generate_properties(self):
        """ Generate event properties for local files. """
        syncFS = self.syncFS

        self.path = self.path()
        self.checksum = self._gen_checksum()
        self.modified = self._gen_modified()
        self.size = int(syncFS(self.path))
        self.isDir = syncFS.isdir(self.path)

    def _gen_checksum(self):
        """ Generate a proper checksum. """
        syncFS = self.syncFS
        system_path = syncFS.getsyspath(self.path).strip("\\\\?\\")
        try:
            checksum = common.getFileHash(system_path)
        except:
            # the file may not be available yet
            checksum = None
        return checksum

    def _gen_modified(self):
        """ Generate a proper modified timestamp. """
        syncFS = self.syncFS
        system_path = syncFS.getsyspath(self.path).strip("\\\\?\\")

        modified = os.path.getmtime(system_path)
        timestamp = datetime.datetime.fromtimestamp(modified).replace(microsecond=0)
        # the local time may vary from the server, so subtract the offset
        shifted_timestamp = timestamp - self.timeOffset
        return shifted_timestamp
