from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Boolean, BigInteger, Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class RemoteFile(Base):
    __tablename__ = "remotefiles"

    id = Column(Integer, primary_key=True)
    path = Column(String)
    checksum = Column(String)
    modified = Column(Date)
    size = Column(BigInteger)
    isDir = Column(Boolean)

    def __init__(self, path, checksum, modified, size, isDir):
        self.path = path
        self.checksum = checksum
        self.modified = modified
        self.size = size
        self.isDir = isDir


class LocalFile(Base):
    __tablename__ = "localfiles"

    id = Column(Integer, primary_key=True)
    path = Column(String)
    checksum = Column(String)
    modified = Column(Date)
    modified_local = Column(Date)
    size = Column(BigInteger)
    isDir = Column(Boolean)

    def __init__(self, path, checksum, modified, modified_local, size, isDir):
        self.path = path
        self.checksum = checksum
        self.modified = modified
        self.modified_local = modified_local
        self.size = size
        self.isDir = isDir
