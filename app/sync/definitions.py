from datetime import datetime
import os

import common


class FileDefinition(object):
    def __init__(self, path, checksum=None, modified=None,
            size=None, is_dir=None):
        self.path = path
        self.checksum = checksum
        self.modified = modified
        self.size = size
        self.is_dir = is_dir


class LocalDefinitionHelper(object):
    """ Helper to create local FileDefinition objects. """
    def __init__(self, path, sync_fs):
        self.path = path
        self.sync_fs = sync_fs

        self.system_path = self.sync_fs.getsyspath(path).strip("\\\\?\\")

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
        is_dir = os.path.isdir(self.system_path)

        self.path = self.normalize_path(self.path)

        return FileDefinition(path=self.path, checksum=checksum,
                              modified=modified, size=size, is_dir=is_dir)

    def normalize_path(self, path):
        path = path.replace('\\', '/')
        if not path.startswith("/"):
            path = os.path.join("/", 'path')

        return path
