import threading
import sys
import time
import datetime
import os
import sqlite3
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

from ftplib import FTP

class Watcher(threading.Thread):
	def __init__(self, parent = None):
		threading.Thread.__init__(self)
		self.parent = parent
		self.database = self.parent.database
	
	def run(self):
		##print "started the watcher"
		self.path = self.parent.config.get('LocalSettings', 'sync-dir')
		self.event_handler = EventHandler(self.parent)
		self.observer = Observer()
		self.observer.schedule(self.event_handler, self.path, recursive=True)
		self.observer.start()
		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			observer.stop()
			observer.join()
		except:
			observer.stop()
			observer.join()
		
		
		
class EventHandler(FileSystemEventHandler):
	def __init__(self, parent = None):
		self.parent = parent
		self.syncdirPath = self.parent.config.get('LocalSettings', 'sync-dir')
		
	def on_moved(self, event):
		try:
			self.parent.smartfile.post('/path/oper/move/', src=(event.src_path), dst=(event.dest_path))
		except:
			raise
		##print event.event_type
		##print event.src_path
		##print event.dest_path

	def on_created(self, event):
		if not (event.is_directory):
			fileToUpload = file(event.src_path)
			try:
				self.parent.smartfile.post('/path/data/', file=(event.src_path.replace(self.syncdirPath,''), fileToUpload))
			except:
				##print "Could not convert into utf-8, so make FTP connection"
				tree = self.parent.smartfile.get('/whoami', '/')
				if 'site' in tree:
					self.sitename = tree['site']['name'].encode("utf-8")
					##print self.sitename
					
					username = self.parent.config.get('Login', 'username')
					password = self.parent.config.get('Login', 'password')
					
					ftpaddress = self.sitename + ".smartfile.com"
					ftp = FTP(ftpaddress, username, password)
					pathOnServer = event.src_path.replace(self.syncdirPath,'')
					try:
						ftp.storbinary('STOR ' + pathOnServer, open(event.src_path, 'rb'))
					except:
						pass
		else:
			self.parent.smartfile.post('/path/oper/mkdir/', event.src_path.replace(self.syncdirPath,''))
		##print event.event_type
		##print event.src_path

	def on_deleted(self, event):
		try:
			thepath = event.src_path
			self.parent.smartfile.post('/path/oper/remove', path=(thepath))
		except:
			pass

	def on_modified(self, event):
		if not (event.is_directory):
			fileToUpload = file(event.src_path)
			try:
				self.parent.smartfile.post('/path/data/', file=(event.src_path.replace(self.syncdirPath,''), fileToUpload))
			except:
				##print "Could not convert into utf-8, so make FTP connection"
				tree = self.parent.smartfile.get('/whoami', '/')
				if 'site' in tree:
					self.sitename = tree['site']['name'].encode("utf-8")
					##print self.sitename
					
					username = self.parent.config.get('Login', 'username')
					password = self.parent.config.get('Login', 'password')
					
					ftpaddress = self.sitename + ".smartfile.com"
					ftp = FTP(ftpaddress, username, password)
					pathOnServer = event.src_path.replace(self.syncdirPath,'')
					try:
						ftp.storbinary('STOR ' + pathOnServer, open(event.src_path, 'rb'))
					except:
						pass
		##print event.event_type
		##print event.src_path
			
