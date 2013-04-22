import ConfigParser, os, sys
from PyQt4 import QtCore, QtGui

import style
from authenticator import Authenticator
from filedatabase import FileDatabase
from filedatabase import Synchronizer
from filedatabase import RefreshThread
from loginwindow import LoginWindow
from setupwizard import SetupWizard
from tray import SystemTrayIcon
from filebrowsergui import FileBrowserGUI
from accountwidget import AccountWidget

import watcher
							
			
class Main(QtGui.QWidget):
	def __init__(self, parent = None):
		super(Main, self).__init__(parent)
		self.style = style.KissyncStyle()
		
		self.config = ConfigParser.RawConfigParser() #configuration parser
		
		self.kissyncDirectory = os.path.join(os.path.expanduser("~"), "Kissync")
		self.workingDirectory = os.path.join(os.path.expanduser("~"), ".kissync")
		self.settingsFile = os.path.join(os.path.expanduser("~"), ".kissync", "configuration.cfg")
		
		if not os.path.exists(self.workingDirectory):
			os.makedirs(self.workingDirectory)
		
		if not os.path.exists(self.kissyncDirectory):
			os.makedirs(self.kissyncDirectory)
		
		try:
			with open(self.settingsFile): pass
		except IOError:
			self.config.add_section('Login')
			self.config.set('Login', 'username', None)
			self.config.set('Login', 'password', None)
			self.config.add_section('LocalSettings')
			self.config.set('LocalSettings', 'first-run', True)
			self.config.set('LocalSettings', 'network-timeout', 30)
			self.config.set('LocalSettings', 'notifications', True)
			self.config.set('LocalSettings', 'sync-offline', False)
			self.config.set('LocalSettings', 'sync-dir', None)
			with open(self.settingsFile, 'wb') as configfile:
				self.config.write(configfile)
		else:
			self.config.read(self.settingsFile)
		
		
		
		#################MAIN WINDOW GUI#####################
		self.setWindowTitle('Keep It Simple Sync')  
		self.displayFont = QtGui.QFont()
		self.setGeometry(200, 200, 870, 600)
		self.setMinimumSize(900, 600)
		
		#Load font for the title text
		fontDatabase = QtGui.QFontDatabase()
		fontfile = QtCore.QFile(os.path.dirname(os.path.realpath(__file__)) + "resources/Roboto-Light-webfont.ttf")
		fontDatabase.addApplicationFont(os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf")
		#os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf"
		palette = QtGui.QPalette()
		#palette.setColor(QtGui.QPalette.Foreground,QtGui.QColor("#FFFFFF"))
		
		
		#Title Text Font
		topText = QtGui.QLabel('Kissync Enterprise')
		#http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
		font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
		topText.setFont(font)
		topText.setPalette(palette)
		#topText.setStyleSheet("color: #FFFFFF;")
		
		#Title Text Widget
		self.titlewidget = QtGui.QWidget()
		self.titlelayout = QtGui.QGridLayout()
		self.titlelayout.addWidget(topText)
		self.titlewidget.setLayout(self.titlelayout)
		self.titlewidget.setMaximumHeight(70)
	
		self.grid = QtGui.QGridLayout()
		self.grid.setContentsMargins(0, 10, 10, 0)
		self.setLayout(self.grid)
		
		#connects directly to the smartfile api, but relies upon self.authenticator	to create
		self.smartfile = None #we don't want to init yet, so we can handle errors later on login
		#login screen
		self.database = FileDatabase(self)
		
		#setup window for initial user configuration
		self.setupwizard = SetupWizard(self)
		
		self.loginwindow = LoginWindow(self)
		#runs the authentication process that connects self.smartfile with a smartfile client
		
		self.tray = SystemTrayIcon(self) #tray icon
		self.tray.show()
		self.tray.notification("Kissync Enterprise", "Starting up....")
		
		self.authenticator = Authenticator(self) #login in
		
		#self.filewatcher = watcher.Watcher(self)
		
	def start(self):
		#this method is called on login success
		self.show()
		
		self.database.generateAuthHash()
		self.database.indexLocalFiles()
		self.database.loadRemoteListingFile()
		
		self.filewatcher = watcher.Watcher(self)
		
		self.synchronizer = Synchronizer(self)
		self.synchronizer.start()
		
		self.rt = RefreshThread(self)
		self.rt.start()
		
		self.filebrowsergui = FileBrowserGUI(self)		
		self.accountwidget = AccountWidget(self)
		self.grid.addWidget(self.titlewidget, 0, 0)
		self.grid.addWidget(self.accountwidget, 0 , 1, 1, 1, QtCore.Qt.AlignRight)
		self.grid.addWidget(self.filebrowsergui, 1, 0, 1, 2)
	
	def closeEvent(self, event):
		event.ignore()
		self.hide()
	
	def exit(self):
		os._exit(-1)


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	mainwindow = Main()
	sys.exit(app.exec_())
	
	
