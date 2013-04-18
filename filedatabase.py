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
				self.remoteFilesList.append(i['path'])
				try:
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

