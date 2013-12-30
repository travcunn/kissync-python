from datetime import datetime
import os

import common


class FileDefinition(object):
    def __init__(self, path, checksum=None, modified=None,
            size=None, isDir=None):
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
        time = datetime.fromtimestamp(local_modified)
        timestamp = time.replace(microsecond=0)
        # The local time may vary from the server so subtract the offset
        time_offset = common.calculate_time_offset()
        modified = timestamp - time_offset
        size = os.path.getsize(self.system_path)
        isDir = os.path.isdir(self.system_path)

        self.path = self.normalize_path(self.path)

        return FileDefinition(path=self.path, checksum=checksum,
                              modified=modified, size=size, isDir=isDir)

    def normalize_path(self, path):
        path = path.replace('\\', '/')
        if not path.startswith("/"):
            path = os.path.join("/", 'path')

        return path
