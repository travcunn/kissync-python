from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
import datetime, hashlib, os, platform, Queue, shutil, sys, time, threading, subprocess
import cPickle as pickle

from StringIO import StringIO

from ftplib import FTP

class FileDatabase(object):
	def __init__(self, parent = None):
		object.__init__(self)
		self.parent = parent
		self.remoteFilesList = []
		
		self.remoteFilesDictionary = {}
		self.remoteFilesDictionaryTime = {}
		self.localFilesDictionary = {}
		self.localFilesDictionaryTime = {}
	
	def indexLocalFiles(self):
		syncdirPath = self.parent.config.get('LocalSettings', 'sync-dir')
		print "[database]: Local Database: Indexing local files..."
		##we must clear the existing table if there is request to index the files
		self.localFilesDictionary = {}
		for (paths, folders, files) in os.walk(syncdirPath):
			for item in files:
				discoveredFilePath = os.path.join(paths,item)
				filehash = self.hashFile(discoveredFilePath)
				modifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(discoveredFilePath))
				#Add file to dictionary. filename:ksjdfoi23lkx983n2lj9x823jl
				self.localFilesDictionary[discoveredFilePath.replace(syncdirPath,'').encode('utf-8')] = filehash.encode('utf-8')
				#Add file to dictionary with time. filename: timestamp
				self.localFilesDictionaryTime[discoveredFilePath.replace(syncdirPath,'').encode('utf-8')] = modifiedTime
				
				print  "[database-indexer]: %s %s" % (discoveredFilePath.replace(syncdirPath,'').encode('utf-8'), filehash.encode('utf-8'))
		print "[database]: Local Database: Done indexing local files..."

	
	def loadRemoteListingFile(self):
		try:
			self.parent.smartfile.post('/path/oper/remove', path='/.kissyncDBserver')
		except:
			pass
		try:
			self.parent.smartfile.post('/path/oper/remove', path='/.kissyncDBtimeserver')
		except:
			pass
		try:
			openPath = self.getServerListingFile()
			openPathTime = self.getServerListingFileTime()
			print "OPEN PATHS SHOULD CONTAIN A FILENAME"
			print openPath
			print openPathTime
		except:
			print "Remote listing does not exist..."
			openPath = None
			openPathTime = None
			self.remoteFilesDictionary = {}
			self.remoteFilesDictionaryTime = {}
			#self.generateRemoteListing()
		else:
			print "REMOTE FILES DICTIONARIES.... THESE SHOULD BE POPULATED"
			print self.remoteFilesDictionary
			print self.remoteFilesDictionaryTime
			picklefile = open(openPath, 'rb')
			self.remoteFilesDictionary = pickle.load(picklefile)
			picklefile.close()
			
			picklefiletime = open(openPathTime, 'rb')
			self.remoteFilesDictionaryTime = pickle.load(picklefiletime)
			picklefiletime.close()
			
			#subprocess.call(('xdg-open', openPath))
			#subprocess.call(('xdg-open', openPathTime))
			
	def generateRemoteListing(self):
		tmpLocalPath = self.parent.workingDirectory + "/.kissyncDBtmp"
		try:
			os.remove(tmpLocalPath)
		except:
			pass
		output = open(tmpLocalPath, 'wb')
		pickle.dump(self.localFilesDictionary, output)
		output.close()
		
		tmpLocalPathTime = self.parent.workingDirectory + "/.kissyncDBtmptime"
		try:
			os.remove(tmpLocalPathTime)
		except:
			pass
		outputtime = open(tmpLocalPathTime, 'wb')
		pickle.dump(self.localFilesDictionaryTime, outputtime)
		outputtime.close()
		
		#now upload the pickled files to the server
		try:
			fileToUpload = file(tmpLocalPath)
			print "Uploading files to the server"
			print fileToUpload.read()
			self.parent.smartfile.post('/path/data/', file=('/.kissyncDBserver', fileToUpload))
			
			fileToUpload = file(tmpLocalPathTime)
			self.parent.smartfile.post('/path/data/', file=('/.kissyncDBtimeserver', fileToUpload))
		except:
			raise
			self.generateRemoteListing()
				
	def getServerListingFile(self):
		filepath = "/.kissyncDBserver"
		fullpath = self.parent.workingDirectory + filepath
		try:
			os.remove(fullpath)
		except:
			pass
		f = self.parent.smartfile.get('/path/data', filepath)
		realPath = self.parent.workingDirectory + filepath
		realPath = realPath.encode("utf-8")
		with file(realPath, 'wb') as o:
			shutil.copyfileobj(f, o)
		return realPath
		
	def getServerListingFileTime(self):
		filepath = "/.kissyncDBtimeserver"
		fullpath = self.parent.workingDirectory + filepath
		try:
			os.remove(fullpath)
		except:
			pass
		f = self.parent.smartfile.get('/path/data/', filepath)
		realPath = self.parent.workingDirectory + filepath
		realPath = realPath.encode("utf-8")
		with file(realPath, 'wb') as o:
			shutil.copyfileobj(f, o)
		return realPath
			
	
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
		
		self.filesToDownload = []
		self.filesToUpload = []
		self.filesToCheckChanges = []
		
		self.downloadQueue = Queue.Queue()
		self.uploadQueue = Queue.Queue()
		self.checkChangesQueue = Queue.Queue()
		
	def start(self):
		#Compare what files server has against local files
		#print self.parent.database.remoteFilesDictionary
		#print self.parent.database.localFilesDictionary
		#print "Compare what files server has against local files:"
		self.dictDiffer = DictDiffer(self.parent.database.remoteFilesDictionary, self.parent.database.localFilesDictionary)
		
		#files the server that client needs
		print "FILES THAT WERE ADDED:"
		print self.dictDiffer.added()
		for i in self.dictDiffer.added():
			self.filesToDownload.append(i)
			self.downloadQueue.put(i)
		
		#local files that smartfile needs
		for i in self.dictDiffer.removed():
			self.filesToUpload.append(i)
			self.uploadQueue.put(i)
			
		#files that are different on the server, that the client needs	
		for i in self.dictDiffer.changed():
			self.filesToCheckChanges.append(i)
			self.checkChangesQueue.put(i)
		
		print "Files to download:"
		print self.filesToDownload
		print "Files to upload:"
		print self.filesToUpload	
		print "Files to check for changes:"
		print self.filesToCheckChanges

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
		print "changes queue joined"
		self.downloadQueue.join()
		print "dl queue joined"
		self.uploadQueue.join()
		print "ul queue joined"
		
		print "done joining"
		
		self.parent.database.generateRemoteListing()
		
		print "done generating remote listing"
		
		self.parent.filewatcher.start()


