import datetime
import hashlib
import os


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
                    filehash = self.__hashFile(discoveredFilePath)
                    modifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(discoveredFilePath))
                    #Add file to dictionary. filename:ksjdfoi23lkx983n2lj9x823jl
                    self.localFilesDictionary[discoveredFilePath.replace(syncdirPath, '')] = filehash
                    #Add file to dictionary with time. filename: timestamp
                    self.localFilesDictionaryTime[discoveredFilePath.replace(syncdirPath, '')] = modifiedTime
        except:
            raise

    def __hashFile(self, filepath):
        fileToHash = open(filepath)
        md5 = hashlib.md5()
        while(True):
            currentLine = fileToHash.readline()
            if not currentLine:
                break
            md5.update(currentLine)
        return md5.hexdigest()
