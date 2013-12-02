import datetime


class BaseEvent(object):
    def __init__(self, path):
        self.path = path
        self.__timestamp = datetime.datetime.now()

    @property
    def timestamp(self):
        """ Return a timestamp of when the event was created. """
        return self.__timestamp

    def __hash__(self):
        return hash(self.__class__.__name__)


class LocalMovedEvent(BaseEvent):
    def __init__(self, src, path):
        BaseEvent.__init__(self, path)
        self._src = src

    @property
    def src(self):
        return self._src


class LocalCreatedEvent(BaseEvent):
    def __init__(self, path, isDir):
        BaseEvent.__init__(self, path)
        self._isDir = isDir

    @property
    def isDir(self):
        return self._isDir


class LocalDeletedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)


class LocalModifiedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)


class RemoteMovedEvent(BaseEvent):
    def __init__(self, src, path):
        BaseEvent.__init__(self, path)
        self._src = src

    @property
    def src(self):
        return self._src


class RemoteCreatedEvent(BaseEvent):
    def __init__(self, path, isDir):
        BaseEvent.__init__(self, path)
        self._isDir = isDir

    @property
    def isDir(self):
        return self._isDir


class RemoteDeletedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)


class RemoteModifiedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)
