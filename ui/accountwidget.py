import hashlib
import os
import sys
import urllib
import webbrowser

from PySide import QtGui, QtCore


class LogoutLabel(QtGui.QLabel):
    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self)
        self.parent = parent
        self.setText("Logout")
        font = QtGui.QFont("Vegur", 16, QtGui.QFont.Normal, False)
        self.setFont(font)
        self.setStyleSheet("color: #1BA1E2;")

    def mousePressEvent(self, event):
        ###print "Logout button pressed"
        reply = QtGui.QMessageBox.question(self, 'Kissync', "Are you sure you want to exit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if (reply == QtGui.QMessageBox.Yes):
            self.parent.parent.tray.notification("Kissync", "Logging out..")
            try:
                os.remove(self.parent.parent.settingsFile)
                os._exit(-1)
            except:
                raise
        else:
            event.ignore()

    def mouseDoubleClickEvent(self, event):
        pass

    def enterEvent(self, event):
        self.setStyleSheet("color: #8CBF26;")
        self.repaint()

    def leaveEvent(self, event):
        self.setStyleSheet("color: #1BA1E2;")
        self.repaint()


class UsernameLabel(QtGui.QLabel):
    def __init__(self, parent=None, fullname=""):
        QtGui.QLabel.__init__(self)
        self.parent = parent
        self.setText(fullname)
        font = QtGui.QFont("Roboto", 12, QtGui.QFont.Light, False)
        self.setFont(font)
        self.setStyleSheet("color: #000000;")
        self.repaint()

    def mousePressEvent(self, event):
        webbrowser.open('https://app.smartfile.com/ftp/private/account/')

    def mouseDoubleClickEvent(self, event):
        pass


class AvatarWidget(QtGui.QWidget):
    def __init__(self, parent=None, email=None):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.email = email

        self.setStyleSheet("QWidget { border: 0px; }")

        self.setMinimumSize(64, 64)
        self.setMaximumSize(64, 64)

        self.gridlayout = QtGui.QGridLayout()

        self.addIcon(self.email)

    def addIcon(self, email):
        self.icon = QtGui.QImage()
        size = 64
        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?s=" + str(size)
        img_file = urllib.urlopen(gravatar_url).read()
        self.icon.loadFromData(img_file, "JPG")
        self.icontarget = QtCore.QRectF(0, 0, 64, 64)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        # Draw Item Thumbnail.
        painter.drawImage(self.icontarget, self.icon)
        painter.end()

    def mousePressEvent(self, event):
        webbrowser.open('http://www.gravatar.com/')

    def mouseDoubleClickEvent(self, event):
        pass


class AccountWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        self.parent = parent

        self.setMinimumSize(300, 80)
        self.setMaximumSize(300, 80)

        ##get rid of the widget border
        self.setStyleSheet("QWidget { border: 0px; }")

        #Call API to get full name and email address.
        try:
            tree = self.parent.parent.smartfile.get('/whoami', '/')
            if 'user' not in tree:
                return []

            self.fullname = tree['user']['name'].encode("utf-8")
            self.email = tree['user']['email'].encode("utf-8")
        except:
            self.fullname = "Test FullName"
            self.email = "web@google.com"

        self.lbFullName = UsernameLabel(self, self.fullname)
        self.lblogout = LogoutLabel(self)

        self.icon = AvatarWidget(self, self.email)

        self.gridlayout = QtGui.QGridLayout()

        self.gridlayout.addWidget(self.icon, 0, 1, 2, 2, QtCore.Qt.AlignRight)
        self.gridlayout.addWidget(self.lbFullName, 0, 0, 1, 2, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.gridlayout.addWidget(self.lblogout, 1, 0, 1, 2, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.setLayout(self.gridlayout)


class Main(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.setWindowTitle('Account Widget Test')
        self.setGeometry(400, 200, 300, 325)
        #Add Account Widget with dummy info.
        self.accountInfo = AccountWidget(self)
        self.grid = QtGui.QGridLayout()
        self.grid.addWidget(self.accountInfo)
        self.setLayout(self.grid)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mainwindow = Main()
    mainwindow.show()
    sys.exit(app.exec_())
