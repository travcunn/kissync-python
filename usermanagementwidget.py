import os, platform, shutil, subprocess, sys, time, urllib2
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
import math

import style

class ItemObject(QtGui.QWidget):
	def __init__(self, parent = None):
		super(LoginWindow, self).__init__()
		self.parent = parent
		self.setWindowTitle('User Management')  
		 
		#set the window type to a dialog
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog)
		self.parent = parent

class Main(QtGui.QWidget):
	def __init__(self, parent = None):
		super(Main, self).__init__(parent)
		self.setWindowTitle('Keep It Simple Sync - User Management')  
		
		#self.setStyleSheet("#MainWindow {background-color: #222222; }") 
		self.setGeometry(400, 200, 300, 325)
		
		self.grid = QtGui.QGridLayout()

		self.setLayout(self.grid)

		
if __name__ == "__main__":
	
	#print os.path.realpath(__file__)
	app = QtGui.QApplication(sys.argv)
	mainwindow = Main()
	mainwindow.show()
	sys.exit(app.exec_())
	
