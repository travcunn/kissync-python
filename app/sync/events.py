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
        self._src = src
        super(LocalMovedEvent, self).__init__(path)

    @property
    def src(self):
        return self._src


class LocalCreatedEvent(BaseEvent):
    def __init__(self, path, isDir):
        self._isDir = isDir
        super(LocalCreatedEvent, self).__init__(path)

    @property
    def isDir(self):
        return self._isDir


class LocalDeletedEvent(BaseEvent):
    def __init__(self, path, isDir=False):
        self._isDir = isDir
        super(LocalDeletedEvent, self).__init__(path)

    @property
    def isDir(self):
        return self._isDir


class LocalModifiedEvent(BaseEvent):
    def __init__(self, path):
        super(LocalModifiedEvent, self).__init__(path)


class RemoteMovedEvent(BaseEvent):
    def __init__(self, src, path):
        self._src = src
        super(RemoteMovedEvent, self).__init__(path)

    @property
    def src(self):
        return self._src


class RemoteCreatedEvent(BaseEvent):
    def __init__(self, path, isDir):
        self._isDir = isDir
        super(RemoteCreatedEvent, self).__init__(path)

    @property
    def isDir(self):
        return self._isDir


class RemoteDeletedEvent(BaseEvent):
    def __init__(self, path, isDir=False):
        self._isDir = isDir
        super(RemoteDeletedEvent, self).__init__(path)

    @property
    def isDir(self):
        return self._isDir


class RemoteModifiedEvent(BaseEvent):
    def __init__(self, path):
        super(RemoteModifiedEvent, self).__init__(path)
