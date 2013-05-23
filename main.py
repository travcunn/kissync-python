import os
import sys
from PyQt4 import QtGui
from tendo.singleton import SingleInstance

from authenticator import Authenticator
from configuration import Configuration
from filedatabase import FileDatabase
from loginwindow import LoginWindow
from setupwizard import SetupWizard
from style import KissyncStyle
from tray import SystemTrayIcon

import watcher


class Main(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.style = KissyncStyle()

        self.syncDirectory = os.path.join(os.path.expanduser("~"), "Kissync")
        self.workingDirectory = os.path.join(os.path.expanduser("~"), ".kissync")
        self.settingsFile = os.path.join(os.path.expanduser("~"), ".kissync", "configuration.cfg")

        self.directorySetup()

        self.configuration = Configuration(self.settingsFile)

        #################MAIN WINDOW GUI#####################
        self.setWindowTitle('Keep It Simple Sync')
        self.displayFont = QtGui.QFont()
        self.setGeometry(200, 200, 870, 600)
        self.setMinimumSize(900, 600)

        palette = QtGui.QPalette()
        #palette.setColor(QtGui.QPalette.Foreground,QtGui.QColor("#FFFFFF"))

        #Title Text Font
        topText = QtGui.QLabel('Kissync Enterprise')
        #http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
        font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
        topText.setFont(font)
        topText.setPalette(palette)

        #Title Text Widget
        self.titlewidget = QtGui.QWidget()
        self.titlelayout = QtGui.QGridLayout()
        self.titlelayout.addWidget(topText)
        self.titlewidget.setLayout(self.titlelayout)
        self.titlewidget.setMaximumHeight(70)

        self.grid = QtGui.QGridLayout()
        self.grid.setContentsMargins(0, 10, 10, 0)
        self.setLayout(self.grid)

        #connects directly to the smartfile api, but relies upon self.authenticator	to create
        self.smartfile = None  # we don't want to init yet, so we can handle errors later on login
        #login screen
        self.database = FileDatabase(self)
        #setup window for initial user configuration
        self.setupwizard = SetupWizard(self)
        self.loginwindow = LoginWindow(self)
        #runs the authentication process that connects self.smartfile with a smartfile client
        #self.tray = SystemTrayIcon(self)  # tray icon

        self.tray = SystemTrayIcon(self)
        self.tray.show()

        self.authenticator = Authenticator(self)  # login in

    def start(self):
        self.filewatcher = watcher.Watcher(self)
        self.filewatcher.start()

        #self.synchronizer = Synchronizer(self)
        #self.synchronizer.start()

        #self.rt = RefreshThread(self)
        #self.rt.start()

    def directorySetup(self):
        if not os.path.exists(self.workingDirectory):
            os.makedirs(self.workingDirectory)

        if not os.path.exists(self.syncDirectory):
            os.makedirs(self.syncDirectory)

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
