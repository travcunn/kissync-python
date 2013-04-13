from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
import datetime, os, platform, sqlite3, sys, time


class FileDatabase(object):
	def __init__(self, parent = None):
		object.__init__(self)
		self.parent = parent
		self.createDatabase()
		self.indexFiles()
	
	#####################################################
	############ Database Connect/Disconnect ############
	#####################################################
	
	def dbConnect(self):
		self.dbconnection = sqlite3.connect("localdb.db")
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
		cursor.execute("UPDATE localfiles SET status=? WHERE peerip=?", (newpath, oldpath))	
		self.dbconnection.commit()
		
	def deleteFileLocal(self, sharepath):
		cursor = self.dbConnect()
		cursor.execute("DELETE FROM localfiles WHERE sharepath=?", (sharepath,))
		self.dbconnection.commit()
		
	#####################################################
	##### Remote file listing in the local database ######
	#####################################################
			
	def addFileRemote(self, sharepath, modified):
		#Adds files to the database.
		try:
			cursor = self.dbConnect()
			cursor.execute("INSERT INTO remotefiles VALUES (?, ?)", (sharepath.decode('utf-8'), modified))
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
		
	def getModifiedRemote(self, filepath): 	
		##Returns when a file was last modified
		cursor = self.dbConnect()
		cursor.execute("SELECT modified FROM remotefiles WHERE sharepath=?", (filepath,))	
		return cursor.fetchone()
		
	def moveFileRemote(self, oldpath, newpath):
		cursor = self.dbConnect()
		cursor.execute("UPDATE remotefiles SET status=? WHERE peerip=?", (newpath, oldpath))	
		self.dbconnection.commit()
		
	def deleteFileRemote(self, sharepath):
		cursor = self.dbConnect()
		cursor.execute("DELETE FROM remotefiles WHERE sharepath=?", (sharepath,))
		self.dbconnection.commit()
		
	

	#####################################################
	######## Local file discovery and indexing  #########
	#####################################################
	
	def indexFiles(self):
		syncdirPath = self.parent.config.get('LocalSettings', 'sync-dir')
		print "[database]: Indexing all files in the shared folder..."
		##we must clear the existing table if there is request to index the files
		self.clearFilesLocal()
		for (paths, folders, files) in os.walk(syncdirPath):
			#for each file it sees, we want the path and the file to we can store it
			for item in files:
				#os.walk crawls in the "Shared" folder and it returns an array of great things (being the file path)!
				#print paths
				## os.path.join combines the real path with the filename, and it works cross platform, woot!
				discoveredFilePath = os.path.join(paths,item)
				modifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(discoveredFilePath))
				self.addFileLocal(discoveredFilePath.replace(syncdirPath,''), modifiedTime)
				print  "[database-indexer]: %s %s" % (discoveredFilePath.replace(syncdirPath,''), modifiedTime)
		print "[database]: Indexing complete..."
			

	#####################################################
	################# Database creation #################
	#####################################################
	
	def createDatabase(self):
		try:
			cursor = self.dbConnect()
			cursor.execute("""CREATE TABLE localfiles (sharepath text, modified datetime)""")
			cursor.execute("""CREATE TABLE remotefiles (sharepath text, modified datetime)""")
			cursor.execute("""CREATE TABLE watchworkqueue (sharepath text, modified datetime)""")
		except sqlite3.OperationalError:
			pass
		finally:
			self.dbDisconnect()
