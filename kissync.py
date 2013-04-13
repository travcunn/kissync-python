import ConfigParser, datetime, os, platform, sqlite3, sys, time, urllib2
from smartfile import OAuthClient
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
from bs4 import BeautifulSoup

import breadcrumb, flowlayout, loadingwidget, style, TaylorSquare

import watcher


class Authenticator(object):
	def __init__(self, parent = None):
		super(Authenticator, self).__init__()
		self.parent = parent 
		
		self.htmlView = AuthBrowser(self)
		self.go()
                
	def go(self):
		try:
			#reset the pageloads counter every time the browser is called
			self.htmlView.pageloads = 0
			self.parent.smartfile = OAuthClient("zGSJpILRq2889Ne2bPBdEmEZLsRHpe", "KOb97irJG84PJ8dtEkoYt2Kqwz3VJa")
		except:
			self.networkerror()
		else:
			self.parent.smartfile.get_request_token()
			self.htmlView.load(QtCore.QUrl(self.parent.smartfile.get_authorization_url()))
	
	def networkerror(self):
		self.parent.loginwindow.networkerror()
	
	def badloginerror(self):
		if not(self.parent.config.get('Login', 'username') == "None" and self.parent.config.get('Login', 'username') == "None"):
			#if the username and pass are wrong but arent the defaults, give an invalid error
			self.parent.loginwindow.invaliderror()
		else:
			#otherwise, just show the login screen without error messages
			self.parent.loginwindow.errorText.hide()
			self.parent.loginwindow.neterrorText.hide()
			self.parent.loginwindow.show()
	
	def success(self):
		#Successfully logged in
		if(self.parent.config.get('LocalSettings', 'first-run') == "True"):
			self.parent.setupwizard.show()
			self.parent.tray.notification("Welcome to Kissync", "Please complete the setup to start using Kissync")
		else:
			print "starting the watcher thread"
			self.parent.filewatcher.start()


class AuthBrowser(QtWebKit.QWebView):
	def __init__(self, parent):
		self.parent = parent
		QtWebKit.QWebView.__init__(self)
		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.loadFinished.connect(self._result_available)
		self.loadStarted.connect(self._starttimer)
		self.timer = QtCore.QTimeLine()
		self.pageloads = 0

	def _result_available(self, ok):
		frame = self.page().mainFrame()
		soup = BeautifulSoup(unicode(frame.toHtml()).encode('utf-8'))
		doc = self.page().mainFrame().documentElement()

        
		#IF ON THE LOGIN FORM PAGE
		if(self.pageloads == 0):
			#fill out the form here
			user = doc.findFirst("input[id=id_login]")
			passwd = doc.findFirst("input[id=id_password]")
			#####this should read from the config file
			self.parent.parent.config.read('configuration.cfg')
			user.evaluateJavaScript("this.value = '" + self.parent.parent.config.get('Login', 'username') + "'")
			passwd.evaluateJavaScript("this.value = '" + self.parent.parent.config.get('Login', 'password') + "'")

			button = doc.findFirst("button[type=button]")
			button.evaluateJavaScript("this.click()")
			#end filling out the form

		#if on the second page, this should be verifier submit page
		if(self.pageloads == 1):
			verify = doc.findFirst("button[type=submit]")
			verify.evaluateJavaScript("this.click()")
		
			if(soup.find(text='You are currently logged in as:') == None):
				#bad username or password, failure
				self.parent.badloginerror()
		
		#if on the third page or higher, get the verifier
		if(self.pageloads >= 2):
			try:
				verifierlocal = soup.find(id="id_verifier").get("value")
			except:
				#bad username or password, failure
				self.parent.badloginerror()
			else:
				#logged in successfully, now verify the key...
				try:
					self.parent.parent.smartfile.get_access_token(None, verifierlocal)
				except:
					#something happened after logging in successfully, and is not sucessful now
					self.parent.badloginerror()
				else:
					#logged in successfully
					self.parent.success()
		
		self.pageloads = self.pageloads + 1
		self.timer.stop()
			
	def _starttimer(self):
		self.pagetimer()
	
	def pagetimer(self):
		#starts up a page timer, so after 30 seconds, we can give a network error
		self.timer.valueChanged.connect(self.netwatch)
		self.timer.setDuration(int(self.parent.parent.config.get('LocalSettings', 'network-timeout')) * 1000)
		self.timer.start()
	
	def netwatch(self, value):
		if (value == 1.0):
			self.stop()
			self.parent.networkerror()
        		

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


