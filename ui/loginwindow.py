from PySide import QtGui, QtCore
from authbrowser import AuthBrowser

import sys

import ui.resources


class LoginWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__()
        self.parent = parent
        self.setWindowTitle('Login to SmartFile')
        #set the window type to a dialog
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog)
        self.setWindowIcon(QtGui.QIcon(":/menuicon.png"))
        #window size constraints
        self.setFixedSize(800, 550)

        self.setStyleSheet("QWidget { font-size: 14pt; }")

        exit = QtGui.QAction(self)
        self.connect(exit, QtCore.SIGNAL('triggered()'), 
                     QtCore.SLOT('close()'))

        topText = QtGui.QLabel('Login to SmartFile')
        topText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        detailsText = QtGui.QLabel('to get started')
        detailsText.setAlignment(QtCore.Qt.AlignHCenter |
                                 QtCore.Qt.AlignVCenter)

        self.htmlView = AuthBrowser(self)

        cloud = CloudIconWidget()
        grid = QtGui.QGridLayout()
        gridleft = QtGui.QGridLayout()
        gridleft.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        leftPanel = QtGui.QWidget()
        leftPanel.setLayout(gridleft)

        #add the objects to the grid
        gridleft.addWidget(topText, 0, 0)
        gridleft.addWidget(detailsText, 1, 0)
        gridleft.addWidget(cloud, 2, 0, 1, 1, QtCore.Qt.AlignHCenter)
        grid.addWidget(leftPanel, 0, 0, 1, 1)
        grid.addWidget(self.htmlView, 0, 1)

        #set the layout to grid layout
        self.setLayout(grid)
        self.centerOnScreen()

    def networkError(self):
        QtGui.QMessageBox.question(self, 'SmartFile',
                                   'Error connecting to SmartFile')
        self.show()

    def invaliderror(self):
        self.errorText.show()
        self.neterrorText.hide()
        self.show()

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, event):
        #if the user closes the login window, close the entire app.
        sys.exit()


class CloudIconWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setStyleSheet("QWidget { border: 0px; }")

        self.setMinimumSize(64, 64)
        self.setMaximumSize(64, 64)

        self.icon = QtGui.QImage()
        self.icon.load(':/icon.xpm')

        self.icontarget = QtCore.QRectF(0, 0, 64, 64)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawImage(self.icontarget, self.icon)
        painter.end()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    loginwindow = LoginWindow()
    loginwindow.show()
    sys.exit(app.exec_())
