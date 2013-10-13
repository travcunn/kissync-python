#!/bin/env python

import os
import platform
import sys
import webbrowser

from app.core.common import is_latest_version
from PySide import QtGui
from tendo.singleton import SingleInstance

from app.core.auth import Authenticator
from app.core.configuration import Configuration
from app.sync.synchronizer import Synchronizer

from ui.loginwindow import LoginWindow
from ui.setupwizard import SetupWizard
from ui.systemtray import SystemTray


version = "0.1"


class Main(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        # Set the version
        self.version = version

        # Check for updates
        self.checkForUpdates()

        self.syncDir = os.path.join(os.path.expanduser("~"), "Smartfile")
        self.settingsDir = self.settingsDirectory()[0]
        self.settingsFile = self.settingsDirectory()[1]

        self.directorySetup()# create the directories that will be needed

        self.configuration = Configuration(self.settingsFile)  # initialize the configuration

        self.smartfile = None  # this will be initiated later in Authenticator()

        self.setupwizard = SetupWizard(self)  # initiate setup wizard UI instead of creating it when needed
        self.loginwindow = LoginWindow(self)  # initiate login window UI instead of creating it when needed
        self.tray = SystemTray(self)  # initiate the system tray
        self.authenticator = Authenticator(self)  # initiate and runs the login on initialization
        self.authenticator.login.connect(self.login)
        self.authenticator.done.connect(self.start)
        self.authenticator.setup.connect(self.setup)
        self.authenticator.neterror.connect(self.neterror)
        self.authenticator.start()

        #################MAIN WINDOW GUI#####################
        self.setWindowTitle('SmartFile Folder Sync')
        self.displayFont = QtGui.QFont()
        self.setGeometry(200, 200, 870, 600)
        self.setMinimumSize(900, 600)

        topText = QtGui.QLabel('SmartFile Folder Sync')
        font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
        topText.setFont(font)

        #Title Text Widget
        self.titlewidget = QtGui.QWidget()
        self.titlelayout = QtGui.QGridLayout()
        self.titlelayout.addWidget(topText)
        self.titlewidget.setLayout(self.titlelayout)
        self.titlewidget.setMaximumHeight(70)

        self.grid = QtGui.QGridLayout()
        self.grid.setContentsMargins(0, 10, 10, 0)
        self.setLayout(self.grid)

    def start(self):
        """Called if the authentication is successful"""
        self.synchronizer = Synchronizer(self)  # initiate the synchronizer
        self.synchronizer.start()
        self.tray.onLogin()

    def login(self, qturl):
        """Opens the login window"""
        self.loginwindow.htmlView.load(qturl)
        self.loginwindow.show()

    def setup(self):
        """First Run: Called if the authentication is successful"""
        self.setupwizard.show()
        #self.tray.notification("Smartfile Setup", "Please complete the setup to start using Kissync")

    def neterror(self):
        QtGui.QMessageBox.critical(self, 'SmartFile Error', 'There was an error while connecting to SmartFile.', 1)
        self.exit()

    def checkForUpdates(self):
        """Checks the current version with the latest from the server"""
        try:
            if (is_latest_version(version) == False):
                self.updateNotify()
        except:
            self.neterror()

    def updateNotify(self):
        """Display a notification when an update is available"""
        updateReply = QtGui.QMessageBox.question(self, 'SmartFile Update',
            'An update is available. Would you like to download now?',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.Yes)

        # Open a web browser if the user selects yes
        if updateReply == QtGui.QMessageBox.Yes:
            webbrowser.open("https://www.kissync.com/download", new=2)

    def directorySetup(self):
        """Checks for sync and settings folder and creates if needed"""
        if not os.path.exists(self.settingsDir):
            os.makedirs(self.settingsDir)

        if not os.path.exists(self.syncDir):
            os.makedirs(self.syncDir)

    def settingsDirectory(self):
        if platform.system() == 'Windows':
            app_dir = os.path.join(
                os.getenv('appdata', os.path.expanduser('~')), 'Smartfile'
            )
            settings_dir = os.path.join(
                os.getenv('appdata', os.path.expanduser('~')), 'Smartfile', 'config.cfg'
            )
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)
        else:
            app_dir = os.path.join(os.path.expanduser("~"), ".smartfile")
            settings_dir = os.path.join(os.path.expanduser("~"), ".smartfile", "config.cfg")
        return app_dir, settings_dir

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def exit(self):
        try:
            self.tray.hide()
        except:
            # main.exit() could be called before tray is instanciated
            pass
        #TODO: clean up the exit
        os._exit(1)


if __name__ == "__main__":
    me = SingleInstance()
    app = QtGui.QApplication(sys.argv)

    mainwindow = Main()

    sys.exit(app.exec_())
