from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
import datetime, hashlib, os, platform, sqlite3, sys, time


class FileDatabase(object):
	def __init__(self, parent = None):
		object.__init__(self)
		self.parent = parent
		self.createDatabase()
		self.remoteFilesList = []
		#self.indexFiles()
	
	#####################################################
	############ Database Connect/Disconnect ############
	#####################################################
	
	def dbConnect(self):
		dbFile = self.parent.workingDirectory + "localdb.db"
		self.dbconnection = sqlite3.connect(dbFile)
		return self.dbconnection.cursor()
	
	def dbDisconnect(self):
		self.dbconnection.close()
		
		
	#####################################################
	##### Local file listing in the local database ######
	#####################################################
			
	def addFileLocal(self, sharepath, modified):
		#Adds files to the database.
		try:
			cursor = self.dbConnect()
			cursor.execute("INSERT INTO localfiles VALUES (?, ?)", (sharepath.decode('utf-8'), modified))
			self.dbconnection.commit()
		except:
			raise
		finally:
			self.dbDisconnect()	
	
	def clearFilesLocal(self):
		#clears the local files table
		cursor = self.dbConnect()
		cursor.execute("DELETE FROM localfiles")
		self.dbconnection.commit()
		
	def getModifiedLocal(self, filepath): 	
		##Returns when a file was last modified
		cursor = self.dbConnect()
		cursor.execute("SELECT modified FROM localfiles WHERE sharepath=?", (filepath,))	
		return cursor.fetchone()
		
	def moveFileLocal(self, oldpath, newpath):
		cursor = self.dbConnect()
		cursor.execute("UPDATE localfiles SET sharepath=? WHERE sharepath=?", (newpath, oldpath))	
		self.dbconnection.commit()
		
	def deleteFileLocal(self, sharepath):
		cursor = self.dbConnect()
		cursor.execute("DELETE FROM localfiles WHERE sharepath=?", (sharepath,))
		self.dbconnection.commit()
		
	#####################################################
	##### Remote file listing in the local database ######
	#####################################################
			
	def addFileRemote(self, sharepath, filehash):
		#Adds files to the database.
		try:
			cursor = self.dbConnect()
			cursor.execute("INSERT INTO remotefiles VALUES (?, ?)", (sharepath.decode('utf-8'), filehash))
			self.dbconnection.commit()
		except:
			raise
		finally:
			self.dbDisconnect()	
	
	def clearFilesRemote(self):
		#clears the remote files table
		cursor = self.dbConnect()
		cursor.execute("DELETE FROM remotefiles")
		self.dbconnection.commit()
		
	def getHashRemote(self, filepath): 	
		##Returns when a file was last modified
		cursor = self.dbConnect()
		cursor.execute("SELECT hash FROM remotefiles WHERE sharepath=?", (filepath,))	
		return cursor.fetchone()
		
	def moveFileRemote(self, oldpath, newpath):
		cursor = self.dbConnect()
		cursor.execute("UPDATE remotefiles SET sharepath=? WHERE sharepath=?", (newpath, oldpath))	
		self.dbconnection.commit()
		
	def deleteFileRemote(self, sharepath):
		cursor = self.dbConnect()
		cursor.execute("DELETE FROM remotefiles WHERE sharepath=?", (sharepath,))
		self.dbconnection.commit()
		
	

	#####################################################
	######## Local and remote file indexing #############
	#####################################################
	
	def indexFiles(self):
		syncdirPath = self.parent.config.get('LocalSettings', 'sync-dir')
		print "[database]: Local Database: Indexing local files..."
		##we must clear the existing table if there is request to index the files
		self.clearFilesLocal()
		for (paths, folders, files) in os.walk(syncdirPath):
			#for each file it sees, we want the path and the file to we can store it
			for item in files:
				#os.walk crawls in the "Shared" folder and it returns an array of great things (being the file path)!
				#print paths
				## os.path.join combines the real path with the filename, and it works cross platform, woot!
				discoveredFilePath = os.path.join(paths,item)
				filehash = self.hashFile(discoveredFilePath)
				self.addFileLocal(discoveredFilePath.replace(syncdirPath,''), filehash)
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
	
	def hashtask(self):
		#print self.remoteFilesList
		#for i in self.remoteFilesList:

		t = self.parent.smartfile.get("/path/oper/checksum", path='/globe.txt', algorithm='MD5')
		print t
		while True:
			s = self.parent.smartfile.get('/task', t['uuid'])
			if s['status'] == 'SUCCESS':
				print "success"
				break
	
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
		
	#####################################################
	################# Database creation #################
	#####################################################
	
	def createDatabase(self):
		try:
			cursor = self.dbConnect()
			cursor.execute("""CREATE TABLE localfiles (sharepath text, hash text)""")
			cursor.execute("""CREATE TABLE remotefiles (sharepath text, hash text)""")
			cursor.execute("""CREATE TABLE watchworkqueue (sharepath text, hash text)""")
		except sqlite3.OperationalError:
			pass
		finally:
			self.dbDisconnect()
