import os, platform, sys, time, urllib2
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg

import authwindow, flowlayout, style

class SquareObject(QtGui.QWidget):
    
	def __init__(self, parent, color = None):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		
		self.squareWidth = 180
		self.squareHeight = 90
		
		self.initUI()
		
		self.icon = QtGui.QImage()
		self.icon.load(os.path.dirname(os.path.realpath(__file__)) + "/icons/faience/mimetypes/x-office-presentation.svg")
		self.icontarget = QtCore.QRectF(0, 0, 64, 64)
		
		self.closebutton = QtGui.QImage()
		self.closebutton.load(os.path.dirname(os.path.realpath(__file__)) + "/icons/bwpx-icns/icons/symbol_multiplication.gif")
		self.closebuttontarget = QtCore.QRectF((self.squareWidth - 18), 0, 18, 18)
		
		if(color == None):
			self.color = parent.style.BLUE
		else:
			self.color = color
		self.color = parent.style.hexToQColor(self.color)
        
	def initUI(self):      
		print "Creating a square..."
		self.setFixedSize(self.squareWidth, self.squareHeight)
		self.opacity = 0.0
		
		self.timeline = QtCore.QTimeLine()
		self.timeline.valueChanged.connect(self.animate)
		self.timeline.setDuration(500)
		self.timeline.start()
		self.show()

	#this is called every time something needs to be repainted
	def paintEvent(self, e):
		painter = QtGui.QPainter()
		painter.begin(self)
		painter.setOpacity(self.opacity)
		self.drawSquare(painter)
		painter.drawImage(self.icontarget, self.icon)
		painter.drawImage(self.closebuttontarget, self.closebutton)
		painter.end()
        
	def drawSquare(self, painter):
		#get rid of the pen... gets rid of outline on drawing
		painter.setPen(QtCore.Qt.NoPen)
		#windows 8 colors are pretty http://www.creepyed.com/2012/09/windows-8-colors-hex-code/
		painter.setBrush(self.color)
		#from docs: drawRect (self, int x, int y, int w, int h)
		painter.drawRect(0, 0, self.squareWidth, self.squareHeight)
	
	def animate(self, value):
		self.opacity = value * self.parent.style.SQUAREOPACITY
		self.repaint()
		
	def enterEvent(self,event): 
		print("Enter") 
		self.opacity = 1.0
		self.repaint()
	
	def leaveEvent(self,event): 
		print("Leave") 
		self.opacity = self.parent.style.SQUAREOPACITY
		self.repaint()
	
	def mousePressEvent(self,event): 
		print("Widget clicked event") 
		self.repaint()
	
	
class FileView(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__(self)

		##get rid of the widget border
		#self.setStyleSheet("border: 0px")
		self.style = style.KissyncStyle()
		
		topText = QtGui.QLabel('Kissync File View Widget Test')
		 
		self.addButton = QtGui.QPushButton('button to add other widgets')
		self.addButton.clicked.connect(self.addWidget)
		
		# flow layout, which will be inside the scroll area called scrollArea
		self.flowLayout = flowlayout.FlowLayout(None, 10)

		# make a widget called
		self.scrollWidget = QtGui.QWidget()
		self.scrollWidget.setLayout(self.flowLayout)
		#set the borders around the scroll widget
		self.scrollWidget.setContentsMargins(10, 10, 10, 10)

		# scroll area
		self.scrollArea = QtGui.QScrollArea()
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setWidget(self.scrollWidget)

		# main layout
		self.mainLayout = QtGui.QVBoxLayout()

		# add all main to the main vLayout
		self.mainLayout.addWidget(self.addButton)
		self.mainLayout.addWidget(self.scrollArea)
		
		self.setLayout(self.mainLayout)

	def addWidget(self):
		self.flowLayout.addWidget(SquareObject(self, self.style.PINK))
		self.flowLayout.addWidget(SquareObject(self, self.style.PURPLE))
		self.flowLayout.addWidget(SquareObject(self, self.style.TEAL))
		self.flowLayout.addWidget(SquareObject(self, self.style.BLUE))
		self.flowLayout.addWidget(SquareObject(self, self.style.LIME))
		self.flowLayout.addWidget(SquareObject(self, self.style.ORANGE))
		self.flowLayout.addWidget(SquareObject(self, self.style.RED))


class MainWindow(QtGui.QWidget):
	def __init__(self, parent = None):
		super(MainWindow, self).__init__(parent)
		self.setWindowTitle('Keep It Simple Sync')  
		
		self.displayFont = QtGui.QFont()
		#self.setStyleSheet("#MainWindow {background-color: #222222; }") 
		self.setGeometry(400, 200, 1000, 500)
		
		fontDatabase = QtGui.QFontDatabase()
		#fontfile = QtCore.QFile("resources/Roboto-Light-webfont.ttf")
		fontDatabase.addApplicationFont(os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf")
		os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf"
		palette = QtGui.QPalette()
		#palette.setColor(QtGui.QPalette.Foreground,QtGui.QColor("#FFFFFF"))
		
		topText = QtGui.QLabel('kisSync')
		#http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
		font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
		topText.setFont(font)
		topText.setPalette(palette)
		#topText.setStyleSheet("color: #FFFFFF;")

		fileview = FileView()	
		
		grid = QtGui.QGridLayout()
		#grid.setContentsMargins(0, 0, 0, 0)
		grid.addWidget(topText)
		grid.addWidget(fileview)

		self.setLayout(grid)

if __name__ == "__main__":
	
	#print os.path.realpath(__file__)
	app = QtGui.QApplication(sys.argv)
	loginwindow = authwindow.LoginWindow()
	loginwindow.show()
	mainwindow = MainWindow()
	mainwindow.show()
	sys.exit(app.exec_())
