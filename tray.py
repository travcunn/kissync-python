from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg


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
