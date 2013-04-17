import ConfigParser, sys
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg

import breadcrumb, flowlayout, loadingwidget, style, square
from authenticator import Authenticator
from filedatabase import FileDatabase
from loginwindow import LoginWindow
from fileview import FileView
from setupwizard import SetupWizard
from tray import TrayMenu, SystemTrayIcon
from filebrowsergui import FileBrowserGUI
from accountwidget import AccountWidget

import watcher
							
			
class Main(QtGui.QWidget):
	def __init__(self, parent = None):
		super(Main, self).__init__(parent)
		self.style = style.KissyncStyle()
		
		self.config = ConfigParser.RawConfigParser() #configuration parser
		
		try:
			with open('configuration.cfg'): pass
		except IOError:
			self.config.add_section('Login')
			self.config.set('Login', 'username', None)
			self.config.set('Login', 'password', None)
			self.config.add_section('LocalSettings')
			self.config.set('LocalSettings', 'first-run', True)
			self.config.set('LocalSettings', 'network-timeout', 20)
			self.config.set('LocalSettings', 'notifications', True)
			self.config.set('LocalSettings', 'sync-offline', False)
			self.config.set('LocalSettings', 'sync-dir', None)
			with open('configuration.cfg', 'wb') as configfile:
				self.config.write(configfile)
		else:
			self.config.read('configuration.cfg')
		
		#connects directly to the smartfile api, but relies upon self.authenticator	to create
		self.smartfile = None #we don't want to init yet, so we can handle errors later on login
		#login screen
		self.loginwindow = LoginWindow(self)
		#runs the authentication process that connects self.smartfile with a smartfile client
		self.authenticator = Authenticator(self) #login in
		#tray icon
		self.tray = SystemTrayIcon(self) #tray icon
		self.tray.show()
		#setup window for initial user configuration
		self.setupwizard = SetupWizard(self)
		#file database
		self.database = FileDatabase(self)
		#file system watcher
		#self.filewatcher = watcher.Watcher(self)
		
		
		#################MAIN WINDOW GUI#####################
		self.filebrowsergui = FileBrowserGUI(self)
		
		self.setWindowTitle('Keep It Simple Sync')  
		self.displayFont = QtGui.QFont()
		#self.setStyleSheet("background-color: #222222; ") 
		self.setGeometry(400, 200, 1000, 500)
		self.setMinimumSize(580, 600)
		
		fontDatabase = QtGui.QFontDatabase()
		#fontfile = QtCore.QFile("resources/Roboto-Light-webfont.ttf")
		#fontDatabase.addApplicationFont(os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf")
		#os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf"
		palette = QtGui.QPalette()
		#palette.setColor(QtGui.QPalette.Foreground,QtGui.QColor("#FFFFFF"))
		
		topText = QtGui.QLabel('Kissync Enterprise')
		#http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
		font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
		topText.setFont(font)
		topText.setPalette(palette)
		#topText.setStyleSheet("color: #FFFFFF;")
		self.titlewidget = QtGui.QWidget()
		self.titlelayout = QtGui.QGridLayout()
		self.titlelayout.addWidget(topText)
		self.titlewidget.setLayout(self.titlelayout)
		self.titlewidget.setMaximumHeight(70)
		
		self.accountwidget = AccountWidget(self)
		
		grid = QtGui.QGridLayout()
		grid.setContentsMargins(0, 0, 0, 0)
		grid.addWidget(self.titlewidget, 0, 0)
		grid.addWidget(self.accountwidget, 0 , 1)
		grid.addWidget(self.filebrowsergui, 1, 0, 2, 1)
		self.setLayout(grid)


if __name__ == "__main__":
	
	app = QtGui.QApplication(sys.argv)
	mainwindow = Main()
	sys.exit(app.exec_())
