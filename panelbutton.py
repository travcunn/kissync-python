import os
from PyQt4 import QtCore, QtGui


class PanelIcon(QtGui.QWidget):
    def __init__(self, parent=None, buttonType=None):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.buttonType = buttonType

        self.setStyleSheet("QWidget { border: 0px; }")

        self.setMinimumSize(48, 48)
        self.setMaximumSize(48, 48)

        self.gridlayout = QtGui.QGridLayout()
        self.setLayout(self.gridlayout)

        self.addIcon(self.buttonType)

    def addIcon(self, buttonType):
        self.icon = QtGui.QImage()
        self.icon.load(os.path.dirname(os.path.realpath(__file__)) + "/icons/simplicio/icons48/" + buttonType + ".png")
        self.icontarget = QtCore.QRectF(0, 0, 48, 48)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)

        painter.drawImage(self.icontarget, self.icon)

        painter.end()


class PanelButton(QtGui.QWidget):
    def __init__(self, parent=None, buttonType=None):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.buttonType = buttonType

        blue = "FFFFFF"
        self.qcolorblue = QtGui.QColor(int(blue[:2], 16), int(blue[2:4], 16), int(blue[4:], 16), 255)

        lime = "222222"
        self.qcolorlime = QtGui.QColor(int(lime[:2], 16), int(lime[2:4], 16), int(lime[4:], 16), 255)

        self.setStyleSheet("QWidget { border: 0px; }")

        self.setMinimumSize(90, 48)
        self.setMaximumSize(90, 64)
        self.setContentsMargins(0, 0, 0, 0)

        self.gridlayout = QtGui.QGridLayout()
        self.gridlayout.addWidget(PanelIcon(self, self.buttonType))
        self.setLayout(self.gridlayout)

        #self.opacity = .07
        self.opacity = .2
        self.hover = False
        self.setStatusTip('Exit application')

    def paintEvent(self, e):
        #Start Painter
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setOpacity(self.opacity)
        #Draw Background Color
        self.draw(painter)
        #End Painter
        painter.end()

    def draw(self, painter):
        penblank = QtGui.QPen(QtCore.Qt.black, -1, QtCore.Qt.SolidLine)

        painter.setPen(penblank)

        if(self.hover):
            painter.setBrush(self.qcolorlime)
        else:
            painter.setBrush(self.qcolorblue)
        painter.drawRect(0, 0, self.frameSize().width(), self.frameSize().height())

    def mousePressEvent(self, event):
        ##print "Clicked on " + self.buttonType.title()
        self.parent.buttonClicked(self.buttonType)

    def mouseDoubleClickEvent(self, event):
        pass

    def enterEvent(self, event):
        self.hover = True
        self.repaint()

    def leaveEvent(self, event):
        self.hover = False
        self.repaint()
