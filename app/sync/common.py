import datetime
from dateutil.parser import parse
import errno
import hashlib
import os
import requests


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


def get_server_time():
    """
    Returns the time of the SmartFile servers
    """
    response = requests.get('https://www.smartfile.com')
    time = parse(response.headers['Date']).replace(tzinfo=None, second=0)
    return time


def calculate_time_offset():
    """
    Calculates a time offset, duh!
    This should be tested more. If the offset calculation is incorrect,
    unchanged files will be put into sync up/down queues, and since a sync up
    on a file that has not been changed will cause corruption.
    """
    server_time = get_server_time()
    now = datetime.datetime.now().replace(microsecond=0, second=0)
    offset = now - server_time
    return offset
