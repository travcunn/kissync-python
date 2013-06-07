import math
import os
import shutil
import subprocess
import sys
from PyQt4 import QtGui, QtCore


class AvatarWidget(QtGui.QWidget):
    def __init__(self, parent=None, extension=None):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.extension = extension
        self.isFolder = self.parent.isFolder

        ##get rid of the widget border
        self.setStyleSheet("QWidget { border: 0px; }")

        self.setMinimumSize(64, 64)
        self.setMaximumSize(64, 64)

        self.gridlayout = QtGui.QGridLayout()

        self.setLayout(self.gridlayout)
        self.addIcon(self.extension)

    def addIcon(self, extension):
        self.icon = QtGui.QImage()
        if (self.isFolder):
            extension = "folder"
        elif (extension is None or extension == ""):
            extension = "unknown"
        else:
            extension = extension[1:]

        if (
        self.icon.load(os.path.dirname(os.path.realpath(__file__)) + "/icons/faience/mimetypes/" + extension + ".svg")):
            ##print "KNOWN"
            pass
        else:
            extension = "unknown"

        self.icon.load(os.path.dirname(os.path.realpath(__file__)) + "/icons/faience/mimetypes/" + extension + ".svg")

        self.icontarget = QtCore.QRectF(0, 0, 64, 64)

    #this is called every time something needs to be repainted
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawImage(self.icontarget, self.icon)
        painter.end()


