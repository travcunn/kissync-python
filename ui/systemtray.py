import math
import webbrowser

from PySide import QtGui, QtCore

from ui.settingswindow import SettingsWindow


class SystemTray(QtGui.QSystemTrayIcon):
    def __init__(self, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        self.parent = parent

        #menu before logging into Smartfile
        self.menu = QtGui.QMenu(parent)
        self.setIcon(QtGui.QIcon(":/menuicon.png"))
        self.setToolTip('SmartFile Sync')

        startAction = self.menu.addAction("Open SmartFile Folder")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.parent.openSyncFolder)

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

    def openWebsite(self):
        url = "https://app.smartfile.com"
        webbrowser.open(url,new=2)

    def openSettings(self):
        """Opens the settings window and brings it into focus"""
        self.settingsWindow.showSettings()

    def onLogin(self):
        """
        After auth finishes, create the settings window
        and update the system tray to display disk usage quota
        """
        self.settingsWindow = SettingsWindow(self.parent)  # also initiate the settings window for quick show/hide
        whoami = self.parent.smartfile.get("/whoami/")
        usedBytes = int(whoami['site']['quota']['disk_bytes_tally'])
        bytesLimit = int(whoami['site']['quota']['disk_bytes_limit'])
        percentUsed = usedBytes / bytesLimit

        spaceLimit = bytesLimit
        if spaceLimit < 1024:
            measurement = "bytes"
        elif spaceLimit < int(math.pow(1024, 2)):
            spaceLimit /= 1024
            measurement = "KB"
        elif spaceLimit < int(math.pow(1024, 3)):
            spaceLimit /= int(math.pow(1024, 2))
            measurement = "MB"
        else:
            spaceLimit /= int(math.pow(1024, 3))
            measurement = "GB"

        #menu after logging into Smartfile
        self.menu = QtGui.QMenu(self.parent)

        self.setIcon(QtGui.QIcon(":/menuicon.png"))
        self.setToolTip('SmartFile Sync')

        startAction = self.menu.addAction("Open SmartFile Folder")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.parent.openSyncFolder)

        openWebsite = self.menu.addAction("Launch SmartFile Website")
        self.connect(openWebsite, QtCore.SIGNAL("triggered()"), self.openWebsite)

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
        """Shows a system tray notification"""
        if self.parent.configuration.get('LocalSettings', 'notifications'):
            self.showMessage(title, message, QtGui.QSystemTrayIcon.NoIcon)
