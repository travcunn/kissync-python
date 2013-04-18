import threading
import sys
import time
import datetime
import os
import sqlite3
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

class Watcher(threading.Thread):
	def __init__(self, parent = None):
		threading.Thread.__init__(self)
		self.parent = parent
		self.database = self.parent.database
	
	def run(self):
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
		
		
		
class EventHandler(FileSystemEventHandler):
	def __init__(self, parent = None):
		self.parent = parent
		self.syncdirPath = self.parent.config.get('LocalSettings', 'sync-dir')
		
	def on_moved(self, event):
		print event.event_type
		print event.src_path
		print event.dest_path

	def on_created(self, event):
		if not (event.is_directory):
			fileToUpload = file(event.src_path)
			self.parent.smartfile.post('/path/data/', file=("/TestingFolder" + event.src_path.replace(self.syncdirPath,''), fileToUpload))
			#self.parent.smartfile.post('/path/data/', file=file(event.src_path.replace(self.syncdirPath,''), 'rb'))
		else:
			self.parent.smartfile.post('/path/oper/mkdir/', event.src_path.replace(self.syncdirPath,''))
		print event.event_type
		print event.src_path

	def on_deleted(self, event):
		print event.event_type
		print event.src_path

	def on_modified(self, event):
		#For polling, folders are "modified" when its contents are. we dont need to see this.
		if not (event.is_directory):
			print event.event_type
			print event.src_path
			
