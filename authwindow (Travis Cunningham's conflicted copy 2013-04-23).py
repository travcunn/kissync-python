import os, sys, urllib2
from smartfile import OAuthClient
from PyQt4 import QtCore, QtGui, QtWebKit
from bs4 import BeautifulSoup

import loadingwidget

class LoginWindow(QtGui.QWidget):

	def __init__(self):
		super(LoginWindow, self).__init__()
		self.setWindowTitle('Login to SmartFile')   
		
		fontDatabase = QtGui.QFontDatabase()
		#fontfile = QtCore.QFile("resources/Roboto-Light-webfont.ttf")
		fontDatabase.addApplicationFont(os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf")
		os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf"
		palette = QtGui.QPalette()
		#palette.setColor(QtGui.QPalette.Foreground,QtGui.QColor("#FFFFFF"))
		
		topText = QtGui.QLabel('kisSync')
		#http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
		font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
		topText.setFont(font)
		topText.setPalette(palette)
		topText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		#topText.setStyleSheet("color: #FFFFFF;")
		topText.hide()
		
		self.loginText = QtGui.QLabel('Login using your SmartFile account:')
		self.loginText.setStyleSheet("font-size: 16px; font-weight : bold;")
		self.loginText.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.networkErrorText = QtGui.QLabel('Network connection error')
		self.networkErrorText.setStyleSheet("font-size: 24px; font-weight : bold;")
		self.networkErrorText.setAlignment(QtCore.Qt.AlignVCenter)
		self.networkErrorText.hide()
		
		self.retryButton = QtGui.QPushButton('Retry')
		self.retryButton.clicked.connect(self.startbrowse)
		self.retryButton.setSizePolicy ( QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
		self.retryButton.hide()
		
		# http://zetcode.com/tutorials/pyqt4/layoutmanagement/
		#http://stackoverflow.com/questions/9624281/how-to-associate-a-horizontal-scrollbar-to-multiple-groupbox
		#create a layout, instantiate the grid layout object
		grid = QtGui.QGridLayout()
		#self.setStyleSheet("QWidget {background-color:white}")
		
		#window size constraints
		self.setFixedSize(450, 600)
		
		#instantiate the browser object
		self.htmlView = Browser(self)
		
		#instantiate the loading widget object
		self.loading = loadingwidget.Main()
		
		spacer = QtGui.QWidget()
		spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

		#scrollArea = QtGui.QScrollArea() 
		#scrollArea.setWidget(self.htmlView)  
		#change the scroll area to get rid of scrollbars
		#scrollArea.setWidgetResizable(True)
		
		#add the objects to the grid
		grid.addWidget(spacer, 0, 0)
		grid.addWidget(spacer, 0, 2)
		grid.addWidget(topText, 0, 1)
		grid.addWidget(spacer, 1, 1)
		grid.addWidget(self.loginText, 2, 1)
		grid.addWidget(self.loading, 3, 1)
		grid.addWidget(self.networkErrorText, 4, 1)
		grid.addWidget(self.retryButton, 5, 1)
		grid.addWidget(self.htmlView, 6, 1)
		grid.addWidget(spacer, 7, 0)
		grid.addWidget(spacer, 8, 2)
		#set the layout to grid layout
		self.setLayout(grid)
		
		self.startbrowse()

	def browse(self):
		authenticator = AuthenticationClient()
		self.htmlView.load(QtCore.QUrl(authenticator.get_auth_url()))
		#self.htmlView.setHtml(newLoginContents)
		#hide the widget contents until the page loads, to add a loading html view
		self.htmlView.hide()
	
	def networkerror(self):
		self.htmlView.hide()
		self.loginText.hide()
		self.networkErrorText.show()
		self.retryButton.show()
	
	def startbrowse(self):
		self.loginText.hide()
		self.networkErrorText.hide()
		self.retryButton.hide()
		self.browse()

class Browser(QtWebKit.QWebView):
	def __init__(self, parent):
		self.parent = parent
		QtWebKit.QWebView.__init__(self)
		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.titleChanged.connect(self._pageloadinc)
		self.loadStarted.connect(self._hideview)
		self.loadFinished.connect(self._result_available)
		self.timer = QtCore.QTimeLine()
		self.pageloads = 0
		self.isdone = 0	

	def _result_available(self, ok):
		frame = self.page().mainFrame()
		soup = BeautifulSoup(unicode(frame.toHtml()).encode('utf-8'))
		try:
			print soup.find(id="id_verifier").get("value")
		except:
			if(self.pageloads >= 1):
				try:
					soup.find(id="right-tabs").contents
				except:
					pass
				else:
					self.isdone = 1
					self.parent.hide()
		else:
			self.isdone = 1
			self.parent.hide()
		if(self.isdone == 0):
			self.parent.loginText.show()
			self.parent.htmlView.show()
			self.parent.loading.hide()
		
		self.timer.stop()
			
		#print unicode(frame.toHtml()).encode('utf-8')
		#show the webpage after it loads completely
		#self.parent.htmlView.show()
	
	def _pageloadinc(self, ok):
		soup = BeautifulSoup(unicode(self.page().mainFrame().toHtml()).encode('utf-8'))
		try:
			if not(soup.title.string == "SmartFile"):
				self.pageloads = self.pageloads + 1
		except:
			pass
		self.parent.htmlView.show()
		self.parent.htmlView.hide()
		self.parent.loginText.hide()

	def _hideview(self):
		self.parent.htmlView.hide()
		self.parent.loginText.hide()
		self.parent.loading.show()
		self.pagetimer()
	
	def pagetimer(self):
		#starts up a page timer, so after 30 seconds, we can give a network error
		self.timer.valueChanged.connect(self.netwatch)
		self.timer.setDuration(15000)
		self.timer.start()
	
	def netwatch(self, value):
		if (value == 1.0):
			self.stop()
			self.parent.networkerror()
	
        
class AuthenticationClient(object):
	
	def __init__(self):
		print "Loading the OAuth client..."
		self.api = OAuthClient("Oft45O8bsR6nJm7tO9Ppwj76KSODFt", "1Um8yXH5sb2JyIbzl3CKrG9WhlFYmX")
	
	def get_auth_url(self):
		try:
			self.api.get_request_token()
			auth_url = self.api.get_authorization_url()
			print "Sending browser to: " + auth_url
			return auth_url
		except:
			print "There was an error loading the SmartFile OAuth authentication"
			
	#add the other OAuth methods here

if __name__ == "__main__":

	app = QtGui.QApplication(sys.argv)
	loginwindow = LoginWindow()
	loginwindow.show()
	sys.exit(app.exec_())
