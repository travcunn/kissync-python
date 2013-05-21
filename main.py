import os
import platform
import subprocess
import sys
from PyQt4 import QtCore, QtGui
from tendo.singleton import SingleInstance

from accountwidget import AccountWidget
from authenticator import Authenticator
from configuration import Configuration
from filebrowsergui import FileBrowserGUI
from filedatabase import FileDatabase
from filedatabase import Synchronizer
from filedatabase import RefreshThread
from loginwindow import LoginWindow
from setupwizard import SetupWizard
from style import KissyncStyle

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

        #self.filewatcher = watcher.Watcher(self)

    def start(self):
        self.filebrowsergui = FileBrowserGUI(self)
        self.accountwidget = AccountWidget(self)
        self.grid.addWidget(self.titlewidget, 0, 0)
        self.grid.addWidget(self.accountwidget, 0, 1, 1, 1, QtCore.Qt.AlignRight)
        self.grid.addWidget(self.filebrowsergui, 1, 0, 1, 2)

        #self.database.generateAuthHash()
        #self.database.indexLocalFiles()
        #self.database.loadRemoteListingFile()

        #self.filewatcher = watcher.Watcher(self)

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


class SystemTrayIcon(QtGui.QSystemTrayIcon):

    def __init__(self, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        self.parent = parent
        menu = QtGui.QMenu(parent)
        self.setIcon(QtGui.QIcon("icons/menuicon.png"))

        startAction = menu.addAction("Browse Kissync Folder")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.openSyncFolder)
        self.setContextMenu(menu)

        #startAction = menu.addAction("Settings")
        #self.connect(startAction, QtCore.SIGNAL("triggered()"), self.test)
        #self.setContextMenu(menu)

        menu.addSeparator()

        exitAction = menu.addAction("Exit")
        self.connect(exitAction, QtCore.SIGNAL("triggered()"), self.exit)
        self.setContextMenu(menu)

        self.loadingIcon1 = QtGui.QIcon("icons/menuicon1.png")
        self.loadingIcon2 = QtGui.QIcon("icons/menuicon2.png")
        self.loadingIcon3 = QtGui.QIcon("icons/menuicon3.png")
        self.loadingIcon4 = QtGui.QIcon("icons/menuicon4.png")

    #def loading(self):
        #self.setIcon(self.loadingIcon1)

    def openSyncFolder(self):
        if platform.system() == 'Darwin':
            subprocess.call(['open', '--', self.parent.syncDirectory])
        elif platform.system() == 'Linux':
            subprocess.call(['gnome-open', self.parent.syncDirectory])
        elif platform.system() == 'Windows':
            subprocess.call(['explorer', self.parent.syncDirectory])

    #def test(self):
        #print "clicked menu item"

    def exit(self):
        sys.exit(0)

    def notification(self, title, message):
        #enum MessageIcon { NoIcon, Information, Warning, Critical }
        if(self.parent.configuration.get('LocalSettings', 'notifications')):
            self.showMessage(title, message, QtGui.QSystemTrayIcon.NoIcon)


if __name__ == "__main__":
    me = SingleInstance()
    app = QtGui.QApplication(sys.argv)

    mainwindow = Main()

    sys.exit(app.exec_())
