import os, platform, shutil, subprocess, sys, time, urllib2
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
import math
from authenticator import Authenticator

# import code for encoding urls and generating md5 hashes
import urllib, hashlib, Image, cStringIO


import style

class LogoutLabel(QtGui.QLabel):
	def __init__(self, parent = None):
		QtGui.QLabel.__init__(self)
		self.parent = parent
		self.setText("Logout")

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
		#self.addIcon(self.email)
		

	def addIcon(self, email):
		self.icon = QtGui.QImage()
		# Set your variables here
		default = "http://i170.photobucket.com/albums/u260/Link5045/XC%20Avatar%20Tutorial/spongebob.jpg"
		size = 60
		 
		# construct the url
		gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
		gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
		
		print(gravatar_url)
		
		#img_file = cStringIO.StringIO(urllib.urlopen(gravatar_url).read())
		#self.icon.loadFromData(img_file, "JPG")
		
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
		tree = self.parent.smartfile.get('/whoami', '/')
		if 'user' not in tree:
			return []
		
		self.fullname = tree['user']['name'].encode("utf-8")
		self.email = tree['user']['email'].encode("utf-8")
		
		##get rid of the widget border
		self.setStyleSheet("QWidget { border: 0px; }")
		
		self.setMinimumSize(64, 64)
		self.setMaximumSize(300, 64)
		
		self.gridlayout = QtGui.QGridLayout()
		
		#Setup Fonts. 
		font = QtGui.QFont("Roboto", 16, QtGui.QFont.Light, False)
		smallfont = QtGui.QFont("Roboto", 12, QtGui.QFont.Light, False)
		
		self.lbFullName = QtGui.QLabel(self.fullname)
		self.lbFullName.setFont(font)
		
		self.lblogout = LogoutLabel(self)
		
		#self.loadGravatar()
		
		self.gridlayout.addWidget(self.lbFullName,0,0,1,1, QtCore.Qt.AlignRight)
		self.gridlayout.addWidget(self.lblogout)
		
		#Icon stuff
		self.newicon = IconWidget(self, self.email)
		#self.gridlayout.addWidget(self.newicon, 0, 1, 1, 1 , QtCore.Qt.AlignLeft)
		
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