class LoginWindow(QtGui.QWidget):

	def __init__(self, parent = None):
		super(LoginWindow, self).__init__()
		self.parent = parent
		self.setWindowTitle('Login to Kissync')   
		#set the window type to a dialog
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog)
		
		fontDatabase = QtGui.QFontDatabase()
		#fontfile = QtCore.QFile("resources/Roboto-Light-webfont.ttf")
		#fontDatabase.addApplicationFont(os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf")
		palette = QtGui.QPalette()
		#palette.setColor(QtGui.QPalette.Foreground,QtGui.QColor("#FFFFFF"))
		
		exit=QtGui.QAction(self)
		self.connect(exit,QtCore.SIGNAL('triggered()'),QtCore.SLOT('close()'))
		
		topText = QtGui.QLabel('Login to Kissync')
		#http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
		font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
		topText.setFont(font)
		topText.setPalette(palette)
		topText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		#topText.setStyleSheet("color: #FFFFFF
		
		detailsText = QtGui.QLabel('using your Smartfile acount')
		#http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
		fontsmall = QtGui.QFont("Roboto", 14, QtGui.QFont.Normal, False)
		detailsText.setFont(fontsmall)
		detailsText.setPalette(palette)
		detailsText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		#topText.setStyleSheet("color: #FFFFFF;")

		grid = QtGui.QGridLayout()
		
		#window size constraints
		self.setFixedSize(465, 325)
		
		spacer = QtGui.QWidget()
		spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		#file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		
		formwidget =  QtGui.QWidget()
		formgrid = QtGui.QFormLayout()
		formwidget.setLayout(formgrid)
		
		fontform = QtGui.QFont("Roboto", 12, QtGui.QFont.Normal, False)
		fonterror = QtGui.QFont("Roboto", 18, QtGui.QFont.Normal, False)
		
		self.errorText = QtGui.QLabel('Invalid Username or Password')
		self.errorText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.errorText.setStyleSheet("color: #FF0000;")
		self.errorText.setFont(fonterror)
		self.errorText.hide()
		
		self.neterrorText = QtGui.QLabel('Error Connecting to SmartFile')
		self.neterrorText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.neterrorText.setStyleSheet("color: #FF0000;")
		self.neterrorText.setFont(fonterror)
		self.neterrorText.hide()
		
		usernameText = QtGui.QLabel('Username:')
		usernameText.setFont(fontform)
		self.usernameField = QtGui.QLineEdit()
		passwordText = QtGui.QLabel('Password:')
		passwordText.setFont(fontform)
		self.passwordField = QtGui.QLineEdit()
		self.passwordField.setEchoMode(QtGui.QLineEdit.Password)
		loginButton = QtGui.QPushButton('Login')
		loginButton.clicked.connect(self.tryLogin)
		
		formgrid.addRow(usernameText, self.usernameField)
		formgrid.addRow(passwordText, self.passwordField)
		formgrid.addRow(loginButton)
		
		#add the objects to the grid
		grid.addWidget(spacer, 0, 0)
		grid.addWidget(spacer, 0, 2)
		grid.addWidget(topText, 0, 1)
		grid.addWidget(detailsText, 1, 1)
		grid.addWidget(self.errorText, 2, 1)
		grid.addWidget(self.neterrorText, 3, 1)
		grid.addWidget(formwidget, 4, 1)
		#grid.addWidget(loading, 1, 1)
		grid.addWidget(spacer, 10, 1)
		#set the layout to grid layout
		self.setLayout(grid)
		self.centerOnScreen()
	
	def tryLogin(self):
		self.parent.config.set('Login', 'username', str(self.usernameField.text()))
		self.parent.config.set('Login', 'password', str(self.passwordField.text()))
		with open('configuration.cfg', 'wb') as configfile:
			self.parent.config.write(configfile)
		
		self.parent.authenticator.go()
		self.hide()
		
	def networkerror(self):
		self.neterrorText.show()
		self.errorText.hide()
		self.show()
		
	def invaliderror(self):
		self.errorText.show()
		self.neterrorText.hide()
		self.show()
			
	def centerOnScreen(self):
		resolution = QtGui.QDesktopWidget().screenGeometry()
		self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
				(resolution.height() / 2) - (self.frameSize().height() / 2))

	def closeEvent(self, event):
		#if the user closes the login window, close the entire app...
		sys.exit()
		

