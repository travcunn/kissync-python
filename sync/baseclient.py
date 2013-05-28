import errno
import os


class BaseClient(object):
    def __init__(self):
        object.__init__(self)

    def basePath(self, path):
        '''
        Returns the path of files in the sync folder
        without the leading system folder separation
        '''
        if path.startswith("/"):
            path = path.replace("/", "", 1)
        elif path.startswith("\\"):
            path = path.replace("\\", "", 1)
        return path

    def createLocalDirs(self, path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
