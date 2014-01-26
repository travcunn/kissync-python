import os

from PySide import QtGui, QtCore

import app.core.common as common
import resources


class SettingsWindow(QtGui.QWidget):
    def __init__(self, parent, name, email):
        super(SettingsWindow, self).__init__()
        self.parent = parent
        self.name = name
        self.email = email

        self.setWindowTitle('SmartFile Settings')
        self.setWindowIcon(QtGui.QIcon(":/menuicon.png"))
        self.setFixedSize(562, 250)
        self.setContentsMargins(0, 0, 0, 0)

        maingrid = QtGui.QVBoxLayout()
        # Set the margin to 0 for the main layout
        maingrid.setContentsMargins(0, 0, 0, 0)
        # Remove the gray spacing between widgets
        maingrid.setSpacing(0)

        try:
            version = VersionContainer(self.parent.version)
        except:
            version = VersionContainer(None)
        self.settingsPanel = SettingsPanel(self)
        self.buttonsBar = ButtonsBar(self)

        maingrid.addWidget(version)
        maingrid.addWidget(self.settingsPanel)
        maingrid.addWidget(self.buttonsBar)

        self.setLayout(maingrid)
        self.centerOnScreen()

    def saveSettings(self):
        """ Saves the settings based on checkboxes. """
        startWithComputer = self.settingsPanel.rightPanel.startWithComputer
        if startWithComputer.isChecked():
            self.parent.configuration.set('autostart', True)
            # Create a startup entry
            common.create_shortcut()
        else:
            self.parent.configuration.set('autostart', False)
            common.delete_shortcut()

        self.hide()
        self.parent.configuration.save()

    def showSettings(self):
        """ Shows the settings window and brings it into focus. """
        autostart = self.settingsPanel.rightPanel.startWithComputer
        if self.parent.configuration.get('autostart'):
            if not autostart.isChecked():
                autostart.toggle()

        self.centerOnScreen()
        self.setWindowState(self.windowState() &
                ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive |
                QtCore.Qt.FramelessWindowHint)
        self.activateWindow()
        self.show()
        self.raise_()

    def hideSettings(self):
        """ Hide the settings window. """
        self.hide()

    def signOut(self):
        ###print "Logout button pressed"
        reply = QtGui.QMessageBox.question(self, 'Smartfile', 
            'Are you sure you want to logout?',
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            os.remove(common.settingsFile())
            os._exit(-1)

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, event):
        event.ignore()
        self.hide()


class SettingsPanel(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SettingsPanel, self).__init__()
        self.parent = parent
        self.setContentsMargins(0, 0, 0, 0)

        color = "FFFFFF"
        self.qcolorback = QtGui.QColor(int(color[:2], 16),
                int(color[2:4], 16), int(color[4:], 16), 255)

        grid = QtGui.QGridLayout()
        grid.setSpacing(0)

        leftPanel = LeftPanel(name=self.parent.name, email=self.parent.email)
        self.rightPanel = RightPanel(self)
        grid.addWidget(leftPanel, 1, 0, 1, 1)
        grid.addWidget(self.rightPanel, 1, 1, 1, 1)

        self.setLayout(grid)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.draw(painter)
        painter.end()

    def draw(self, painter):
        penblank = QtGui.QPen(QtCore.Qt.black, -1, QtCore.Qt.SolidLine)
        painter.setPen(penblank)
        painter.setBrush(self.qcolorback)
        painter.drawRect(0, 0, self.frameSize().width(),
                self.frameSize().height())


class VersionContainer(QtGui.QWidget):
    def __init__(self, version=None):
        super(VersionContainer, self).__init__()
        self.setFixedSize(562, 35)
        self.setContentsMargins(0, 0, 0, 0)

        color = "FFFFFF"
        self.qcolorback = QtGui.QColor(int(color[:2], 16),
                int(color[2:4], 16), int(color[4:], 16), 255)

        layout = QtGui.QGridLayout()

        if version is None:
            version = "0.1 beta"

        versionLabel = QtGui.QLabel()
        versionLabel.setText("version %s" % (version))
        versionLabel.setStyleSheet("color: #CCCCCC; font-size: 16px;")
        layout.addWidget(versionLabel, 0, 0, 1, 1, QtCore.Qt.AlignRight)

        self.setLayout(layout)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.draw(painter)
        painter.end()

    def draw(self, painter):
        penblack = QtGui.QPen(QtCore.Qt.black, -1, QtCore.Qt.SolidLine)
        painter.setPen(penblack)
        painter.setBrush(self.qcolorback)
        painter.drawRect(0, 0, self.frameSize().width(),
                self.frameSize().height())