class SquareObject(QtGui.QWidget):
	def __init__(self, parent, color = None):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		
		self.squareWidth = 180
		self.squareHeight = 90


		self.icon = QtGui.QImage()
		self.icon.load(os.path.dirname(os.path.realpath(__file__)) + "/icons/faience/mimetypes/x-office-presentation.svg")
		self.icontarget = QtCore.QRectF(0, 0, 64, 64)
		
		self.closebutton = QtGui.QImage()
		self.closebutton.load(os.path.dirname(os.path.realpath(__file__)) + "/icons/bwpx-icns/icons/symbol_multiplication.gif")
		self.closebuttontarget = QtCore.QRectF((self.squareWidth - 18), 0, 18, 18)
		
		if(color == None):
			self.color = parent.style.BLUE
		else:
			self.color = color
		self.color = parent.style.hexToQColor(self.color)
		self.initUI()
        
	def initUI(self):      
		print "Creating a square..."
		self.setFixedSize(self.squareWidth, self.squareHeight)
		self.opacity = 0.0
		self.timeline = QtCore.QTimeLine()
		self.timeline.valueChanged.connect(self.animate)
		self.timeline.setDuration(500)
		self.timeline.start()


	#this is called every time something needs to be repainted
	def paintEvent(self, e):
		painter = QtGui.QPainter()
		painter.begin(self)
		painter.setOpacity(self.opacity)
		self.drawSquare(painter)
		painter.drawImage(self.icontarget, self.icon)
		painter.drawImage(self.closebuttontarget, self.closebutton)
		painter.end()
        
	def drawSquare(self, painter):
		#get rid of the pen... gets rid of outline on drawing
		painter.setPen(QtCore.Qt.NoPen)
		#windows 8 colors are pretty http://www.creepyed.com/2012/09/windows-8-colors-hex-code/
		painter.setBrush(self.color)
		#from docs: drawRect (self, int x, int y, int w, int h)
		painter.drawRect(0, 0, self.squareWidth, self.squareHeight)
	
	def animate(self, value):
		self.opacity = value * self.parent.style.SQUAREOPACITY
		self.repaint()
		
	def enterEvent(self,event): 
		print("Enter") 
		self.opacity = 1.0
		self.repaint()
	
	def leaveEvent(self,event): 
		print("Leave") 
		self.opacity = self.parent.style.SQUAREOPACITY
		self.repaint()
	
	def mousePressEvent(self,event): 
		print("Widget clicked event") 
		self.repaint()
	
	
