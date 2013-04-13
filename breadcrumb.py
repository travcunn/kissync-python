import math, os, platform, sys, time, urllib2
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg

import style

class Crumb(QtGui.QWidget):
    
	def __init__(self, parent, color = None, name = None, arrow = 1, indexnumber = 0):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		self.name = name
		self.arrow = arrow
		self.squareWidth = 100
		self.squareHeight = 38
		self.indexnumber = indexnumber
		
		self.setMaxSize()
	
		self.color = color
		self.color = parent.style.hexToQColor(self.color)
		
		fontDatabase = QtGui.QFontDatabase()
		#fontfile = QtCore.QFile("resources/Roboto-Light-webfont.ttf")
		fontDatabase.addApplicationFont(os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf")
		os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf"
		
		self.text = name
		self.font = QtGui.QFont("Roboto", 12, QtGui.QFont.Bold, False)
		
		self.isfirst = False
		self.isactive = False	
		
		if(self.arrow == 0):
			self.isfirst = True
		
		self.textCondense()
		
		self.initUI()
	
	def setMaxSize(self):
		self.setMaximumSize(self.squareWidth, self.squareHeight)
		self.setMinimumSize(self.squareWidth, self.squareHeight)
		
	def textCondense(self):    
		self.displayText = self.text
		if(len(self.name) > 10):
			if(self.isactive == False):
				if(len(self.name) <= 18):
					ratio = len(self.name) - 10
					self.squareWidth = 100 + ratio * 10
					self.setMaxSize()
				else:
					cut = len(self.name) - 18
					self.displayText = self.name.replace(self.name[-cut:], '.....')
						
					self.squareWidth = 100 + 5 * 14
					self.setMaxSize()
			else:
				ratio = len(self.name) - 10
				self.squareWidth = 100 + ratio * 14
				self.setMaxSize()
				
		self.displayText = "    " + self.displayText
		
	def initUI(self):      
		self.repaint()
	
	def paintEvent(self, e):
		painter = QtGui.QPainter()
		painter.begin(self)
		self.drawCrumbBack(painter)
		if(self.isfirst == False):
			self.drawArrow(painter)
		self.drawText(e, painter)
		painter.end()
        
	def drawCrumbBack(self, painter):
		penbold = QtGui.QPen(QtCore.Qt.black, 5, QtCore.Qt.SolidLine)
		penblank = QtGui.QPen(QtCore.Qt.black, -1, QtCore.Qt.SolidLine)

		painter.setPen(penblank)
		if(self.isactive == False):
			painter.setBrush(self.color)
		else:
			painter.setBrush(self.parent.style.hexToQColor(self.parent.style.LIME))
		painter.drawRect(0, 0, self.squareWidth, self.squareHeight)
		
	def drawArrow(self, painter):
		penbold = QtGui.QPen(QtCore.Qt.white, 3, QtCore.Qt.SolidLine)
		penblank = QtGui.QPen(QtCore.Qt.black, -1, QtCore.Qt.SolidLine)
		
		side = math.sqrt(math.pow(self.squareHeight, 2)/2)
		painter.setPen(penbold)
		painter.setBrush(self.color)
		painter.rotate(45)
		painter.drawRect(0, 0, side, side)
		painter.rotate(-45)
		
	def drawText(self, event, painter):
		painter.setPen(QtGui.QColor(255, 255, 255))
		painter.setFont(self.font)
		painter.drawText(event.rect(), QtCore.Qt.AlignCenter, self.displayText)  
	
	def setToFirst(self):
		self.isfirst = True
		self.repaint()
		
	def makeActive(self):
		self.isactive = True
		self.textCondense()
		self.repaint()
	
	def makeInactive(self):
		self.isactive = False
		self.textCondense()
		self.repaint()
		
	def mousePressEvent(self,event): 
		self.parent.clicked(self.indexnumber)
	
	
class BreadCrumb(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self)
		self.parent = parent

		self.setStyleSheet("QWidget { border: 0px; }")
		self.style = style.KissyncStyle()
		
		self.setMaximumHeight(89)
		
		self.gridlayout = QtGui.QHBoxLayout()
		self.gridlayout.setAlignment(QtCore.Qt.AlignLeft)
		
		#print self.frameSize().width()
		self.gridlayout.setSpacing(0)
		self.gridlayout.setContentsMargins(0, 0, 0, 0)
		
		# make a widget called
		self.scrollWidget = QtGui.QWidget()
		self.scrollWidget.setLayout(self.gridlayout)

		# scroll area
		self.scrollArea = QtGui.QScrollArea()
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setWidget(self.scrollWidget)
		
		self.scrollArea.setMaximumHeight(90)
		self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		
		# main layout
		self.mainLayout = QtGui.QVBoxLayout()

		# add all main to the main vLayout
		self.mainLayout.addWidget(self.scrollArea)
		
		self.setLayout(self.mainLayout)
		self.mainLayout.setContentsMargins(0, 0, 0, 0)
		
		self.breadcrumbItemNames = []
		self.breadcrumbItems = []
		self.index = 0
		'''
		self.__add("Long Folder Namesdfsdfsdfsdfsdfsdf")
		self.__add("This One Is Long Too")
		self.__add("School")
		self.__add("CS 240")
		self.__add("Bubble Sort")
		'''
		path = "root/something/anotherone/asdfa/asdfasdfasdfasdf/asdhirjfaldsgaalsdgjaskdjlkjlfajkf"
		self.path = path.split("/")
		self.setPath()
		
	def __add(self, name):
		if(len(self.breadcrumbItems) == 0):
			item = Crumb(self, self.style.BLUE, name, 0, self.index)
		else:
			item = Crumb(self, self.style.BLUE, name, 1, self.index)
		self.breadcrumbItemNames.append(name)
		self.breadcrumbItems.append(item)
		self.gridlayout.addWidget(item)
		self.__makeActive(name)
		self.index = self.index + 1
		
	def __removeAfter(self, name):
		elementsToRemove = 0
		indexToStart = self.breadcrumbItemNames.index(name)
		for i in range(len(self.breadcrumbItemNames)):
			if(i > indexToStart):
				self.gridlayout.removeWidget(self.breadcrumbItems[i])
				self.breadcrumbItems[i].close()
				self.path.pop()
				print self.path
				elementsToRemove = elementsToRemove + 1
		for i in range(elementsToRemove):
			self.breadcrumbItems.pop(indexToStart + 1)
			self.breadcrumbItemNames.pop(indexToStart + 1)
			self.index = self.index - 1
	
	def clicked(self, index):
		self.__removeAfter(self.breadcrumbItemNames[index])
		self.__makeActive(self.breadcrumbItemNames[index])
		
	
	def clearActive(self):
		for i in range(len(self.breadcrumbItemNames)):
			self.breadcrumbItems[i].makeInactive()
	
	def __makeActive(self, name):
		indexToMakeActive = self.breadcrumbItemNames.index(name)
		self.clearActive()
		self.breadcrumbItems[indexToMakeActive].makeActive()
		
	def setPath(self):
		print self.path
		for item in self.path:
			self.__add(item)

class Main(QtGui.QWidget):
	def __init__(self, parent = None):
		super(Main, self).__init__(parent)
		self.setWindowTitle('BreadCrumb Widget')  
		
		#self.setStyleSheet("#MainWindow {background-color: #222222; }") 
		self.setGeometry(400, 500, 500, 325)

		self.breadcrumb = BreadCrumb()
		
		grid = QtGui.QGridLayout()
		grid.addWidget(self.breadcrumb)
		
		grid.setContentsMargins(0, 0, 0, 0)
		self.setLayout(grid)

		
if __name__ == "__main__":
	
	#print os.path.realpath(__file__)
	app = QtGui.QApplication(sys.argv)
	mainwindow = Main()
	mainwindow.show()
	sys.exit(app.exec_())
	
	
	
