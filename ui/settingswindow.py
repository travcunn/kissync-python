import os
from PyQt4 import QtGui, QtCore

from ui.accountwidget import AccountWidget
from ui.style import KissyncStyle


class SettingsWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__()
        self.style = KissyncStyle()

        self.setWindowTitle('Kissync Settings')
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog)
        self.setFixedSize(465, 325)

        generalTab = QtGui.QLabel('settings')
        font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
        generalTab.setFont(font)
        generalTab.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        color = self.style.BLUE
        generalTab.setStyleSheet("color: %s;" % color)
        
        accountTab = AccountTab(self, False)

        grid = QtGui.QGridLayout()
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.settingsWidget = QtGui.QWidget()
        formgrid = QtGui.QFormLayout()
        self.settingsWidget.setLayout(formgrid)

        accountWidget = QtGui.QWidget()
        accountGrid = QtGui.QGridLayout()
        accountWidget.setLayout(accountGrid)

        self.cbWrite = QtGui.QCheckBox('Write', self)
        self.cbDelete = QtGui.QCheckBox('Delete', self)
        self.cbRead = QtGui.QCheckBox('Read', self)
        self.cbView = QtGui.QCheckBox('View', self)
        font = QtGui.QFont("Roboto", 16, QtGui.QFont.Normal, False)

        finishButton = QtGui.QPushButton('Save')

        formgrid.addRow(self.cbWrite)
        formgrid.addRow(spacer)
        formgrid.addRow(self.cbDelete)
        formgrid.addRow(spacer)
        formgrid.addRow(self.cbRead)
        formgrid.addRow(spacer)
        formgrid.addRow(self.cbView)
        formgrid.addRow(spacer)
        formgrid.addRow(finishButton)

        self.accountWidget = AccountWidget(self)
        accountGrid.addWidget(spacer, 0, 0)
        accountGrid.addWidget(spacer, 0, 5)
        accountGrid.addWidget(self.accountWidget)
        #add the objects to the grid
        grid.addWidget(spacer, 0, 0)
        grid.addWidget(spacer, 0, 5)
        grid.addWidget(generalTab, 0, 1)
        grid.addWidget(accountTab, 0, 2)
        grid.addWidget(self.settingsWidget, 2, 1)
        grid.addWidget(accountWidget, 2, 1, 2, 2)
        grid.addWidget(spacer, 5, 1)
        #set the layout to grid layout
        self.setLayout(grid)
        self.centerOnScreen()
        self.accountWidget.hide()

    def saveSettings(self):
        self.parent.configuration.set('LocalSettings', 'sync-offline', True)

        if(self.checkboxNotifications.isChecked()):
            self.parent.configuration.set('LocalSettings', 'notifications', True)
        else:
            self.parent.configuration.set('LocalSettings', 'notifications', False)

        directory = os.path.join(os.path.expanduser("~"), "Kissync")
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.parent.configuration.set('LocalSettings', 'sync-dir', directory)

        self.parent.configuration.set('LocalSettings', 'first-run', False)
        self.hide()
        self.parent.configuration.save()

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2), (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, event):
        event.ignore()
        self.hide()


class AccountTab(QtGui.QLabel):
    def __init__(self, parent, isActive):
        QtGui.QLabel.__init__(self)
        self.parent = parent
        self.setText("account")
        font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
        self.setFont(font)
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.setStyleSheet("color: #1BA1E2;")
        self.isActive = isActive
        if self.isActive:
            self.activate()

    def activate(self):
        self.isActive = True
        self.parent.settingsWidget.hide()
        self.parent.accountWidget.show()
        self.setStyleSheet("color: #8CBF26; font-weight: normal;")
        self.repaint()

    def deactivate(self):
        self.isActive = False
        self.parent.accountWidget.hide()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def mousePressEvent(self, event):
        self.activate()

    def mouseDoubleClickEvent(self, event):
        pass

    def enterEvent(self, event):
        if not self.isActive:
            self.setStyleSheet("color: #8CBF26;")
            self.repaint()

    def leaveEvent(self, event):
        if not self.isActive:
            self.setStyleSheet("color: #1BA1E2;")
            self.repaint()
