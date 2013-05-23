import os
import sys
from PyQt4 import QtGui
from tendo.singleton import SingleInstance

from authenticator import Authenticator
from configuration import Configuration
from filedatabase import FileDatabase
from watcher import Watcher

from ui.loginwindow import LoginWindow
from ui.setupwizard import SetupWizard
from ui.style import KissyncStyle
from ui.tray import SystemTrayIcon


class Main(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.style = KissyncStyle()

        self.syncDir = os.path.join(os.path.expanduser("~"), "Kissync")
        self.settingsDir = os.path.join(os.path.expanduser("~"), ".kissync")
        self.settingsFile = os.path.join(os.path.expanduser("~"), ".kissync", "configuration.cfg")

        self.directorySetup()  # create the directories that will be needed

        self.configuration = Configuration(self.settingsFile)  # initialize the configuration

        self.smartfile = None  # this will be initiated later in Authenticator()
        self.database = FileDatabase(self)  # initiate local and remote file database
        self.setupwizard = SetupWizard(self)  # initiate setup wizard UI instead of creating it when needed
        self.loginwindow = LoginWindow(self)  # initiate login window UI instead of creating it when needed
        self.tray = SystemTrayIcon(self)  # initiate the system tray
        self.tray.show()

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

        self.authenticator = Authenticator(self)  # initiate and runs the login on initialization

    def start(self):
        '''Called if the authentication is successful'''
        self.localFileWatcher = Watcher(self)
        self.localFileWatcher.start()

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
