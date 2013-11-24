import os

from fs.osfs import OSFS

import common


class SyncObject(object):
    """ Inherit this for any object that performs synchronization. """
    def __init__(self, path=None):
        self._timeOffset = common.calculate_time_offset()
        # TODO: objects that inherit this will default to the first option
        if path is None:
            self._syncDir = os.path.join(os.path.expanduser("~"), "Smartfile")
        else:
            self._syncDir = path

        self._checkSyncDir()
        self.syncFS = OSFS(self._syncDir)

    @property
    def syncDir(self):
        """ Get the sync directory. """
        return self._syncDir

    @property
    def timeOffset(self):
        """ Get the time offset to use in time calculations. """
        return self._timeOffset

    def _checkSyncDir(self):
        """ Verify that the sync dir exists. """
        if not os.path.exists(self._syncDir):
            os.makedirs(self._syncDir)
