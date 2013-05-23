import platform
import subprocess
import sys
from PyQt4 import QtGui, QtCore


class SystemTrayIcon(QtGui.QSystemTrayIcon):

    def __init__(self, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        self.parent = parent
        menu = QtGui.QMenu(parent)
        self.setIcon(QtGui.QIcon("icons/menuicon.png"))
        self.setToolTip(QtCore.QString('Kissync'))

        startAction = menu.addAction("Browse Kissync Folder")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.openSyncFolder)
        self.setContextMenu(menu)

        menu.addSeparator()

        exitAction = menu.addAction("Exit")
        self.connect(exitAction, QtCore.SIGNAL("triggered()"), self.parent.exit)
        self.setContextMenu(menu)

        #TODO: Create a method that cycles through loading images for the system tray on sync
        #self.loadingIcon1 = QtGui.QIcon("icons/menuicon1.png")
        #self.loadingIcon2 = QtGui.QIcon("icons/menuicon2.png")
        #self.loadingIcon3 = QtGui.QIcon("icons/menuicon3.png")
        #self.loadingIcon4 = QtGui.QIcon("icons/menuicon4.png")

    #def loading(self):
        #self.setIcon(self.loadingIcon1)

    def openSyncFolder(self):
        if platform.system() == 'Darwin':
            subprocess.call(['open', '--', self.parent.syncDir])
        elif platform.system() == 'Linux':
            subprocess.call(['gnome-open', self.parent.syncDir])
        elif platform.system() == 'Windows':
            subprocess.call(['explorer', self.parent.syncDir])

    def exit(self):
        sys.exit(0)

    def notification(self, title, message):
        #enum MessageIcon { NoIcon, Information, Warning, Critical }
        if(self.parent.configuration.get('LocalSettings', 'notifications')):
            self.showMessage(title, message, QtGui.QSystemTrayIcon.NoIcon)