class CheckChanges(threading.Thread):
 
	def __init__(self, parent, queue):
		threading.Thread.__init__(self)
		self.parent = parent
		self.queue = queue
 
	def run(self):
		while True:
			print "running comparison..."
			path = self.queue.get()
			print path
			self.checkFile(path)
			self.queue.task_done()
				
	def checkFile(self, filepath):
		print "checking " + filepath
		localpath = self.parent.parent.config.get('LocalSettings', 'sync-dir') + filepath
		localModifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(localpath))
		if(self.parent.parent.database.remoteFilesDictionaryTime[filepath] > self.parent.parent.database.localFilesDictionaryTime[filepath]):
			print "Newer on the server: " + filepath
		elif(self.parent.parent.database.remoteFilesDictionaryTime[filepath] < self.parent.parent.database.localFilesDictionaryTime[filepath]):
			print "Newer on the client: " + filepath
		else:
			print "Equal on server and client: " + filepath

		
class Downloader(threading.Thread):
 
	def __init__(self, parent, queue):
		threading.Thread.__init__(self)
		self.parent = parent
		self.queue = queue
 
	def run(self):
		while True:
			path = self.queue.get()
			print "Downloading: " + path
			self.downloadFile(path)
			self.queue.task_done()
			print self.queue.qsize()
				
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
		try:
			f = self.parent.parent.smartfile.get('/path/data/', filepath)
			realPath = self.parent.parent.config.get('LocalSettings', 'sync-dir') + filepath
			realPath = realPath.encode("utf-8")
			with file(realPath, 'wb') as o:
				shutil.copyfileobj(f, o)
		except:
			pass
                
                
class Uploader(threading.Thread):
 
	def __init__(self, parent, queue):
		threading.Thread.__init__(self)
		self.parent = parent
		self.queue = queue
		self.syncdirPath = self.parent.parent.config.get('LocalSettings', 'sync-dir')
 
	def run(self):
		while True:
			path = self.queue.get()
			print "Uploading: " + path
			self.uploadFile(path)
			self.queue.task_done()
			print "Done uploading " + path
			print self.queue.qsize()
				
	def uploadFile(self, filepath):
		localpath = filepath
		filepath = self.syncdirPath + filepath
		if not (os.path.isdir(filepath)):
			fileToUpload = file(filepath, 'rb')
			try:
				self.parent.parent.smartfile.post('/path/data/', file=(filepath.replace(self.syncdirPath,''), StringIO(fileToUpload.read())))
			except:
				print "Could not convert into utf-8, so make FTP connection"
				tree = self.parent.parent.smartfile.get('/whoami', '/')
				if 'site' in tree:
					self.sitename = tree['site']['name'].encode("utf-8")
					
					username = self.parent.parent.config.get('Login', 'username')
					password = self.parent.parent.config.get('Login', 'password')
					
					#while(True):
					ftpaddress = self.sitename + ".smartfile.com"
					ftp = FTP(ftpaddress, username, password)
					
					pathArray = localpath.split("/")
					pathArray.pop(0)
					pathArray.pop(len(pathArray) - 1)
					pathToAdd = ""
					
					#A BUG EXISTS IN THIS, PLEASE TEST THIS
					syncdir =  self.parent.parent.config.get('LocalSettings', 'sync-dir')	
					for directory in pathArray:
						try:
							ftp.mkd("/" + pathToAdd + directory)
						except:
							print "directory exists already: " + directory
						else:
							print "created directory " + pathToAdd + directory
						#os.makedirs(self.parent.parent.parent.config.get('LocalSettings', 'sync-dir') + "/" + pathToAdd + directory)
						pathToAdd = pathToAdd + directory + "/"
					ftp.storbinary('STOR ' + localpath.encode('utf-8'), open(filepath, 'rb'))
				else:
					print "Could not upload the file via ftp"
							
		else:
			self.parent.parent.smartfile.post('/path/oper/mkdir/', filepath.replace(self.syncdirPath,''))
			
	def directoryexists(self, ftp, dir):
		filelist = []
		ftp.retrlines('LIST',filelist.append)
		for f in filelist:
			print f
			if f.split()[-1] == dir and f.upper().startswith('D'):
				return True
		return False
	
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
