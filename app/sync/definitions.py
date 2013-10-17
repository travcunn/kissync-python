class RemoteFile():
    def __init__(self, path, checksum, modified, size, isDir):
        self.path = path
        self.checksum = checksum
        self.modified = modified
        self.size = size
        self.isDir = isDir


class LocalFile():
    def __init__(self, path, system_path, checksum, modified, modified_local, size, isDir):
        self.path = path
        self.system_path = system_path
        self.checksum = checksum
        self.modified = modified
        self.modified_local = modified_local
        self.size = size
        self.isDir = isDir
