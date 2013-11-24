import datetime


class BaseEvent(object):
    def __init__(self, path):
        self.path = path
        self.__timestamp = datetime.datetime.now()

    @property
    def timestamp(self):
        """ Return a timestamp of when the event was created. """
        return self.__timestamp


class LocalMovedEvent(BaseEvent):
    def __init__(self, path, src):
        BaseEvent.__init__(self, path)
        self.__src = src

    @property
    def src(self):
        return self.__src


class LocalCreatedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)


class LocalDeletedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)


class LocalModifiedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)


class RemoteMovedEvent(BaseEvent):
    def __init__(self, path, src):
        BaseEvent.__init__(self, path)
        self.__src = src

    @property
    def src(self):
        return self.__src


class RemoteCreatedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)


class RemoteDeletedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)


class RemoteModifiedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)
