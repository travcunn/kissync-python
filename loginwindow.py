from PyQt4 import QtCore, QtGui

import sys


class LoginWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__()
        self.parent = parent
        self.setWindowTitle('Login to Kissync')
        #set the window type to a dialog
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog)

        #fontfile = QtCore.QFile("resources/Roboto-Light-webfont.ttf")
        #fontDatabase.addApplicationFont(os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf")
        palette = QtGui.QPalette()
        #palette.setColor(QtGui.QPalette.Foreground,QtGui.QColor("#FFFFFF"))

        exit = QtGui.QAction(self)
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        topText = QtGui.QLabel('Login to Kissync')
        #http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
        font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
        topText.setFont(font)
        topText.setPalette(palette)
        topText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        #topText.setStyleSheet("color: #FFFFFF

        detailsText = QtGui.QLabel('using your Smartfile acount')
        #http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
        fontsmall = QtGui.QFont("Roboto", 14, QtGui.QFont.Normal, False)
        detailsText.setFont(fontsmall)
        detailsText.setPalette(palette)
        detailsText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        #topText.setStyleSheet("color: #FFFFFF;")

        grid = QtGui.QGridLayout()

        #window size constraints
        self.setFixedSize(465, 325)

        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        #file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        formwidget = QtGui.QWidget()
        formgrid = QtGui.QFormLayout()
        formwidget.setLayout(formgrid)

        fontform = QtGui.QFont("Roboto", 12, QtGui.QFont.Normal, False)
        fonterror = QtGui.QFont("Roboto", 18, QtGui.QFont.Normal, False)

        self.errorText = QtGui.QLabel('Invalid Username or Password')
        self.errorText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.errorText.setStyleSheet("color: #FF0000;")
        self.errorText.setFont(fonterror)
        self.errorText.hide()

        self.neterrorText = QtGui.QLabel('Error Connecting to SmartFile')
        self.neterrorText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.neterrorText.setStyleSheet("color: #FF0000;")
        self.neterrorText.setFont(fonterror)
        self.neterrorText.hide()

        usernameText = QtGui.QLabel('Username:')
        usernameText.setFont(fontform)
        self.usernameField = QtGui.QLineEdit()
        passwordText = QtGui.QLabel('Password:')
        passwordText.setFont(fontform)
        self.passwordField = QtGui.QLineEdit()
        self.passwordField.setEchoMode(QtGui.QLineEdit.Password)
        loginButton = QtGui.QPushButton('Login')
        loginButton.clicked.connect(self.tryLogin)

        formgrid.addRow(usernameText, self.usernameField)
        formgrid.addRow(passwordText, self.passwordField)
        formgrid.addRow(loginButton)

        #add the objects to the grid
        grid.addWidget(spacer, 0, 0)
        grid.addWidget(spacer, 0, 2)
        grid.addWidget(topText, 0, 1)
        grid.addWidget(detailsText, 1, 1)
        grid.addWidget(self.errorText, 2, 1)
        grid.addWidget(self.neterrorText, 3, 1)
        grid.addWidget(formwidget, 4, 1)
        #grid.addWidget(loading, 1, 1)
        grid.addWidget(spacer, 10, 1)
        #set the layout to grid layout
        self.setLayout(grid)
        self.centerOnScreen()

    def tryLogin(self):
        self.hide()
        self.parent.config.set('Login', 'username', str(self.usernameField.text()))
        self.parent.config.set('Login', 'password', str(self.passwordField.text()))
        with open(self.parent.settingsFile, 'wb') as configfile:
            self.parent.config.write(configfile)

        self.parent.authenticator.go()

    def networkerror(self):
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
