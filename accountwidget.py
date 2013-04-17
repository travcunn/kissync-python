import os, platform, shutil, subprocess, sys, time, urllib2
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
import math
from authenticator import Authenticator

# import code for encoding urls and generating md5 hashes
import urllib, hashlib, Image, cStringIO

import style

#topText.setStyleSheet("color: #FFFFFF;")

class SettingsLabel(QtGui.QLabel):
	def __init__(self, parent = None):
		QtGui.QLabel.__init__(self)
		self.parent = parent
		self.setText("Settings")
		font = QtGui.QFont("Roboto", 16, QtGui.QFont.Normal, False)
		self.setFont(font)
		self.setStyleSheet("color: #1BA1E2;")
		
	def mousePressEvent(self, event):
		print "Settings button pressed"
		
	def mouseDoubleClickEvent(self, event):
		pass
		
	def enterEvent(self,event): 
		self.setStyleSheet("color: #8CBF26;")
		self.repaint()
	
	def leaveEvent(self,event): 
		self.setStyleSheet("color: #1BA1E2;")
		self.repaint()
		
		
class LogoutLabel(QtGui.QLabel):
	def __init__(self, parent = None):
		QtGui.QLabel.__init__(self)
		self.parent = parent
		self.setText("Logout")
		font = QtGui.QFont("Roboto", 16, QtGui.QFont.Normal, False)
		self.setFont(font)
		self.setStyleSheet("color: #1BA1E2;")
		
	def mousePressEvent(self, event):
		print "Logout button pressed"
		
	def mouseDoubleClickEvent(self, event):
		pass
		
	def enterEvent(self,event): 
		self.setStyleSheet("color: #8CBF26;")
		self.repaint()
	
	def leaveEvent(self,event): 
		self.setStyleSheet("color: #1BA1E2;")
		self.repaint()
		
		
class UsernameLabel(QtGui.QLabel):
	def __init__(self, parent = None, fullname = ""):
		QtGui.QLabel.__init__(self)
		self.parent = parent
		self.setText(fullname)
		font = QtGui.QFont("Roboto", 16, QtGui.QFont.Light, False)
		self.setFont(font)

		
class IconWidget(QtGui.QWidget):
	
	def __init__(self, parent = None, email = None):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		self.email = email

		##get rid of the widget border
		self.setStyleSheet("QWidget { border: 0px; }")
		
		self.setMinimumSize(64, 64)
		self.setMaximumSize(64, 64)
		
		self.gridlayout = QtGui.QGridLayout()
		
		#self.setLayout(self.gridlayout)
		self.addIcon(self.email)
		

	def addIcon(self, email):
		self.icon = QtGui.QImage()
		size = 64
		
		gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?s=" + str(size)

		img_file = urllib.urlopen(gravatar_url).read()
		self.icon.loadFromData(img_file, "JPG")
		
		self.icontarget = QtCore.QRectF(0, 0, 64, 64)
        
	#this is called every time something needs to be repainted
	def paintEvent(self, e):
		#Start Painter
		painter = QtGui.QPainter()
		painter.begin(self)
				
		# Draw Item Thumbnail.
		painter.drawImage(self.icontarget, self.icon)
		
		#End Painter
		painter.end()


class AccountWidget(QtGui.QWidget):
	
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		#Call API to get full name and email address.
		try:
			tree = self.parent.smartfile.get('/whoami', '/')
			if 'user' not in tree:
				return []
				
			self.fullname = tree['user']['name'].encode("utf-8")
			self.email = tree['user']['email'].encode("utf-8")
		except:
			self.fullname = "Travis Cunningham"
			self.email = "travcunn@umail.iu.edu"
		
		
		##get rid of the widget border
		self.setStyleSheet("QWidget { border: 0px; }")
		
		self.setMinimumSize(300, 85)
	
		self.setMaximumSize(300, 85)
		
		self.gridlayout = QtGui.QGridLayout()
		
		self.lbFullName = UsernameLabel(self, self.fullname)
		self.lbsettings = SettingsLabel(self)
		self.lblogout = LogoutLabel(self)
		
		#self.loadGravatar()
		
		self.gridlayout.addWidget(self.lbFullName, 0, 1, 1, 2, QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
		self.gridlayout.addWidget(self.lbsettings, 1, 1, 1, 1, QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
		self.gridlayout.addWidget(self.lblogout, 1, 2, 1, 1, QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
		
		#Icon stuff
		self.newicon = IconWidget(self, self.email)
		self.gridlayout.addWidget(self.newicon, 0, 0, 2, 1 , QtCore.Qt.AlignCenter)
		
		self.setLayout(self.gridlayout)
		
		
class Main(QtGui.QWidget):
	def __init__(self, parent = None):
		super(Main, self).__init__(parent)
		self.setWindowTitle('Keep It Simple Sync')  
		
		#self.setStyleSheet("#MainWindow {background-color: #222222; }") 
		self.setGeometry(400, 200, 300, 325)
		
		#Add Account Widget With dummy Info.
		self.accountInfo = AccountWidget(self)

		self.grid = QtGui.QGridLayout()
		
		
		self.grid.addWidget(self.accountInfo)

		self.setLayout(self.grid)

		
if __name__ == "__main__":
	
	#print os.path.realpath(__file__)
	app = QtGui.QApplication(sys.argv)
	mainwindow = Main()
	mainwindow.show()
	sys.exit(app.exec_())
