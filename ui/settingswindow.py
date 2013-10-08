from PySide import QtGui, QtCore
from ui.accountwidget import AccountWidget

import ui.resources


class SettingsWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__()
        self.parent = parent
        self.tray = self.parent.tray
        self.settingsFile = self.parent.settingsFile

        self.setWindowTitle('SmartFile Settings')
        self.setWindowIcon(QtGui.QIcon(":/menuicon.png"))
        self.setFixedSize(480, 350)
        self.setContentsMargins(0, 0, 0, 0)

        self.settingsWidget = SettingsPanel(self)

        titleBar = TitleBar()
        maingrid = QtGui.QGridLayout()
        maingrid.setContentsMargins(0, 0, 0, 0)
        maingrid.addWidget(titleBar, 0, 0)
        maingrid.addWidget(self.settingsWidget, 1, 0, 2, 2)

        self.setLayout(maingrid)
        self.centerOnScreen()

    def saveSettings(self):
        if self.settingsWidget.checkboxNotifications.isChecked():
            self.parent.configuration.set('LocalSettings', 'notifications', True)
        else:
            self.parent.configuration.set('LocalSettings', 'notifications', False)

        self.hide()
        self.parent.configuration.save()

    def showSettings(self):
        self.centerOnScreen()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive | QtCore.Qt.FramelessWindowHint)
        self.activateWindow()
        self.show()
        self.raise_()

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2), (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, event):
        event.ignore()
        self.hide()


class TitleBar(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TitleBar, self).__init__()
        self.parent = parent
        self.setMinimumSize(480, 60)
        self.setMaximumSize(480, 60)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("color: #FFFFFF;")
        self.setStyleSheet("QWidget { border: 0px; }")

        settingsLabel = QtGui.QLabel('SmartFile Sync Settings')
        font = QtGui.QFont("Vegur", 28, QtGui.QFont.Light, False)
        settingsLabel.setFont(font)
        settingsLabel.setObjectName("settingsLabel")
        settingsLabel.setStyleSheet("color: #FFFFFF;")

        titleBarGrid = QtGui.QGridLayout()
        titleBarGrid.addWidget(settingsLabel)
        self.setAutoFillBackground(True)
        self.setLayout(titleBarGrid)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.draw(painter)
        painter.end()

    def draw(self, painter):
        penblank = QtGui.QPen(QtCore.Qt.black, -1, QtCore.Qt.SolidLine)
        painter.setPen(penblank)
        painter.setBrush(QtGui.QColor('#1763A6'))
        painter.drawRect(0, 0, self.frameSize().width(), self.frameSize().height())


class SettingsPanel(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SettingsPanel, self).__init__()
        self.parent = parent

        self.setContentsMargins(0, 0, 0, 0)

        grid = QtGui.QGridLayout()
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        tabWidget = QtGui.QTabWidget()
        generalTab = QtGui.QWidget()
        accountTab = QtGui.QWidget()
        networkTab = QtGui.QWidget()

        generalTabLayout = QtGui.QGridLayout(generalTab)
        accountTabLayout = QtGui.QGridLayout(accountTab)
        networkTabLayout = QtGui.QGridLayout(networkTab)

        generalTabLayout.setAlignment(QtCore.Qt.AlignTop)
        generalTab.setContentsMargins(10, 10, 0, 10)

        tabWidget.addTab(generalTab, "General")
        tabWidget.addTab(accountTab, "Account")
        tabWidget.addTab(networkTab, "Network")

        self.checkboxNotifications = QtGui.QCheckBox('Allow Desktop Notifications', self)
        if self.parent.parent.configuration.get('LocalSettings', 'notifications'):
            if not self.checkboxNotifications.isChecked():
                self.checkboxNotifications.toggle()

        generalTabLayout.addWidget(self.checkboxNotifications, 1, 1, 1, 1)

        saveButton = QtGui.QPushButton("Save", self)
        saveButton.clicked.connect(self.parent.saveSettings)

        self.accountWidget = AccountWidget(self.parent)

        grid.addWidget(tabWidget, 1, 1, 1, 3)
        """
        grid.addWidget(self.checkboxNotifications, 1, 1, 2, 2)
        grid.addWidget(self.accountWidget, 1, 2, 1, 2)
        """
        grid.addWidget(saveButton, 3, 3, 1, 1)

        self.setLayout(grid)
