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
        self.setObjectName("settingswindow")
        self.setStyleSheet("QWidget#settingswindow { background: #3c3c3c; }")
        #blue color: 699afb

        settingsLabel = QtGui.QLabel('settings')
        font = QtGui.QFont("Vegur", 32, QtGui.QFont.Light, False)
        settingsLabel.setFont(font)
        settingsLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        #color = self.style.BLUE
        #settingsLabel.setStyleSheet("color: %s;" % color)

        titleBar = QtGui.QWidget()
        titleBar.setObjectName("titlebar")
        titleBar.setStyleSheet("QWidget#titlebar { background: #699afb; }")
        titleBar.setMinimumSize(200, 60)

        grid = QtGui.QGridLayout()
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.checkboxNotifications = QtGui.QCheckBox('Allow Desktop Notifications', self)
        font = QtGui.QFont("Vegur", 16, QtGui.QFont.Light, False)
        self.checkboxNotifications.setFont(font)
        if self.parent.configuration.get('LocalSettings', 'notifications'):
            if not self.checkboxNotifications.isChecked():
                self.checkboxNotifications.toggle()

        saveButton = QtGui.QPushButton('Save')
        saveButton.clicked.connect(self.saveSettings)

        self.accountWidget = AccountWidget(self.parent)
        #add the objects to the grid
        grid.addWidget(titleBar, 0, 0, 1, 5)

        grid.addWidget(settingsLabel, 1, 1)
        grid.addWidget(self.accountWidget, 1, 2, 1, 2)
        grid.addWidget(self.checkboxNotifications, 2, 1, 2, 2)
        grid.addWidget(saveButton, 3, 3)

        #set the layout to grid layout
        self.setLayout(grid)
        self.centerOnScreen()

    def saveSettings(self):
        if(self.checkboxNotifications.isChecked()):
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
