import errno
import hashlib
import os


def basePath(path):
    """
    Returns the path of files in the sync folder
    without the leading system folder separation
    """
    if path.startswith("/"):
        path = path.replace("/", "", 1)
    if path.startswith("\\"):
        path = path.replace("\\", "", 1)
    return path


def createLocalDirs(path):
    """Tries to create local directories"""
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def getFileHash(filepath):
    """
    Returns the MD5 hash of a local file
    """
    fileToHash = open(filepath)
    md5 = hashlib.md5()
    while True:
        currentLine = fileToHash.readline()
        if not currentLine:
            break
        md5.update(currentLine)
    return md5.hexdigest()
