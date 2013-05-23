import datetime
import hashlib
import os


class FileDatabase(object):
    def __init__(self, parent=None):
        object.__init__(self)
        self.parent = parent

        '''
        Dictionaries used for comparison
        Format:
            filename:(hash, modified time)
        '''
        self.localFiles = {}
        self.remoteFiles = {}

    def indexLocalFiles(self):
        '''
        Indexes the local files and populates the self.localFiles dictionary
        '''
        try:
            syncdirPath = self.parent.configuration.get('LocalSettings', 'sync-dir')
            for (paths, dirs, files) in os.walk(syncdirPath):
                for item in files:
                    discoveredFilePath = os.path.join(paths, item)
                    filehash = self.__getFileHash(discoveredFilePath)
                    modifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(discoveredFilePath))
                    #Add file to dictionary. filename:(hash, modified time)
                    self.localFilesDictionary[discoveredFilePath.replace(syncdirPath, '')] = filehash, modifiedTime
        except:
            raise

    def getFileHash(self, filepath):
        '''
        '''
        fileToHash = open(filepath)
        md5 = hashlib.md5()
        while(True):
            currentLine = fileToHash.readline()
            if not currentLine:
                break
            md5.update(currentLine)
        return md5.hexdigest()
