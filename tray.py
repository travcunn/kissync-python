import os
from PyQt4 import QtCore, QtGui


class TrayMenu(QtGui.QMenu):
    def __init__(self, parent=None):
        QtGui.QMenu.__init__(self)
        self.parent = parent

        openItem = QtGui.QAction('Open Kissync Browser', self)
        openItem.triggered.connect(self.openmain)

        exitItem = QtGui.QAction('&Exit', self)
        exitItem.triggered.connect(self.exit)

        self.addAction(openItem)
        self.addAction(exitItem)

    def openmain(self):
        self.parent.parent.show()

    def notification(self):
        self.parent.notification("Kissync", "hello")

    def exit(self):
        self.parent.parent.exit()


class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        self.parent = parent
        self.setIcon(QtGui.QIcon(os.path.dirname(os.path.realpath(__file__)) + "/icons/icon.xpm"))
        self.setToolTip(QtCore.QString('Kissync'))

        self.menu = TrayMenu(self)
        self.setContextMenu(self.menu)
        self.show()

    def notification(self, title, message):
        #enum MessageIcon { NoIcon, Information, Warning, Critical }
        if(self.parent.configuration.get('LocalSettings', 'notifications')):
            self.showMessage(title, message, QtGui.QSystemTrayIcon.NoIcon)

    def show(self):
        #QtCore.QTimer.singleShot(100, self.welcome)
        QtGui.QSystemTrayIcon.show(self)