class ItemObject(QtGui.QWidget):
    def __init__(self, parent=None, filePath=None, fileName=None, fileSize=None, fileType=None, isFolder=False,
                 modified=None, panelView=False):
        QtGui.QWidget.__init__(self)
        self.parent = parent

        blue = "1BA1E2"
        self.qcolorblue = QtGui.QColor(int(blue[:2], 16), int(blue[2:4], 16), int(blue[4:], 16), 255)

        lime = "8CBF26"
        self.qcolorlime = QtGui.QColor(int(lime[:2], 16), int(lime[2:4], 16), int(lime[4:], 16), 255)

        #Item Properties
        self.filePath = filePath
        self.fileName = fileName
        self.fileSize = fileSize
        self.fileType = fileType
        self.isActive = False
        self.isFolder = isFolder
        self.lastModified = modified
        self.panelView = panelView

        #get rid of the widget border
        self.setStyleSheet("QWidget { border: 0px;}")
        self.setMinimumSize(200, 90)
        self.setMaximumSize(200, 90)
        self.setGeometry(0, 0, self.frameSize().width() - 50, self.frameSize().height() - 50)

        self.gridlayout = QtGui.QGridLayout()

        self.rows = 3
        self.cols = 2

        #Get file extension and type
        if (self.fileName.rfind('.') != -1):
            dotIndex = self.fileName.rfind('.')
            ##print dotIndex
            fileNameLength = len(self.fileName)
            ##print fileNameLength
            extension = self.fileName[dotIndex:fileNameLength]
        else:
            extension = None

        ##print extension

        #Icon
        self.icon = AvatarWidget(self, extension)
        self.gridlayout.addWidget(self.icon, 1, 1, 3, 1, QtCore.Qt.AlignLeft)

        #Delete Button
        if not (self.panelView):
            self.deleteMeButton = QtGui.QPushButton('X')
            self.deleteMeButton.setStyleSheet('QPushButton {color: White}')
            self.deleteMeButton.clicked.connect(self.deleteMe)
            self.deleteMeButton.setStyleSheet("QPushButton {background-color: transparent;}")
            self.deleteMeButton.setMinimumSize(10, 10)

            self.gridlayout.addWidget(self.deleteMeButton, 1, 2, QtCore.Qt.AlignRight)

        #File Name Label
        font = QtGui.QFont("Roboto", 11, QtGui.QFont.Bold, False)
        #tempSlashIndex = self.filePath.rfind('/')
        #tempFileName = self.filePath[tempSlashIndex + 1:len(self.filePath)]
        self.lbFileName = QtGui.QLabel(self.fileName)
        self.lbFileName.setFont(font)
        self.lbFileName.setStyleSheet('QLabel {color: White}')
        self.lbFileName.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.gridlayout.addWidget(self.lbFileName, 2, 2, QtCore.Qt.AlignLeft)

        #File Size Label
        thissize = self.fileSize
        if (thissize < 1024):
            measurement = "bytes"
        elif (thissize < int(math.pow(1024, 2))):
            thissize /= 1024
            measurement = "kB"
        elif (thissize < int(math.pow(1024, 3))):
            thissize /= int(math.pow(1024, 2))
            measurement = "mB"
        else:
            thissize /= int(math.pow(1024, 3))
            measurement = "gb"

        self.lbFileSize = QtGui.QLabel(str(thissize) + " " + measurement)
        self.lbFileSize.setStyleSheet('QLabel {color: #222222}')
        self.lbFileSize.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        if not (self.isFolder):
            self.gridlayout.addWidget(self.lbFileSize, 3, 2, QtCore.Qt.AlignLeft)

        self.setLayout(self.gridlayout)

        if not (self.panelView):
            self.opacity = 0.0
            self.timeline = QtCore.QTimeLine()
            self.timeline.valueChanged.connect(self.animate)
            self.timeline.setDuration(500)
            self.timeline.start()
        else:
            self.opacity = 1.0

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        #Set Opacity
        painter.setOpacity(self.opacity)
        self.draw(painter)
        painter.end()

    def draw(self, painter):
        penblank = QtGui.QPen(QtCore.Qt.black, -1, QtCore.Qt.SolidLine)

        painter.setPen(penblank)

        if (self.isActive):
            painter.setBrush(self.qcolorlime)
        else:
            painter.setBrush(self.qcolorblue)
        painter.drawRect(0, 0, self.frameSize().width(), self.frameSize().height())

    def animate(self, value):
        self.opacity = value * 0.5
        self.repaint()

    def mousePressEvent(self, event):
        if not (self.panelView):
            if not (self.isActive):
                self.isActive = True
                self.opacity = 1.0
            else:
                self.parent.parent.bottompanel.deactivate()
                self.parent.parent.folderpanel.show()
                self.isActive = False
                self.opacity = 0.66

            if (len(self.parent.parent.fileview.getActive()) > 0):
                self.parent.parent.folderpanel.hide()
                self.parent.parent.bottompanel.activate()

            self.repaint()

    def mouseDoubleClickEvent(self, event):
        if not (self.panelView):
            #Go Deeper into directory, or download and open if file.
            ##print self.filePath
            self.isActive = False
            self.parent.parent.bottompanel.deactivate()
            self.parent.parent.folderpanel.show()
            if (self.isFolder):
                ##print "You double clicked a folder"
                #Item double clicked upon is a Folder.
                #Change the breadcrumb path.
                self.parent.parent.changePath(self.filePath)
                #Change Sidebar to show directory properties.
            else:
                #Item double clicked upon.
                ##print "You double clicked a file."
                self.parent.parent.parent.tray.notification("Kissync", "Downloading and Opening...")
                self.openFile(self.filePath)

    def enterEvent(self, event):
        if not (self.panelView):
            ##print("Enter")
            self.opacity = 1.0
            self.repaint()

    def leaveEvent(self, event):
        if not (self.panelView):
            ##print("Leave")
            if not (self.isActive):
                self.opacity = 0.66
            self.repaint()

    def deleteMe(self):
        #This will delete it's self.
        #print "Delete button clicked!"
        #Create the file path to delete.
        try:
            deleteMeFilePath = os.path.expanduser("~") + "/Kissync" + self.filePath
            ##print deleteMeFilePath
            ##Delete the file from the system.
            os.remove(deleteMeFilePath)
            ##Instead of deleting a specific square.. just re-update the fileview.
            deleteFileName = self.filePath.rfind('/')
            ##prints out the directory...
            ##print self.filePath[:deleteFileName + 1]
            self.parent.parent.changePath(self.filePath[:deleteFileName + 1])
        except:
            ##print "File does not exist on computer... Deleting from Cloud!"
            try:
                self.parent.parent.parent.smartfile.post('/path/oper/remove/', path=self.filePath)
            except:
                pass
            self.parent.parent.parent.tray.notification("Kissync", "In Deletion Queue...")

    def downloadFile(self, filepath):
        try:
            with open(self.parent.parent.parent.configuration.get('LocalSettings', 'sync-dir')):
                pass
        except:
            pathArray = filepath.split("/")
            pathArray.pop(0)
            pathArray.pop(len(pathArray) - 1)
            pathToAdd = ""
            #A BUG EXISTS IN THIS, PLEASE TEST THIS
            for directory in pathArray:
                if not os.path.exists(self.parent.parent.parent.configuration.get('LocalSettings',
                                                                                  'sync-dir') + "/" + pathToAdd + directory):
                    os.makedirs(self.parent.parent.parent.configuration.get('LocalSettings',
                                                                            'sync-dir') + "/" + pathToAdd + directory)
                    pathToAdd = pathToAdd + directory + "/"
                    ##print pathToAdd

            f = self.parent.parent.parent.smartfile.get('/path/data/', filepath)
            realPath = self.parent.parent.parent.configuration.get('LocalSettings', 'sync-dir') + filepath
            realPath = realPath.encode("utf-8")
            with file(realPath, 'wb') as o:
                shutil.copyfileobj(f, o)
            return realPath
        else:
            realPath = self.parent.parent.parent.configuration.get('LocalSettings', 'sync-dir') + filepath
            return realPath

    def openFile(self, filepath):
        openPath = self.downloadFile(filepath)
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', openPath))
        elif os.name == 'nt':
            os.startfile(openPath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', openPath))
