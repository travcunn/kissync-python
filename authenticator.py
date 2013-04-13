from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
from authbrowser import AuthBrowser


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
