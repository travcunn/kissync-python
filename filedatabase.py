from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
import datetime, hashlib, os, platform, sqlite3, sys, time


class FileDatabase(object):
	def __init__(self, parent = None):
		object.__init__(self)
		self.parent = parent
		self.remoteFilesList = []
		
		self.remoteFilesDictionary = {}
		self.localFilesDictionary = {}
	
	def indexLocalFiles(self):
		syncdirPath = self.parent.config.get('LocalSettings', 'sync-dir')
		print "[database]: Local Database: Indexing local files..."
		##we must clear the existing table if there is request to index the files
		self.localFilesDictionary = {}
		for (paths, folders, files) in os.walk(syncdirPath):
			for item in files:
				discoveredFilePath = os.path.join(paths,item)
				filehash = self.hashFile(discoveredFilePath)
				self.localFilesDictionary[discoveredFilePath.replace(syncdirPath,'')] = filehash
				print  "[database-indexer]: %s %s" % (discoveredFilePath.replace(syncdirPath,''), filehash)
		print "[database]: Local Database: Done indexing local files..."
		
	def indexRemoteFiles(self, path):
		#this might take some time, as we are creating a 'task' on their server for MD5 hashing
		tree = self.parent.smartfile.get('/path/info' + path, children = True)
		if 'children' not in tree:
			return []
		for i in tree['children']:
			if i['isdir']:
				self.indexRemoteFiles(i['path'])
			else:
				try:
					print i['path']
					self.remoteFilesDictionary[i['path']] = self.hashtask(i['path'])
				except:
					self.indexRemoteFiles("/")
	
	def hashtask(self, filepath):
		try:
			self.parent.smartfile.post("/path/oper/checksum", path=(filepath,), algorithm='MD5')
		except:
			pass
		
		while True:
			s = self.parent.smartfile.get('/task')
			for i in s:
				results = i['result']['result']
				if 'checksums' in results:
					fileAndHash =  i['result']['result']['checksums']
					if filepath in fileAndHash:
						return i['result']['result']['checksums'][filepath]
			
	
	def hashFile(self, filepath):
	##Read files line by line instead of all at once (allows for large files to be hashes)
	##For each line in the file, update the hash, then when it reaches the end of the 
		fileToHash = open(filepath)
		md5 = hashlib.md5()
		while(True):
			currentLine = fileToHash.readline()
			if not currentLine:
				#when readline() returns false, it is at the end of the file, so break the loop
				break
			md5.update(currentLine)
		return md5.hexdigest()


class Synchronizer(object):
	def __init__(self, parent = None):
		object.__init__(self)
		self.parent = parent
		self.dictDiffer = DictDiffer(self.parent.database.remoteFilesDictionary, self.parent.database.localFilesDictionary)
	
	def start(self):
		#Compare what files server has against local files
		print "Compare what files server has against local files:"
		print self.dictDiffer.added()
		

class QueueManager(object):
	def __init__(self, parent = None):
		object.__init__(self)
		self.parent = parent
		self.downloadQueue = []
		self.uploadQueue = []



"""
A dictionary difference calculator
Originally posted as:
http://stackoverflow.com/questions/1165352/fast-comparison-between-two-python-dictionary/1165552#1165552
"""

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
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (current_dict, past_dict)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        return self.current_keys - self.intersect

    def removed(self):
        return self.past_keys - self.intersect

    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])
