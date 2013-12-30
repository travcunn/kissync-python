#!/bin/env python

import argparse
import logging
import os
import platform
import subprocess
import sys
import webbrowser

from PySide import QtGui
from tendo.singleton import SingleInstance

from app.core.auth import Authenticator
import app.core.common as common
from app.core.configuration import Configuration
from app.sync.syncengine import SyncThread

from ui.loginwindow import LoginWindow
from ui.setupwizard import SetupWizard
from ui.systemtray import SystemTray

"""
# hide logs from requests and oauthlib
logs = [logging.getLogger("requests"), logging.getLogger("oauthlib")]
for log in logs:
    log.setLevel(logging.WARNING)
"""

version = "0.23"


class Main(QtGui.QWidget):
    def __init__(self):
        super(Main, self).__init__()

        # Set the version
        self.version = version

        # Check for updates
        self.checkForUpdates()

        self.sync_dir = os.path.join(os.path.expanduser("~"), "Smartfile")
        self.settingsDir = common.settingsDirectory()
        self.settingsFile = common.settingsFile()

        self.directorySetup() # Make sure proper directories are created

        self.configuration = Configuration(self.settingsFile)

        self.setupwizard = SetupWizard(self)  # initiate setup wizard UI
        self.loginwindow = LoginWindow(self)  # initiate login window UI
        self.tray = SystemTray(self)

        self.authenticator = Authenticator(self)
        self.authenticator.login.connect(self.login)
        self.authenticator.done.connect(self.start)
        self.authenticator.setup.connect(self.setup)
        self.authenticator.neterror.connect(self.neterror)
        self.authenticator.start()

        if self.configuration.get('LocalSettings', 'autostart'):
            common.create_shortcut()
        else:
            common.delete_shortcut()

    def start(self):
        """ Called if authentication is successful. """
        self.synchronizer = SyncThread(self.api, self.sync_dir)
        self.synchronizer.start()
        self.tray.onLogin()

    def login(self, qturl):
        """ Opens the login window. """
        self.loginwindow.htmlView.load(qturl)
        self.loginwindow.show()

    def setup(self):
        """ First Run: Called if the authentication is successful. """
        self.setupwizard.show()

    def neterror(self):
        QtGui.QMessageBox.critical(self, 'SmartFile Error', 
                'There was an error while connecting to SmartFile.', 1)
        self.exit()

    def checkForUpdates(self):
        """ Checks the current version with the latest from the server. """
        try:
            if not common.latest_version(version):
                self.updateNotify()
        except:
            self.neterror()

    def updateNotify(self):
        """ Display a notification when an update is available. """
        updateReply = QtGui.QMessageBox.question(self, 'SmartFile Update',
            'An update is available. Would you like to download now?',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.Yes)

        # Open a web browser if the user selects yes
        if updateReply == QtGui.QMessageBox.Yes:
            webbrowser.open("https://www.kissync.com/download", new=2)

    def directorySetup(self):
        """ Checks for sync and settings folder and creates if needed. """
        if not os.path.exists(self.settingsDir):
            os.makedirs(self.settingsDir)

        if not os.path.exists(self.sync_dir):
            os.makedirs(self.sync_dir)

    def openSyncFolder(self):
        """ Opens a file browser depending on the system. """
        if platform.system() == 'Darwin':
            subprocess.call(['open', '--', self.sync_dir])
        elif platform.system() == 'Linux':
            subprocess.call(['gnome-open', self.sync_dir])
        elif platform.system() == 'Windows':
            subprocess.call(['explorer', self.sync_dir])

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def exit(self):
        try:
            self.tray.hide()
        except:
            pass
        #TODO: clean up the exit
        os._exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SmartFile Sync')
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)


    me = SingleInstance()
    app = QtGui.QApplication(sys.argv)

    mainwindow = Main()

    sys.exit(app.exec_())
