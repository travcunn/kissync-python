import os

from PySide import QtGui, QtCore


class SetupWizard(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SetupWizard, self).__init__()
        self.parent = parent
        self.setWindowTitle('Setup Smartfile')
        #set the window type to a dialog
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog)
        self.setFixedSize(465, 175)

        palette = QtGui.QPalette()

        exit = QtGui.QAction(self)
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        topText = QtGui.QLabel('Setting Up Smartfile')
        font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
        topText.setFont(font)
        topText.setPalette(palette)
        topText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        grid = QtGui.QGridLayout()

        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        formwidget = QtGui.QWidget()
        formgrid = QtGui.QFormLayout()
        formwidget.setLayout(formgrid)

        self.checkboxNotifications = QtGui.QCheckBox('Allow Desktop Notifications', self)
        font = QtGui.QFont("Roboto", 16, QtGui.QFont.Light, False)

        self.checkboxNotifications.setFont(font)
        self.checkboxNotifications.toggle()

        openFolderButton = QtGui.QPushButton("Open SmartFile Folder")
        openFolderButton.clicked.connect(self.parent.openSyncFolder)

        finishButton = QtGui.QPushButton('Finish Setup')
        finishButton.clicked.connect(self.saveSettings)

        formgrid.addRow(self.checkboxNotifications)
        formgrid.addRow(spacer)

        #add the objects to the grid
        grid.addWidget(spacer, 0, 0)
        grid.addWidget(spacer, 0, 3)
        grid.addWidget(topText, 0, 1, 1, 2)
        grid.addWidget(formwidget, 2, 1, 1, 2)
        grid.addWidget(openFolderButton, 3, 1, 1, 1)
        grid.addWidget(finishButton, 3, 2, 1, 1)
        #grid.addWidget(spacer, 5, 1)

        #set the layout to grid layout
        self.setLayout(grid)
        self.centerOnScreen()

    def saveSettings(self):
        """Saves the settings based upon values in the setup"""
        self.parent.configuration.set('LocalSettings', 'sync-offline', True)

        if self.checkboxNotifications.isChecked():
            self.parent.configuration.set('LocalSettings', 'notifications', True)
        else:
            self.parent.configuration.set('LocalSettings', 'notifications', False)

        directory = os.path.join(os.path.expanduser("~"), "Smartfile")
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.parent.configuration.set('LocalSettings', 'sync-dir', directory)

        self.parent.configuration.set('LocalSettings', 'first-run', False)
        self.hide()
        self.parent.configuration.save()
        self.parent.start()

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2), (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Setup Wizard', "Are you sure you want to exit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
