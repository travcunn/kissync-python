import datetime
import os

import common
from syncobject import SyncObject


class FileDefinition(SyncObject):
    def __init__(self, path, checksum=None, modified=None,
            size=None, isDir=None, isLocal=False):
        self.path = path
        self.checksum = checksum
        self.modified = modified
        self.size = size
        self.isDir = isDir


class LocalDefinitionHelper(object):
    """ Helper to create local FileDefinition objects. """
    def __init__(self, path, syncFS):
        self.path = path
        self.syncFS = syncFS

        self.system_path = self.syncFS.getsyspath(path).strip("\\\\?\\")

    def create_definition(self):
        try:
            checksum = common.getFileHash(self.system_path)
        except:
            # The file may not be available yet
            checksum = None
        local_modified = os.path.getmtime(self.system_path)
        timestamp = datetime.datetime.fromtimestamp(local_modified).replace(microsecond=0)
        # The local time may vary from the server so subtract the offset
        time_offset = common.calculate_time_offset()
        modified = timestamp - time_offset
        size = os.path.getsize(self.system_path)
        isDir = os.path.isdir(self.system_path)

        return FileDefinition(path=self.path, checksum=checksum,
                              modified=modified, size=size, isDir=isDir)
