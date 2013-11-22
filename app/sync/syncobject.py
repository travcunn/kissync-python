import os

from fs.osfs import OSFS

import common


class SyncObject(object):
    """ Inherit this for any object that performs synchronization """
    def __init__(self):
        self._timeOffset = common.calculate_time_offset()
        self._syncDir = os.path.join(os.path.expanduser("~"), "Smartfile")

        self.syncFS = OSFS(self._syncDir)

    @property
    def syncDir(self):
        """ Get the sync directory """
        return self._syncDir

    @property
    def timeOffset(self):
        """ Get the time offset to use in time calculations """
        return self._timeOffset
