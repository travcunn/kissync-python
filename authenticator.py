from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
from authbrowser import AuthBrowser
from smartfile import OAuthClient

import os, webbrowser


class Authenticator(object):
	def __init__(self, parent = None):
		super(Authenticator, self).__init__()
		self.parent = parent 
		
		if not (os.name == 'nt'):
			self.htmlView = AuthBrowser(self)
			self.go()
		else:
			self.goWindows() # #thingsnottosayoutloud
                
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
	
	def goWindows(self):
		try:
			self.parent.smartfile = OAuthClient("zGSJpILRq2889Ne2bPBdEmEZLsRHpe", "KOb97irJG84PJ8dtEkoYt2Kqwz3VJa")
		except:
			self.networkerror()
		else:
			self.parent.smartfile.get_request_token()
			webbrowser.open(self.parent.smartfile.get_authorization_url())
			text, ok = QtGui.QInputDialog.getText(self.parent, 'Kissync Verification', 'Paste the verifier here:')
        
			if not ok:
				text = None
				os._exit()
			else:
				try:
					self.parent.smartfile.get_access_token(None, text)
					
				except:
					#something happened after logging in successfully, and is not sucessful now
					quit_msg = "Wrong verification code. Try again?"
					reply = QtGui.QMessageBox.question(self.parent, 'Kissync Login', 
						quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

					if reply == QtGui.QMessageBox.Yes:
						self.goWindows()
					else:
						os._exit()
				else:
					#logged in successfully
					userpass, ok = QtGui.QInputDialog.getText(self.parent, 'Kissync', 'Reenter your password:')
					
					if not ok:
						userpass = None
					else:
						tree = self.parent.smartfile.get('/whoami', '/')
						if 'site' in tree:
							username = tree['site']['name'].encode("utf-8")
						self.parent.config.set('Login', 'username', username)
						self.parent.config.set('Login', 'password', userpass)
						with open(self.parent.settingsFile, 'wb') as configfile:
							self.parent.config.write(configfile)
					self.success()
				
	
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
			self.parent.tray.notification("Kissync Setup", "Please complete the setup to start using Kissync")
		else:
			self.parent.start()
			#self.parent.filewatcher.start()
