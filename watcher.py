import logging
import os
import threading
import time
import string
from ftplib import FTP
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler


class Watcher(threading.Thread):
    def __init__(self, parent=None):
        threading.Thread.__init__(self)
        self.parent = parent
        self.database = self.parent.database

    def run(self):
        self.path = self.parent.configuration.get('LocalSettings', 'sync-dir')
        self.event_handler = EventHandler(self.parent)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()


class EventHandler(FileSystemEventHandler):
    def __init__(self, parent=None):
        self.parent = parent
        self.syncdirPath = self.parent.configuration.get('LocalSettings', 'sync-dir')

    def on_moved(self, event):
        print event.src_path
        try:
            self.parent.smartfile.post('/path/oper/move/', src=(event.src_path), dst=(event.dest_path))
        except:
            raise

    def on_created(self, event):
        serverPath = self.localToServerPath(event.src_path)
        if not (event.is_directory):
            pathOnServer = event.src_path.replace(self.syncdirPath, '')
            #TODO: add file to the upload queue here
        else:
            try:
                self.parent.smartfile.post('/path/oper/mkdir/', path=serverPath)
            except:
                raise

    def on_deleted(self, event):
        print event.src_path
        try:
            thepath = event.src_path
            self.parent.smartfile.post('/path/oper/remove', path=thepath)
        except:
            pass

    def on_modified(self, event):
        print event.src_path
        if not (event.is_directory):
            ##print "Could not convert into utf-8, so make FTP connection"
            tree = self.parent.smartfile.get('/whoami', '/')
            if 'site' in tree:
                self.sitename = tree['site']['name'].encode("utf-8")
                ##print self.sitename

                username = self.parent.configuration.get('Login', 'username')
                password = self.parent.configuration.get('Login', 'password')

                ftpaddress = self.sitename + ".smartfile.com"
                ftp = FTP(ftpaddress, username, password)
                pathOnServer = event.src_path.replace(self.syncdirPath, '')
                try:
                    ftp.storbinary('STOR ' + pathOnServer, open(event.src_path, 'rb'))
                except:
                    pass
                else:
                    self.parent.database.generateRemoteListing()
        ##print event.event_type
        ##print event.src_path
    
    def localToServerPath(self, path):
        pathOnServer = path.replace(self.syncdirPath, '')
        if(pathOnServer.startswith("/")):
            pathOnServer = pathOnServer.strip("/")
        elif(pathOnServer.startswith("\\")):
            pathOnServer = pathOnServer.strip("\\")
        return pathOnServer
