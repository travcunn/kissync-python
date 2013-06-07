from PyQt4 import QtGui, QtCore

import style


class LoadingSquare(QtGui.QWidget):
    def __init__(self, parent, color=None, delay=0):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.delay = delay

        self.squareWidth = 32
        self.squareHeight = 32

        self.color = color
        self.color = parent.style.hexToQColor(self.color)

        self.initUI()

    def initUI(self):
        self.setFixedSize(self.squareWidth, self.squareHeight)
        self.opacity = 0.0

        if not (self.delay == 1):
            self.timeline = QtCore.QTimeLine()
            self.timeline.valueChanged.connect(self.animate)
            self.timeline.setDuration(1)
            self.timeline.start()
        else:
            self.opacity = 1
            self.repaint()

    #this is called every time something needs to be repainted
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setOpacity(self.opacity)
        self.drawSquare(painter)
        painter.end()

    def drawSquare(self, painter):
        #get rid of the pen... gets rid of outline on drawing
        painter.setPen(QtCore.Qt.NoPen)
        #windows 8 colors are pretty http://www.creepyed.com/2012/09/windows-8-colors-hex-code/
        painter.setBrush(self.color)
        #from docs: drawRect (self, int x, int y, int w, int h)
        painter.drawRect(0, 0, self.squareWidth, self.squareHeight)

    def animate(self, value):
        self.opacity = value * 1
        self.repaint()
        if self.opacity == 1.0:
            self.timeline1 = QtCore.QTimeLine()
            self.timeline1.valueChanged.connect(self.animateback)
            self.timeline1.setDuration(1500)
            self.timeline1.start()

    def animateback(self, value):
        self.opacity = 1 - (value * 1)
        self.repaint()
        if self.opacity == 0.0:
            ##print self.showdelay
            self.timeline1 = QtCore.QTimeLine()
            self.timeline1.valueChanged.connect(self.animate)
            self.timeline1.setDuration(300)
            self.timeline1.start()


class LoadingWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        ##get rid of the widget border
        self.setStyleSheet("QWidget { border: 0px; }")
        self.style = style.KissyncStyle()
        self.setMaximumSize(140, 140)

        self.gridlayout = QtGui.QGridLayout()

        self.setLayout(self.gridlayout)
        QtCore.QTimer.singleShot(0, self.add9)
        QtCore.QTimer.singleShot(200, self.add1)
        QtCore.QTimer.singleShot(400, self.add2)
        QtCore.QTimer.singleShot(600, self.add3)
        QtCore.QTimer.singleShot(800, self.add4)
        QtCore.QTimer.singleShot(1000, self.add5)
        QtCore.QTimer.singleShot(1250, self.add6)
        QtCore.QTimer.singleShot(1500, self.add7)
        QtCore.QTimer.singleShot(1750, self.add8)
        QtCore.QTimer.singleShot(2000, self.add9)

    def add1(self):
        self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE), 0, 0)

    def add2(self):
        self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE), 0, 1)

    def add3(self):
        self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE), 0, 2)

    def add4(self):
        self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE), 1, 2)

    def add5(self):
        self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE), 2, 2)

    def add6(self):
        self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE), 2, 1)

    def add7(self):
        self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE), 2, 0)

    def add8(self):
        self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE), 1, 0)

    def add9(self):
        self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE, 1), 1, 1)

    def counter(self):
        for i in range(self.gridlayout.count()):
            self.gridlayout.removeItem(self.gridlayout.itemAt(i))


class Main(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.setWindowTitle('Keep It Simple Sync')

        self.setGeometry(400, 200, 300, 325)

        self.loadingwidget = LoadingWidget()

        grid = QtGui.QGridLayout()
        grid.addWidget(self.loadingwidget)

        self.setLayout(grid)
