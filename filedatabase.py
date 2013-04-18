from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
import datetime, hashlib, os, platform, Queue, sys, time, threading


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
				self.localFilesDictionary[discoveredFilePath.replace(syncdirPath,'').encode('utf-8')] = filehash.encode('utf-8')
				print  "[database-indexer]: %s %s" % (discoveredFilePath.replace(syncdirPath,'').encode('utf-8'), filehash.encode('utf-8'))
		print "[database]: Local Database: Done indexing local files..."
		
	def indexRemoteFiles(self, path):
		#this might take some time, as we are creating a 'task' on their server for MD5 hashing
		tree = self.parent.smartfile.get('/path/info' + path, children = True)
		if 'children' not in tree:
			return []
		for i in tree['children']:
			if i['isdir']:
				self.indexRemoteFiles(i['path'].encode('utf-8'))
			else:
				try:
					self.remoteFilesDictionary[i['path'].encode('utf-8')] = self.hashtask(i['path'].encode('utf-8'))
				except:
					self.indexRemoteFiles("/")
	
	def hashtask(self, filepath):
		try:
			self.parent.smartfile.post("/path/oper/checksum", path=(filepath,), algorithm='MD5')
		except:
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
						return i['result']['result']['checksums'][filepath].encode('utf-8')
			
	
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
		
		self.filesToDownload = []
		self.filesToUpload = []
		
		self.downloadQueue = Queue.Queue()
		self.uploadQueue = Queue.Queue()
		
	def start(self):
		#Compare what files server has against local files
		#print self.parent.database.remoteFilesDictionary
		#print self.parent.database.localFilesDictionary
		#print "Compare what files server has against local files:"
		
		#files the server that client needs
		for i in self.dictDiffer.added():
			self.filesToDownload.append(i)
			self.downloadQueue.put(i)
			
		#files that are different on the server, that the client needs	
		for i in self.dictDiffer.changed():
			self.filesToDownload.append(i)
			self.downloadQueue.put(i)
		
		#local files that smartfile needs
		for i in self.dictDiffer.removed():
			self.filesToUpload.append(i)
			self.uploadQueue.put(i)
		
		
		print "Files to download:"
		print self.filesToDownload
		print "Files to upload:"
		print self.filesToUpload	
		"""
		downthread = Downloader(self, self.downloadQueue)
		downthread.setDaemon(True)
		downthread.start()
		
		upthread = Uploader(self, self.downloadQueue)
		upthread.setDaemon(True)
		upthread.start()
		"""
		
class Downloader(threading.Thread):
 
	def __init__(self, parent, queue):
		threading.Thread.__init__(self)
		self.parent = parent
		self.queue = queue
 
	def run(self):
		while True:
			path = self.queue.get()
			print path
			self.downloadFile(path)
			self.queue.task_done()
				
	def downloadFile(self, filepath):
		pathArray = filepath.split("/")
		pathArray.pop(0)
		pathArray.pop(len(pathArray) - 1)
		pathToAdd = ""
		#A BUG EXISTS IN THIS, PLEASE TEST THIS
		for directory in pathArray:
			if not os.path.exists(self.parent.parent.config.get('LocalSettings', 'sync-dir') + "/" + pathToAdd + directory):
				os.makedirs(self.parent.parent.config.get('LocalSettings', 'sync-dir') + "/" + pathToAdd + directory)
				pathToAdd = pathToAdd + directory + "/"
				#print pathToAdd
				
		f = self.parent.parent.smartfile.get('/path/data/', filepath)
		realPath = self.parent.parent.config.get('LocalSettings', 'sync-dir') + filepath
		realPath = realPath.encode("utf-8")
		with file(realPath, 'wb') as o:
			shutil.copyfileobj(f, o)
                
                
class Uploader(threading.Thread):
 
	def __init__(self, parent, queue):
		threading.Thread.__init__(self)
		self.parent = parent
		self.queue = queue
		self.syncdirPath = self.parent.parent.config.get('LocalSettings', 'sync-dir')
 
	def run(self):
		while True:
			path = self.queue.get()
			print path
			self.uploadFile(path)
			self.queue.task_done()
				
	def uploadFile(self, filepath):
		filepath = self.syncdirPath + filepath
		if not (os.path.isdir(filepath)):
			fileToUpload = file(filepath)
			self.parent.parent.smartfile.post('/path/data/', file=(filepath.replace(self.syncdirPath,''), fileToUpload))
		else:
			self.parent.parent.smartfile.post('/path/oper/mkdir/', filepath.replace(self.syncdirPath,''))
			

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
