import os
import sys
from PySide import QtGui
from tendo.singleton import SingleInstance

from app.core.auth import Authenticator
from app.core.configuration import Configuration

from app.sync.synchronizer import Synchronizer

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
        self.sync = None

        self.setupwizard = SetupWizard(self)  # initiate setup wizard UI instead of creating it when needed
        self.loginwindow = LoginWindow(self)  # initiate login window UI instead of creating it when needed
        self.tray = SystemTray(self)  # initiate the system tray
        self.authenticator = Authenticator(self)  # initiate and runs the login on initialization
        self.authenticator.login.connect(self.login)
        self.authenticator.done.connect(self.start)
        self.authenticator.setup.connect(self.setup)
        self.authenticator.start()

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
        self.synchronizer = Synchronizer(self)  # initiate the synchronizer
        self.synchronizer.start()
        self.tray.onLogin()

    def login(self, qturl):
        '''Opens the login window'''
        self.loginwindow.htmlView.load(qturl)
        self.loginwindow.show()

    def setup(self):
        '''First Run: Called if the authentication is successful'''
        self.setupwizard.show()
        self.tray.notification("Kissync Setup", "Please complete the setup to start using Kissync")

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
        self.tray.hide()
        os._exit(-1)


if __name__ == "__main__":
    me = SingleInstance()
    app = QtGui.QApplication(sys.argv)

    mainwindow = Main()

    sys.exit(app.exec_())