class LeftPanel(QtGui.QWidget):
    def __init__(self, name='Test Full Name', email='test@smartfile.com'):
        super(LeftPanel, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)

        layout = QtGui.QGridLayout()

        logo = Logo()
        layout.addWidget(logo, 0, 0, 1, 1, QtCore.Qt.AlignVCenter)

        # Email address label
        nameLabel = QtGui.QLabel()
        nameLabel.setText("%s" % (name))
        nameLabel.setStyleSheet("color: #303030; font-size: 24px;")
        layout.addWidget(nameLabel, 1, 0, 1, 1, QtCore.Qt.AlignCenter)

        # Email address label
        emailLabel = QtGui.QLabel()
        emailLabel.setText("(%s)" % (email))
        emailLabel.setStyleSheet("color: #888888; font-size:18px;")
        layout.addWidget(emailLabel, 2, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.setLayout(layout)


class RightPanel(QtGui.QWidget):
    def __init__(self, parent=None):
        super(RightPanel, self).__init__()
        self.parent = parent
        self.setContentsMargins(0, 0, 0, 0)

        layout = QtGui.QGridLayout()

        #logo = Logo()
        #layout.addWidget(logo, 0, 0, 1, 1, QtCore.Qt.AlignVCenter)

        self.startWithComputer = QtGui.QCheckBox('Start with my computer', self)
        self.startWithComputer.setStyleSheet("font-size: 22px;")
        #self.startWithComputer.toggle()

        layout.addWidget(self.startWithComputer, 0, 0, 1, 1, QtCore.Qt.AlignTop)

        self.setLayout(layout)


class Logo(QtGui.QWidget):
    def __init__(self):
        super(Logo, self).__init__()

        self.setMinimumSize(214, 47)
        self.setMaximumSize(214, 47)

        self.image = QtGui.QImage()
        self.image.load(':/smartfile.xpm')

        self.imagetarget = QtCore.QRectF(0, 0, 214, 47)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawImage(self.imagetarget, self.image)
        painter.end()


class ButtonsBar(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ButtonsBar, self).__init__()
        self.parent = parent
        self.setMinimumSize(562, 50)
        self.setMaximumSize(562, 50)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum,
                QtGui.QSizePolicy.Maximum)

        grid = QtGui.QGridLayout()

        leftSpacer = QtGui.QWidget()
        leftSpacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                QtGui.QSizePolicy.Expanding)
        rightSpacer = QtGui.QWidget()
        rightSpacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                QtGui.QSizePolicy.Expanding)

        #grid.addWidget(leftSpacer, 0, 0, 1, 1)

        signoutButton = QtGui.QPushButton("Sign out", self)
        signoutButton.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                    QtGui.QSizePolicy.Fixed)
        signoutButton.clicked.connect(self.parent.signOut)
        grid.addWidget(signoutButton, 0, 1, 1, 1)

        grid.addWidget(rightSpacer, 0, 2, 1, 1)

        cancelButton = QtGui.QPushButton("Cancel", self)
        cancelButton.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                QtGui.QSizePolicy.Fixed)
        cancelButton.clicked.connect(self.parent.hideSettings)
        grid.addWidget(cancelButton, 0, 4, 1, 1)

        saveButton = QtGui.QPushButton("Save", self)
        saveButton.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                QtGui.QSizePolicy.Fixed)
        saveButton.clicked.connect(self.parent.saveSettings)
        grid.addWidget(saveButton, 0, 5, 1, 1)

        self.setLayout(grid)


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    settingsWindow = SettingsWindow(name='test name', email='a@smartfile.com')
    settingsWindow.showSettings()
    sys.exit(app.exec_())
