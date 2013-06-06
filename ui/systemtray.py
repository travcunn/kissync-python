import math
import platform
import subprocess
from PySide import QtGui, QtCore

from ui.settingswindow import SettingsWindow


class SystemTray(QtGui.QSystemTrayIcon):

    def __init__(self, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        self.parent = parent

        #menu before logging into Smartfile
        self.menu = QtGui.QMenu(parent)
        #TODO: Update this resource to be packaged with other resources
        self.setIcon(QtGui.QIcon("icons/icon.ico"))
        self.setToolTip('Kissync')

        startAction = self.menu.addAction("Open Kissync Folder")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.openSyncFolder)

        startingup = self.menu.addAction("Connecting...")
        startingup.setEnabled(False)

        self.menu.addSeparator()

        exitAction = self.menu.addAction("Exit")
        self.connect(exitAction, QtCore.SIGNAL("triggered()"), self.parent.exit)

        self.setContextMenu(self.menu)
        self.show()

        #TODO: Create a method that cycles through loading images for the system tray on sync
        #self.loadingIcon1 = QtGui.QIcon("icons/menuicon1.png")
        #self.loadingIcon2 = QtGui.QIcon("icons/menuicon2.png")
        #self.loadingIcon3 = QtGui.QIcon("icons/menuicon3.png")
        #self.loadingIcon4 = QtGui.QIcon("icons/menuicon4.png")

    #def loading(self):
        #self.setIcon(self.loadingIcon1)

    def openSyncFolder(self):
        '''Opens a file browser depending on the system'''
        if platform.system() == 'Darwin':
            subprocess.call(['open', '--', self.parent.syncDir])
        elif platform.system() == 'Linux':
            subprocess.call(['gnome-open', self.parent.syncDir])
        elif platform.system() == 'Windows':
            subprocess.call(['explorer', self.parent.syncDir])

    def openSettings(self):
        '''Opens the settings window and brings it into focus'''
        self.settingsWindow.showSettings()

    def onLogin(self):
        '''
        After auth finishes, create the settings window
        and update the system tray to display disk usage quota
        '''
        self.settingsWindow = SettingsWindow(self.parent)  # also initiate the settings window for quick show/hide
        whoami = self.parent.smartfile.get("/whoami/")
        usedBytes = int(whoami['site']['quota']['disk_bytes_tally'])
        bytesLimit = int(whoami['site']['quota']['disk_bytes_limit'])
        percentUsed = usedBytes / bytesLimit

        spaceLimit = bytesLimit
        if(spaceLimit < 1024):
            measurement = "bytes"
        elif(spaceLimit < int(math.pow(1024, 2))):
            spaceLimit = spaceLimit / 1024
            measurement = "KB"
        elif(spaceLimit < int(math.pow(1024, 3))):
            spaceLimit = spaceLimit / int(math.pow(1024, 2))
            measurement = "MB"
        else:
            spaceLimit = spaceLimit / int(math.pow(1024, 3))
            measurement = "GB"

        #menu after logging into Smartfile
        self.menu = QtGui.QMenu(self.parent)
        #TODO: Update this resource to be packaged with other resources
        self.setIcon(QtGui.QIcon("icons/menuicon.png"))
        self.setToolTip('Kissync')

        startAction = self.menu.addAction("Open Kissync Folder")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.openSyncFolder)

        self.menu.addSeparator()

        quota = self.menu.addAction("%.1f%s of %s%s used" % (percentUsed, "%", spaceLimit, measurement))
        quota.setEnabled(False)

        self.menu.addSeparator()

        settingsAction = self.menu.addAction("Settings")
        self.connect(settingsAction, QtCore.SIGNAL("triggered()"), self.openSettings)

        self.menu.addSeparator()

        exitAction = self.menu.addAction("Exit")
        self.connect(exitAction, QtCore.SIGNAL("triggered()"), self.parent.exit)

        self.setContextMenu(self.menu)

    def notification(self, title, message):
        '''Shows a system tray notification'''
        if(self.parent.configuration.get('LocalSettings', 'notifications')):
            self.showMessage(title, message, QtGui.QSystemTrayIcon.NoIcon)
