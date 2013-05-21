from PyQt4 import QtGui, QtCore
from authbrowser import AuthBrowser

import sys
import os


class LoginWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__()
        self.parent = parent
        self.setWindowTitle('Login to Kissync')
        #set the window type to a dialog
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog)

        exit = QtGui.QAction(self)
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        topText = QtGui.QLabel('Login to Kissync')
        #http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
        font = QtGui.QFont("Roboto", 24, QtGui.QFont.Light, False)
        topText.setFont(font)
        topText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        #topText.setStyleSheet("color: #FFFFFF

        detailsText = QtGui.QLabel('using your Smartfile acount')
        #http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
        fontsmall = QtGui.QFont("Roboto", 14, QtGui.QFont.Light, False)
        detailsText.setFont(fontsmall)
        detailsText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        #topText.setStyleSheet("color: #FFFFFF;")

        self.htmlView = AuthBrowser(self)

        #window size constraints
        self.setFixedSize(800, 550)

        fonterror = QtGui.QFont("Roboto", 18, QtGui.QFont.Normal, False)

        self.neterrorText = QtGui.QLabel('Error Connecting to SmartFile')
        self.neterrorText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.neterrorText.setStyleSheet("color: #FF0000;")
        self.neterrorText.setFont(fonterror)
        self.neterrorText.hide()

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
        self.neterrorText.show()
        self.errorText.hide()
        self.show()

    def invaliderror(self):
        self.errorText.show()
        self.neterrorText.hide()
        self.show()

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2), (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, event):
        #if the user closes the login window, close the entire app...
        sys.exit()


class CloudIconWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        ##get rid of the widget border
        self.setStyleSheet("QWidget { border: 0px; }")

        self.setMinimumSize(64, 64)
        self.setMaximumSize(64, 64)

        self.icon = QtGui.QImage()
        self.icon.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons", "icon.xpm"))

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
