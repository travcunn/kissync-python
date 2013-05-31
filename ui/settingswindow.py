from PySide import QtGui, QtCore

from ui.accountwidget import AccountWidget
from ui.style import KissyncStyle


class SettingsWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__()
        self.parent = parent
        self.style = KissyncStyle()

        self.setWindowTitle('Kissync Folder Sync Settings')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowIcon(QtGui.QIcon("icons/menuicon.png"))
        self.setFixedSize(520, 180)
        self.setContentsMargins(0, 0, 0, 0)
        #blue color: 699afb

        self.settingsWidget = SettingsPanel(self)

        titleBar = TitleBar()
        maingrid = QtGui.QGridLayout()
        maingrid.setContentsMargins(0, 0, 0, 0)
        maingrid.addWidget(titleBar)
        maingrid.addWidget(self.settingsWidget)

        #set the layout to maingrid layout
        self.setLayout(maingrid)
        self.centerOnScreen()

    def saveSettings(self):
        if(self.settingsWidget.checkboxNotifications.isChecked()):
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

    def resizeEvent(self, event):
        pixmap = QtGui.QPixmap(self.size())
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setBrush(QtCore.Qt.black)
        painter.drawRoundedRect(pixmap.rect(), 8, 8)
        painter.end()
        self.setMask(pixmap.mask())

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
        self.setMinimumSize(200, 60)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("color: #FFFFFF;")
        self.setStyleSheet("QWidget { border: 0px; }")

        settingsLabel = QtGui.QLabel('settings')
        font = QtGui.QFont("Vegur", 28, QtGui.QFont.Light, False)
        settingsLabel.setFont(font)
        #color = self.style.BLUE
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

        painter.setBrush(QtGui.QColor('#699afb'))
        painter.drawRect(0, 0, self.frameSize().width(), self.frameSize().height())


class SettingsPanel(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SettingsPanel, self).__init__()
        self.parent = parent
        self.setMinimumSize(200, 80)
        self.setContentsMargins(0, 0, 0, 0)

        grid = QtGui.QGridLayout()
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.checkboxNotifications = QtGui.QCheckBox('Allow Desktop Notifications', self)
        self.checkboxNotifications.setObjectName("checkboxNotifications")
        self.checkboxNotifications.setStyleSheet("QCheckBox#checkboxNotifications { color: #FFFFFF; }")
        font = QtGui.QFont("Vegur", 16, QtGui.QFont.Light, False)
        self.checkboxNotifications.setFont(font)
        if self.parent.parent.configuration.get('LocalSettings', 'notifications'):
            if not self.checkboxNotifications.isChecked():
                self.checkboxNotifications.toggle()

        saveButton = QtGui.QPushButton('Save')
        saveButton.clicked.connect(self.parent.saveSettings)

        self.accountWidget = AccountWidget(self.parent)
        #add the objects to the grid

        grid.addWidget(self.accountWidget, 1, 2, 1, 2)
        grid.addWidget(self.checkboxNotifications, 2, 1, 2, 2)
        grid.addWidget(saveButton, 3, 3)

        self.setLayout(grid)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.draw(painter)
        painter.end()

    def draw(self, painter):
        penblank = QtGui.QPen(QtCore.Qt.black, -1, QtCore.Qt.SolidLine)

        painter.setPen(penblank)

        painter.setBrush(QtGui.QColor('#3c3c3c'))
        painter.drawRect(0, 0, self.frameSize().width(), self.frameSize().height())
