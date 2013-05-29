from PyQt4 import QtGui, QtCore

from ui.accountwidget import AccountWidget
from ui.style import KissyncStyle


class SettingsWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__()
        self.parent = parent
        self.style = KissyncStyle()

        self.setWindowTitle('Kissync Folder Sync Settings')
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog)
        self.setFixedSize(520, 180)

        settingsLabel = QtGui.QLabel('settings')
        font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
        settingsLabel.setFont(font)
        settingsLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        color = self.style.BLUE
        #settingsLabel.setStyleSheet("color: %s;" % color)

        grid = QtGui.QGridLayout()
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.checkboxNotifications = QtGui.QCheckBox('Allow Desktop Notifications', self)
        font = QtGui.QFont("Roboto", 16, QtGui.QFont.Light, False)
        self.checkboxNotifications.setFont(font)
        if self.parent.configuration.get('LocalSettings', 'notifications'):
            if not self.checkboxNotifications.isChecked():
                self.checkboxNotifications.toggle()

        saveButton = QtGui.QPushButton('Save')
        saveButton.clicked.connect(self.saveSettings)

        self.accountWidget = AccountWidget(self.parent)
        #add the objects to the grid
        grid.addWidget(spacer, 0, 0)
        grid.addWidget(spacer, 0, 5)
        grid.addWidget(settingsLabel, 0, 1)
        grid.addWidget(self.accountWidget, 0, 2, 1, 2)
        grid.addWidget(self.checkboxNotifications, 1, 1, 2, 2)
        grid.addWidget(saveButton, 2, 3)
        grid.addWidget(spacer, 5, 1)
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

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2), (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, event):
        event.ignore()
        self.hide()
