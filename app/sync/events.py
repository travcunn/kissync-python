import datetime

from definitions import FileDefinition
from syncobject import SyncObject


class BaseEvent(SyncObject):
    def __init__(self, path):
        SyncObject.__init__(self)
        self.properties = FileDefinition(path)
        self.__timestamp = datetime.datetime.now()

    @property
    def timestamp(self):
        """ Return a timestamp of when the event was created. """
        return self.__timestamp

    def generate_properties(self):
        self.properties.generate_properties()


class LocalMovedEvent(BaseEvent):
    def __init__(self, path, src):
        BaseEvent.__init__(self, path)
        self.__src = src

        self.generate_properties()

    @property
    def src(self):
        return self.__src


class LocalCreatedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)

        self.generate_properties()


class LocalDeletedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)


class LocalModifiedEvent(BaseEvent):
    def __init__(self, path):
        BaseEvent.__init__(self, path)

        self.generate_properties()


class RemoteMovedEvent(BaseEvent):
    def __init__(self, path, src):
        BaseEvent.__init__(self, path)
        self.__src = src

    @property
    def source(self):
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
