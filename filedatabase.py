import datetime
import hashlib
import os
import errno
import Queue
import shutil
import threading


class FileDatabase(object):
    def __init__(self, parent=None):
        object.__init__(self)
        self.parent = parent

        self.remoteFilesDictionary = {}
        self.remoteFilesDictionaryTime = {}
        self.localFilesDictionary = {}
        self.localFilesDictionaryTime = {}

    def indexLocalFiles(self):
        try:
            syncdirPath = self.parent.configuration.get('LocalSettings', 'sync-dir')
            self.localFilesDictionary = {}
            for (paths, dirs, files) in os.walk(syncdirPath):
                for item in files:
                    discoveredFilePath = os.path.join(paths, item)
                    filehash = self.hashFile(discoveredFilePath)
                    modifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(discoveredFilePath))
                    #Add file to dictionary. filename:ksjdfoi23lkx983n2lj9x823jl
                    self.localFilesDictionary[discoveredFilePath.replace(syncdirPath, '')] = filehash
                    #Add file to dictionary with time. filename: timestamp
                    self.localFilesDictionaryTime[discoveredFilePath.replace(syncdirPath, '')] = modifiedTime
        except:
            raise

    def hashFile(self, filepath):
        fileToHash = open(filepath)
        md5 = hashlib.md5()
        while(True):
            currentLine = fileToHash.readline()
            if not currentLine:
                break
            md5.update(currentLine)
        return md5.hexdigest()


class Synchronizer(object):
    def __init__(self, parent=None):
        object.__init__(self)
        self.parent = parent

        self.downloadQueue = Queue.Queue()
        self.uploadQueue = Queue.Queue()
        self.checkChangesQueue = Queue.Queue()

    def start(self):
        self.dictDiffer = DictDiffer(self.parent.database.remoteFilesDictionary, self.parent.database.localFilesDictionary)

        for i in self.dictDiffer.added():
            self.downloadQueue.put(i)

        for i in self.dictDiffer.removed():
            self.uploadQueue.put(i)

        for i in self.dictDiffer.changed():
            self.checkChangesQueue.put(i)

        comparethread = CheckChanges(self, self.checkChangesQueue)
        comparethread.setDaemon(True)
        comparethread.start()

        downthread = Downloader(self, self.downloadQueue)
        downthread.setDaemon(True)
        downthread.start()

        upthread = Uploader(self, self.uploadQueue)
        upthread.setDaemon(True)
        upthread.start()

        self.checkChangesQueue.join()
        self.downloadQueue.join()
        self.uploadQueue.join()

        self.parent.database.loadRemoteListingFile()
        self.parent.database.generateRemoteListing()

        self.parent.filewatcher.start()


class CheckChanges(threading.Thread):

    def __init__(self, parent, queue):
        threading.Thread.__init__(self)
        self.parent = parent
        self.queue = queue

    def run(self):
        while True:
            path = self.queue.get()
            self.checkFile(path)
            self.queue.task_done()

    def checkFile(self, filepath):
        if(self.parent.parent.database.remoteFilesDictionaryTime[filepath] > self.parent.parent.database.localFilesDictionaryTime[filepath]):
            #print "Newer on the server: " + filepath
            pass
        elif(self.parent.parent.database.remoteFilesDictionaryTime[filepath] < self.parent.parent.database.localFilesDictionaryTime[filepath]):
            #print "Newer on the client: " + filepath
            pass
        else:
            #print "Equal on server and client: " + filepath
            pass


class Downloader(threading.Thread):
    def __init__(self, parent, queue):
        threading.Thread.__init__(self)
        self.parent = parent
        self.queue = queue

    def run(self):
        while True:
            path = self.queue.get()
            self.downloadFile(path)
            self.queue.task_done()

    def downloadFile(self, filepath):
        absolutePath = os.path.join(self.parent.parent.configuration.get('LocalSettings', 'sync-dir'), filepath)
        self.checkDirsToCreate(absolutePath)
        try:
            f = self.parent.parent.smartfile.get('/path/data/', filepath)
            with file(absolutePath, 'wb') as o:
                shutil.copyfileobj(f, o)
        except:
            raise

    def checkDirsToCreate(self, path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


class Uploader(threading.Thread):
    def __init__(self, parent, queue):
        threading.Thread.__init__(self)
        self.parent = parent
        self.queue = queue
        self.syncdirPath = self.parent.parent.configuration.get('LocalSettings', 'sync-dir')

    def run(self):
        while True:
            path = self.queue.get()
            self.uploadFile(path)
            self.queue.task_done()

    def uploadFile(self, filepath):
        filepath = self.syncdirPath + filepath
        if not (os.path.isdir(filepath)):
            #Todo: Upload the files here
            pass
        else:
            self.parent.parent.smartfile.post('/path/oper/mkdir/', filepath.replace(self.syncdirPath, ''))


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [set(d.keys()) for d in (current_dict, past_dict)]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        return self.current_keys - self.intersect

    def removed(self):
        return self.past_keys - self.intersect

    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])
