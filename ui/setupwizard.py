import os

from PySide import QtGui, QtCore

import resources


class SetupWizard(QtGui.QWidget):
    def __init__(self, parent):
        super(SetupWizard, self).__init__()
        self.parent = parent

        self.setWindowTitle('SmartFile')
        self.setWindowIcon(QtGui.QIcon(":/menuicon.png"))
        self.setFixedSize(559, 290)
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        maingrid = QtGui.QVBoxLayout()
        # Set the margin to 0 for the main layout
        maingrid.setContentsMargins(0, 0, 0, 0)
        # Remove the gray spacing between widgets
        maingrid.setSpacing(0)

        self.buttonsBar = ButtonsBar(self)

        self.topimage = QtGui.QImage()
        self.topimage.load(":/setupback.png")
        self.icontarget = QtCore.QRectF(0, 0, 559, 290)

        maingrid.addItem(QtGui.QSpacerItem(0, 190))
        maingrid.addWidget(self.buttonsBar)

        self.setLayout(maingrid)
        self.centerOnScreen()

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawImage(self.icontarget, self.topimage)
        painter.end()

    def saveSettings(self):
        """Saves the settings based upon values in the setup"""
        directory = os.path.join(os.path.expanduser("~"), "Smartfile")
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.parent.configuration.set('sync-dir', directory)

        self.parent.configuration.set('first-run', False)
        self.hide()
        self.parent.start()

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'SmartFile',
                                           "Are you sure you want to exit?",
                                           QtGui.QMessageBox.Yes, 
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class OpenFolderButton(QtGui.QWidget):
    def __init__(self, onclick):
        self.onclick = onclick

        self.icon = QtGui.QImage()
        self.icon.load(":/openfolderbutton.png")
        self.icontarget = QtCore.QRectF(0, 0, 228, 41)
        super(OpenFolderButton, self).__init__()
        self.setMinimumSize(228, 44)
        self.setMaximumSize(228, 44)
        self.setContentsMargins(0, 0, 0, 0)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawImage(self.icontarget, self.icon)
        painter.end()

    def mousePressEvent(self, event):
        self.onclick()

    def enterEvent(self, event):
        self.icon.load(":/openfolderbuttondown.png")
        self.repaint()

    def leaveEvent(self, event):
        self.icon.load(":/openfolderbutton.png")
        self.repaint()


class FinishButton(QtGui.QWidget):
    def __init__(self, onclick):
        self.onclick = onclick

        self.icon = QtGui.QImage()
        self.icon.load(":/finishsetupbutton.png")
        self.icontarget = QtCore.QRectF(0, 0, 228, 41)
        super(FinishButton, self).__init__()
        self.setMinimumSize(228, 44)
        self.setMaximumSize(228, 44)
        self.setContentsMargins(0, 0, 0, 0)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawImage(self.icontarget, self.icon)
        painter.end()

    def mousePressEvent(self, event):
        self.onclick()

    def enterEvent(self, event):
        self.icon.load(":/finishsetupbuttondown.png")
        self.repaint()

    def leaveEvent(self, event):
        self.icon.load(":/finishsetupbutton.png")
        self.repaint()


class ButtonsBar(QtGui.QWidget):
    def __init__(self, parent):
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
        middleSpacer = QtGui.QWidget()
        middleSpacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                QtGui.QSizePolicy.Expanding)

        rightSpacer = QtGui.QWidget()
        rightSpacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                QtGui.QSizePolicy.Expanding)

        self.openbutton = OpenFolderButton(onclick=self.parent.parent.openSyncFolder)
        self.finishbutton = FinishButton(onclick=self.parent.saveSettings)

        grid.addWidget(leftSpacer, 1, 0, 1, 1)
        grid.addWidget(self.openbutton, 1, 1, 1, 1)

        grid.addWidget(middleSpacer, 1, 2, 1, 1)

        grid.addWidget(self.finishbutton, 1, 4, 1, 1)
        grid.addWidget(rightSpacer, 1, 5, 1, 1)

        self.setLayout(grid)
