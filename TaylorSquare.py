import os, platform, sys, time, urllib2
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg

import style

class IconWidget(QtGui.QWidget):
	
	def __init__(self, parent = None, extension = None):
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
		if(self.isFolder == True):
			extension = "folder"
		elif(extension == None):
			extension = "unknown"
		else:
			extension = extension[1:]
		print extension
		self.icon.load(os.path.dirname(os.path.realpath(__file__)) + "/icons/faience/mimetypes/" + extension + ".svg")
		
		self.icontarget = QtCore.QRectF(0, 0, 64, 64)
        
	#this is called every time something needs to be repainted
	def paintEvent(self, e):
		#Start Painter
		painter = QtGui.QPainter()
		painter.begin(self)
				
		# Draw Item Thumbnail.
		painter.drawImage(self.icontarget, self.icon)
		
		#End Painter
		painter.end()

class ItemObject(QtGui.QWidget):
	def __init__(self, parent = None, fileName = None, filePath = None, fileSize = None, fileType = None, isFolder = False):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		
		blue = "1BA1E2"
		self.qcolorblue = QtGui.QColor(int(blue[:2], 16), int(blue[2:4], 16), int(blue[4:], 16), 255)
		
		#Item Properties
		self.fileName = fileName
		self.filePath = filePath
		self.fileSize = fileSize
		self.fileType = fileType
		self.isActive = False
		self.isFolder = isFolder
		
		#get rid of the widget border
		self.setStyleSheet("QWidget { border: 0px; }")
		self.setMaximumSize(200, 90)
		self.setGeometry(0,0,self.frameSize().width() - 50,self.frameSize().height() - 50)
		
		self.gridlayout = QtGui.QGridLayout()
		
		self.rows = 3
		self.cols = 2
		
		#Get file extension and type
		if (self.fileName.rfind('.') != -1):
			dotIndex = self.fileName.rfind('.')
			print dotIndex
			fileNameLength = len(self.fileName)
			print fileNameLength
			extension = self.fileName[dotIndex:fileNameLength]
		else:
			extension = None
			
		print extension
		
		#Icon
		self.icon = IconWidget(self, extension)
		self.gridlayout.addWidget(self.icon, 1 , 1, 3, 1 , QtCore.Qt.AlignLeft)
		
		#Delete Button
		self.deleteMeButton = QtGui.QPushButton('X')
		self.deleteMeButton.setStyleSheet('QPushButton {color: White}')
		self.deleteMeButton.clicked.connect(self.deleteMe)
		self.gridlayout.addWidget(self.deleteMeButton, 1, 2, QtCore.Qt.AlignRight)
		
		#File Name Label
		self.lbFileName = QtGui.QLabel(self.fileName)
		self.lbFileName.setStyleSheet('QLabel {color: White}')
		self.gridlayout.addWidget(self.lbFileName, 2, 2, QtCore.Qt.AlignLeft)
		
		#File Size Label
		self.lbFileSize = QtGui.QLabel(self.fileSize)
		self.lbFileSize.setStyleSheet('QLabel {color: #222222}')
		self.gridlayout.addWidget(self.lbFileSize, 3, 2, QtCore.Qt.AlignLeft)
		
		self.setLayout(self.gridlayout)
		
		self.opacity = 0.0
		self.timeline = QtCore.QTimeLine()
		self.timeline.valueChanged.connect(self.animate)
		self.timeline.setDuration(500)
		self.timeline.start()
		
	#this is called every time something needs to be repainted
	def paintEvent(self, e):
		#Start Painter
		painter = QtGui.QPainter()
		painter.begin(self)
		#Set Opacity
		painter.setOpacity(self.opacity)
		#Draw Background Color
		self.draw(painter)	
		#End Painter
		painter.end()
		
	def draw(self, painter):
		penbold = QtGui.QPen(QtCore.Qt.black, 5, QtCore.Qt.SolidLine)
		penblank = QtGui.QPen(QtCore.Qt.black, -1, QtCore.Qt.SolidLine)

		painter.setPen(penblank)
		
		painter.setBrush(self.qcolorblue)
		painter.drawRect(0, 0, self.frameSize().width(), self.frameSize().height())	
		
		
	def animate(self, value):
		self.opacity = value * 0.5
		self.repaint()
		
	def mousePressEvent(self, event):
		print("Clicked")
		if not(self.isActive == True):
			self.isActive = True
			self.opacity = 1.0
		else:
			self.isActive = False
			self.opacity = 0.5
			
		self.repaint()
	
	def enterEvent(self,event): 
		print("Enter") 
		self.opacity = 1.0
		self.repaint()
	
	def leaveEvent(self,event): 
		print("Leave") 
		if not(self.isActive == True):
			self.opacity = 0.5
			
		self.repaint()
	
	def deleteMe(self):
		#This will delete it's self.
		print "Delete button clicked!"
	
		pass

class Main(QtGui.QWidget):
	def __init__(self, parent = None):
		super(Main, self).__init__(parent)
		self.setWindowTitle('Keep It Simple Sync')  
		
		#self.setStyleSheet("#MainWindow {background-color: #222222; }") 
		self.setGeometry(400, 200, 300, 325)
		
		self.style = style.KissyncStyle()
		self.loadingwidget = ItemObject(self, "index.html", "I am Path", "400.0kB" , "text/application", True)

		self.grid = QtGui.QGridLayout()
		
		self.loginButton = QtGui.QPushButton('Add Square')
		self.loginButton.clicked.connect(self.addSquare)
		self.grid.addWidget(self.loginButton)
		
		self.grid.addWidget(self.loadingwidget)

		self.setLayout(self.grid)
		
	def addSquare(self):
		
		for x in range(0, 4):
			self.grid.addWidget(ItemObject(self, str(x)))
			
		
		
		
		"""
		self.timeline1 = QtCore.QTimeLine()
		self.timeline1.valueChanged.connect(self.destroyer)
		self.timeline1.setDuration(2000)
		self.timeline1.start()
	
	def destroyer(self, timercount):
		if(timercount == 1.0):
			self.loadingwidget.counter()
		"""

		
if __name__ == "__main__":
	
	#print os.path.realpath(__file__)
	app = QtGui.QApplication(sys.argv)
	mainwindow = Main()
	mainwindow.show()
	sys.exit(app.exec_())
	
	
	

