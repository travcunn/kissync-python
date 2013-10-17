from PySide import QtGui, QtCore

import resources


class SettingsWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__()
        self.parent = parent

        self.setWindowTitle('SmartFile Settings')
        self.setWindowIcon(QtGui.QIcon(":/menuicon.png"))
        self.setFixedSize(562, 250)
        self.setContentsMargins(0, 0, 0, 0)

        maingrid = QtGui.QVBoxLayout()
        maingrid.setContentsMargins(0, 0, 0, 0)

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
        self.hide()
        self.parent.configuration.save()

    def showSettings(self):
        self.centerOnScreen()
        self.setWindowState(self.windowState() &
                ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive |
                QtCore.Qt.FramelessWindowHint)
        self.activateWindow()
        self.show()
        self.raise_()

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

        leftPanel = LeftPanel()
        grid.addWidget(leftPanel, 1, 0, 1, 1)

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
        versionLabel.setStyleSheet("color: #CCCCCC")
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
    def __init__(self, parent=None):
        super(LeftPanel, self).__init__()
        self.parent = parent
        self.setContentsMargins(0, 0, 0, 0)

        layout = QtGui.QGridLayout()

        logo = Logo()
        layout.addWidget(logo, 0, 0, 1, 1, QtCore.Qt.AlignVCenter)

        #TODO: Add account information here (name, email)

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
        grid.addWidget(signoutButton, 0, 1, 1, 1)

        grid.addWidget(rightSpacer, 0, 2, 1, 1)

        cancelButton = QtGui.QPushButton("Cancel", self)
        cancelButton.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                QtGui.QSizePolicy.Fixed)
        grid.addWidget(cancelButton, 0, 4, 1, 1)

        saveButton = QtGui.QPushButton("Save", self)
        saveButton.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                QtGui.QSizePolicy.Fixed)
        grid.addWidget(saveButton, 0, 5, 1, 1)

        self.setLayout(grid)


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    settingsWindow = SettingsWindow()
    settingsWindow.showSettings()
    sys.exit(app.exec_())
