import os, platform, sys, time, urllib2
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg

import style

class LoadingSquare(QtGui.QWidget):
    
	def __init__(self, parent, color = None, showdelay = 1000):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		self.showdelay = showdelay
		
		self.squareWidth = 32
		self.squareHeight = 32
		
		self.color = color
		self.color = parent.style.hexToQColor(self.color)
		
		self.initUI()
		
        
	def initUI(self):      
		print "Creating a square..."
		self.setFixedSize(self.squareWidth, self.squareHeight)
		self.opacity = 0.0
		
		self.show()
		
		if not (self.showdelay == 0):
			self.timeline = QtCore.QTimeLine()
			self.timeline.valueChanged.connect(self.animate)
			self.timeline.setDuration(self.showdelay)
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
		if(self.opacity == 1.0):
			self.timeline1 = QtCore.QTimeLine()
			self.timeline1.valueChanged.connect(self.animateback)
			self.timeline1.setDuration(1000)
			self.timeline1.start()
		
	def animateback(self, value):
		self.opacity = 1 - (value * 1)
		self.repaint()
		if(self.opacity == 0.0):
			print self.showdelay
			self.timeline1 = QtCore.QTimeLine()
			self.timeline1.valueChanged.connect(self.animate)
			self.timeline1.setDuration(200)
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
		self.addWidgets()

	def addWidgets(self):
		self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE, 150), 0, 0)
		self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE, 300), 0, 1)
		self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE, 450), 0, 2)
		
		self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE, 600), 1, 2)
		self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE, 750), 2, 2)
		self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE, 900), 2, 1)
		
		self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE, 1050), 2, 0)
		self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE, 1200), 1, 0)
		self.gridlayout.addWidget(LoadingSquare(self, self.style.BLUE, 0), 1, 1)


class Main(QtGui.QWidget):
	def __init__(self, parent = None):
		super(Main, self).__init__(parent)
		self.setWindowTitle('Keep It Simple Sync')  
		
		#self.setStyleSheet("#MainWindow {background-color: #222222; }") 
		self.setGeometry(400, 200, 300, 325)

		loadingwidget = LoadingWidget()	
		
		grid = QtGui.QGridLayout()
		grid.addWidget(loadingwidget)

		self.setLayout(grid)

if __name__ == "__main__":
	
	#print os.path.realpath(__file__)
	app = QtGui.QApplication(sys.argv)
	mainwindow = Main()
	mainwindow.show()
	sys.exit(app.exec_())
