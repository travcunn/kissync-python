import os
import sys
from PyQt4 import QtGui
from tendo.singleton import SingleInstance

from core.auth import Authenticator
from core.configuration import Configuration

from sync.synchronizer import Synchronizer
from sync.watcher import Watcher

from ui.loginwindow import LoginWindow
from ui.setupwizard import SetupWizard
from ui.style import KissyncStyle
from ui.systemtray import SystemTray


class Main(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.style = KissyncStyle()

        self.syncDir = os.path.join(os.path.expanduser("~"), "Kissync")
        self.settingsDir = os.path.join(os.path.expanduser("~"), ".kissync")
        self.settingsFile = os.path.join(os.path.expanduser("~"), ".kissync", "config.cfg")

        self.directorySetup()  # create the directories that will be needed

        self.configuration = Configuration(self.settingsFile)  # initialize the configuration

        self.smartfile = None  # this will be initiated later in Authenticator()
        self.synchronizer = Synchronizer(self)  # initiate the synchronizer
        self.localFileWatcher = Watcher(self)  # initiate the file system watcher

        self.setupwizard = SetupWizard(self)  # initiate setup wizard UI instead of creating it when needed
        self.loginwindow = LoginWindow(self)  # initiate login window UI instead of creating it when needed
        self.tray = SystemTray(self)  # initiate the system tray
        self.authenticator = Authenticator(self)  # initiate and runs the login on initialization

        #################MAIN WINDOW GUI#####################
        self.setWindowTitle('Keep It Simple Sync')
        self.displayFont = QtGui.QFont()
        self.setGeometry(200, 200, 870, 600)
        self.setMinimumSize(900, 600)

        topText = QtGui.QLabel('Kissync Enterprise')
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
        '''Called if the authentication is successful'''
        self.localFileWatcher.start()
        self.synchronizer.start()

    def directorySetup(self):
        '''Checks for sync and settings folder and creates if needed'''
        if not os.path.exists(self.settingsDir):
            os.makedirs(self.settingsDir)

        if not os.path.exists(self.syncDir):
            os.makedirs(self.syncDir)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def exit(self):
        os._exit(-1)


if __name__ == "__main__":
    me = SingleInstance()
    app = QtGui.QApplication(sys.argv)

    mainwindow = Main()

    sys.exit(app.exec_())
