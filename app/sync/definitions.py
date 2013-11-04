import common


class File(object):
    def __init__(self, path, checksum, modified, size, isDir):
        self.path = path
        self.system_path = common.basePath(path)
        self.checksum = checksum
        self.modified = modified
        self.size = size
        self.isDir = isDir