class FileView(QtGui.QWidget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		##get rid of the widget border
		#self.setStyleSheet("border: 0px")
		self.style = style.KissyncStyle()
		
		topText = QtGui.QLabel('Kissync File View Widget Test')
		 
		self.addButton = QtGui.QPushButton('button to add other widgets')
		self.addButton.clicked.connect(self.addWidget)
		
		# flow layout, which will be inside the scroll area called scrollArea
		self.flowLayout = flowlayout.FlowLayout(self, 0, 10)

		# make a widget called
		self.scrollWidget = QtGui.QWidget()
		self.scrollWidget.setLayout(self.flowLayout)
		#set the borders around the scroll widget
		self.scrollWidget.setContentsMargins(10, 10, 10, 10)

		# scroll area
		self.scrollArea = QtGui.QScrollArea()
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setWidget(self.scrollWidget)
		
		self.scrollArea.setContentsMargins(0, 0, 0, 0)
		self.scrollWidget.setContentsMargins(0, 0, 0, 0)
		
		# main layout
		self.mainLayout = QtGui.QVBoxLayout()

		# add all main to the main vLayout
		self.mainLayout.addWidget(self.addButton)
		self.mainLayout.addWidget(self.scrollArea)
		
		self.setLayout(self.mainLayout)
		self.mainLayout.setContentsMargins(0, 0, 0, 0)

	def addWidget(self):
		#self.flowLayout.addWidget(SquareObject(self, self.style.PINK))
		self.flowLayout.addWidget(TaylorSquare.ItemObject(self, "IAmAFileNameBecauseIAmCool.html", "I am Path", "400.0kB" , "text/application", True))
		

class SetupWizard(QtGui.QWidget):

	def __init__(self, parent = None):
		super(SetupWizard, self).__init__()
		self.parent = parent
		self.setWindowTitle('Setup')   
		#set the window type to a dialog
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog)
		
		fontDatabase = QtGui.QFontDatabase()
		#fontfile = QtCore.QFile("resources/Roboto-Light-webfont.ttf")
		#fontDatabase.addApplicationFont(os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf")
		#os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf"
		palette = QtGui.QPalette()
		#palette.setColor(QtGui.QPalette.Foreground,QtGui.QColor("#FFFFFF"))
		
		exit=QtGui.QAction(self)
		self.connect(exit,QtCore.SIGNAL('triggered()'),QtCore.SLOT('close()'))
		
		topText = QtGui.QLabel('Setting Up Kissync')
		#http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
		font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
		topText.setFont(font)
		topText.setPalette(palette)
		topText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		#topText.setStyleSheet("color: #FFFFFF;")

		if not (sys.platform == 'win32'):
			loading = loadingwidget.Main()
			#this allows the squares to show properly, as the timing gets off sometimes
			loading.show()
			loading.hide()

		grid = QtGui.QGridLayout()
		
		#window size constraints
		self.setFixedSize(465, 325)
		
		spacer = QtGui.QWidget()
		spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		#file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		
		formwidget =  QtGui.QWidget()
		formgrid = QtGui.QFormLayout()
		formwidget.setLayout(formgrid)
		
		self.checkboxOfflineMode = QtGui.QCheckBox('Store All Files Offline', self)
		self.checkboxNotifications = QtGui.QCheckBox('Allow Desktop Notifications', self)
		font = QtGui.QFont("Roboto", 16, QtGui.QFont.Normal, False)
		self.checkboxOfflineMode.setFont(font)
		self.checkboxNotifications.setFont(font)
		self.checkboxNotifications.toggle()
		
		finishButton = QtGui.QPushButton('Finish Setup')
		finishButton.clicked.connect(self.saveSettings)
		
		formgrid.addRow(self.checkboxOfflineMode)
		formgrid.addRow(self.checkboxNotifications)
		formgrid.addRow(spacer)
		formgrid.addRow(finishButton)
		
		#add the objects to the grid
		grid.addWidget(spacer, 0, 0)
		grid.addWidget(spacer, 0, 2)
		grid.addWidget(topText, 0, 1)
		grid.addWidget(formwidget, 2, 1)
		if not (sys.platform == 'win32'):
			grid.addWidget(loading, 4, 1)
		grid.addWidget(spacer, 5, 1)
		#set the layout to grid layout
		self.setLayout(grid)
		self.centerOnScreen()
		
	def saveSettings(self):
		print self.checkboxOfflineMode.isChecked()
		if(self.checkboxOfflineMode.isChecked()):
			self.parent.config.set('LocalSettings', 'sync-offline', True)
		else:
			self.parent.config.set('LocalSettings', 'sync-offline', False)
		if(self.checkboxNotifications.isChecked()):
			self.parent.config.set('LocalSettings', 'notifications', True)
		else:
			self.parent.config.set('LocalSettings', 'notifications', False)
		
		self.parent.config.set('LocalSettings', 'first-run', False)
		
		with open('configuration.cfg', 'wb') as configfile:
				self.parent.config.write(configfile)
		self.parent.tray.notification("Kissync", "Welcome to Kissync Enterprise File Management")
		self.hide()
		
	def centerOnScreen (self):
		resolution = QtGui.QDesktopWidget().screenGeometry()
		self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
				(resolution.height() / 2) - (self.frameSize().height() / 2))

	def closeEvent(self, event):
		reply=QtGui.QMessageBox.question(self,'Setup Wizard',"Are you sure you want to exit?",QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
		if reply==QtGui.QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()
			self.parent.tray.notification("Kissync", "The user pressed cancel. Continuing the setup...")
			self.parent.show()
						
		
class TrayMenu(QtGui.QMenu):
	def __init__(self, parent=None):
		QtGui.QMenu.__init__(self)
		self.parent = parent

		notifyItem = QtGui.QAction('Show Notification', self)   
		notifyItem.triggered.connect(self.notification)

		exitItem = QtGui.QAction('&Exit', self)   
		exitItem.triggered.connect(QtCore.QCoreApplication.instance().quit)
		
		self.addAction(notifyItem)
		self.addAction(exitItem)
	
	def notification(self):
		self.parent.notification("Kissync", "hello")


class SystemTrayIcon(QtGui.QSystemTrayIcon):
	def __init__(self, parent=None):
		QtGui.QSystemTrayIcon.__init__(self, parent)
		self.parent = parent
		
		self.setIcon(QtGui.QIcon("icons/icon.xpm"))
		self.setToolTip(QtCore.QString('Kissync'))
		
		self.menu = TrayMenu(self)
		self.setContextMenu(self.menu)

	def notification(self, title, message):
		#enum MessageIcon { NoIcon, Information, Warning, Critical }
		if(self.parent.config.get('LocalSettings', 'notifications')):
			self.showMessage(title, message, QtGui.QSystemTrayIcon.NoIcon)
        
	def show(self):
		#QtCore.QTimer.singleShot(100, self.welcome)
		QtGui.QSystemTrayIcon.show(self)
		
			
class MainWindow(QtGui.QWidget):
	def __init__(self, parent = None):
		super(MainWindow, self).__init__(parent)
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
			self.config.set('LocalSettings', 'network-timeout', 15)
			self.config.set('LocalSettings', 'notifications', True)
			self.config.set('LocalSettings', 'sync-offline', False)
			self.config.set('LocalSettings', 'sync-dir', None)
			with open('configuration.cfg', 'wb') as configfile:
				self.config.write(configfile)
		else:
			self.config.read('configuration.cfg')
		
		#connects directly to the smartfile api, but relies upon self.authenticator	to create
		self.smartfile = None #we don't want to init yet, so we can handle errors later on login
		#runs the authentication process that connects self.smartfile with a smartfile client
		self.authenticator = Authenticator(self) #login in
		#tray icon
		self.tray = SystemTrayIcon(self) #tray icon
		self.tray.show()
		#login screen
		self.loginwindow = LoginWindow(self)
		#setup window for initial user configuration
		self.setupwizard = SetupWizard(self)
		self.setupwizard.show()
		#file database
		self.database = FileDatabase(self)
		#file system watcher
		#self.filewatcher = watcher.Watcher(self)
		
		
		
		#################MAIN WINDOW GUI#####################
		self.breadcrumb = breadcrumb.BreadCrumb(self)	
		self.fileview = FileView(self)	
		#initialize all neccessary objects that will talk to MainWindow and each other
		
		self.setWindowTitle('Keep It Simple Sync')  
		self.displayFont = QtGui.QFont()
		#self.setStyleSheet("background-color: #222222; ") 
		self.setGeometry(400, 200, 1000, 500)
		
		fontDatabase = QtGui.QFontDatabase()
		#fontfile = QtCore.QFile("resources/Roboto-Light-webfont.ttf")
		#fontDatabase.addApplicationFont(os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf")
		#os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf"
		palette = QtGui.QPalette()
		#palette.setColor(QtGui.QPalette.Foreground,QtGui.QColor("#FFFFFF"))
		
		topText = QtGui.QLabel('Kissync')
		#http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
		font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
		topText.setFont(font)
		topText.setPalette(palette)
		#topText.setStyleSheet("color: #FFFFFF;")
		
		grid = QtGui.QGridLayout()
		grid.setContentsMargins(0, 0, 0, 0)
		grid.addWidget(topText)
		grid.addWidget(self.breadcrumb)
		grid.addWidget(self.fileview)
		self.setLayout(grid)
		self.show()


if __name__ == "__main__":
	
	app = QtGui.QApplication(sys.argv)
	mainwindow = MainWindow()
	sys.exit(app.exec_())
