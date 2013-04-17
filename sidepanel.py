import math, os, sys
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg

from square import ItemObject

class SidePanel(QtGui.QWidget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		self.setStyleSheet("QWidget { background: #FFFFFF; }")
		
		font = QtGui.QFont("Roboto", 24, QtGui.QFont.Normal, False)
		fontsmall = QtGui.QFont("Roboto", 12, QtGui.QFont.Normal, False)
		fontsmallerbold = QtGui.QFont("Roboto", 10, QtGui.QFont.Bold, False)
		fontsmallbold = QtGui.QFont("Roboto", 10, QtGui.QFont.Bold, False)
		
		self.numberSelected = QtGui.QLabel()
		self.numberSelected.setFont(fontsmall)
		self.numberSelected.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.actionsText = QtGui.QLabel('Actions')
		self.actionsText.setFont(font)
		self.actionsText.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.topText = QtGui.QLabel('Information')
		self.topText.setFont(font)
		self.topText.setAlignment(QtCore.Qt.AlignHCenter)
		
		
		self.fileNameTitle = QtGui.QLabel()
		self.fileNameTitle.setText("Filename:")
		self.fileNameTitle.setFont(fontsmallbold)
		self.fileNameTitle.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.fileNameText = QtGui.QLabel()
		self.fileNameText.setFont(fontsmall)
		self.fileNameText.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.fileTypeTitle = QtGui.QLabel()
		self.fileTypeTitle.setText("Type:")
		self.fileTypeTitle.setFont(fontsmallbold)
		self.fileTypeTitle.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.fileTypeText = QtGui.QLabel()
		self.fileTypeText.setFont(fontsmall)
		self.fileTypeText.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.lastModifiedTitle = QtGui.QLabel()
		self.lastModifiedTitle.setText("Last Modified:")
		self.lastModifiedTitle.setFont(fontsmallbold)
		self.lastModifiedTitle.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.lastModifiedText = QtGui.QLabel()
		self.lastModifiedText.setFont(fontsmall)
		self.lastModifiedText.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.sizeSelectedTitle = QtGui.QLabel()
		self.sizeSelectedTitle.setFont(fontsmallbold)
		self.sizeSelectedTitle.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.sizeSelected = QtGui.QLabel()
		self.sizeSelected.setFont(fontsmall)
		self.sizeSelected.setAlignment(QtCore.Qt.AlignHCenter)
		
		#Information section
		self.infoTextWidget = QtGui.QWidget()
		self.infoLayout = QtGui.QGridLayout()
		self.infoLayout.addWidget(self.topText, 0, 0, 1, 0, QtCore.Qt.AlignHCenter)
		self.infoLayout.addWidget(self.numberSelected, 1, 0, 1, 0, QtCore.Qt.AlignHCenter)
		self.infoLayout.addWidget(self.fileNameTitle, 2, 0)
		self.infoLayout.addWidget(self.fileNameText, 2, 1)
		self.infoLayout.addWidget(self.fileTypeTitle, 3, 0)
		self.infoLayout.addWidget(self.fileTypeText, 3, 1)
		self.infoLayout.addWidget(self.sizeSelectedTitle, 4, 0)
		self.infoLayout.addWidget(self.sizeSelected, 4, 1)
		self.infoLayout.addWidget(self.lastModifiedTitle, 5, 0)
		self.infoLayout.addWidget(self.lastModifiedText, 5, 1)
		self.infoTextWidget.setLayout(self.infoLayout)
		self.infoTextWidget.setContentsMargins(20, 0, 20, 20)

		self.gridLayout = QtGui.QGridLayout()
		
		#buttons
		self.addButton = PanelButton(self, "add")
		
		self.gridLayout.addWidget(self.infoTextWidget, 0, 0)
		self.gridLayout.addWidget(self.addButton, 0, 1)
		#self.gridLayout.addWidget(self.actionsText, 1, 0)
		
		self.gridLayout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.gridLayout)
		
		self.item = None
		
		self.hide()
	
	def updateView(self):
		numberOfItems = 0
		for item in self.parent.fileview.getActive():
			numberOfItems = numberOfItems + 1
			
		if(numberOfItems > 1):
			#set the max size with less info in the info panel
			self.infoTextWidget.setMaximumHeight(130)
			self.infoLayout.removeWidget(item)
			self.item.close()
			self.numberSelected.setText(str(numberOfItems) + " items selected.")
			self.sizeSelectedTitle.setText("Size of Selection: ")
			self.hideSingle()
		else:
			#set the max size on one object
			self.infoTextWidget.setMaximumHeight(185)
			#self.parent.fileview.squareArray[0]
			self.item = ItemObject(self, self.parent.fileview.activeSquares[0].filePath, self.parent.fileview.activeSquares[0].fileName, self.parent.fileview.activeSquares[0].fileSize, self.parent.fileview.activeSquares[0].fileType, self.parent.fileview.activeSquares[0].isFolder, self.parent.fileview.activeSquares[0].lastModified, True)
			#self.infoLayout.addWidget(self.item, 10, 0, 1, 0, QtCore.Qt.AlignHCenter)
			self.numberSelected.setText("1 item selected.")
			self.sizeSelectedTitle.setText("Size: ")
			
			#only details for only single files
			filetype = self.parent.fileview.activeSquares[0].fileType
			if not (len(filetype) <= 24):
				cut = len(filetype) - 24
				filetype = filetype.replace(filetype[-cut:], '...')
			
			self.fileNameText.setText(self.parent.fileview.activeSquares[0].fileName)
			self.fileTypeText.setText(filetype)
			self.lastModifiedText.setText(self.item.lastModified.replace("T", " "))
			self.showSingle()
			
	def hideSingle(self):
		self.fileNameTitle.hide()
		self.fileNameText.hide()
		self.fileTypeTitle.hide()
		self.fileTypeText.hide()
		self.lastModifiedTitle.hide()
		self.lastModifiedText.hide()
	
	def showSingle(self):
		self.fileNameTitle.show()
		self.fileNameText.show()
		self.fileTypeTitle.show()
		self.fileTypeText.show()
		self.lastModifiedTitle.show()
		self.lastModifiedText.show()
			
	
	def updateSizes(self):
		totalsize = 0
		for item in self.parent.fileview.getActive():
			totalsize = totalsize + item.fileSize
		
		thissize = totalsize
		if(thissize < 1024):
			measurement = "bytes"
		elif(thissize < int(math.pow(1024, 2))):
			thissize = thissize/1024
			measurement = "kB"
		elif(thissize < int(math.pow(1024, 3))):
			thissize = thissize/int(math.pow(1024, 2))
			measurement = "mB"
		else:
			thissize = thissize/int(math.pow(1024, 3))
			measurement = "gb"
		totalsize = thissize
		self.sizeSelected.setText(str(totalsize) + " " + measurement)
	
	def activate(self):
		#update selection count
		self.updateView()
		
		#update the size total
		self.updateSizes()
		
		#show the widget
		self.show()
		
	def deactivate(self):
		if not(self.item == None):
			self.infoLayout.removeWidget(self.item)
			self.sizeSelected.setText("")
			self.numberSelected.setText("")
			self.item.close()
		self.hide()
		
		
class PanelButton(QtGui.QWidget):
	def __init__(self, parent = None, buttonType = None):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		self.buttonType = buttonType
		
		##get rid of the widget border
		self.setStyleSheet("QWidget { border: 0px; }")
		
		self.setMinimumSize(48, 48)
		self.setMaximumSize(48, 48)
		
		self.gridlayout = QtGui.QGridLayout()
		
		self.setLayout(self.gridlayout)
		self.addIcon(self.buttonType)
		

	def addIcon(self, buttonType):
		self.icon = QtGui.QImage()
		print buttonType
		self.icon.load(os.path.dirname(os.path.realpath(__file__)) + "/icons/simplicio/icons48/" + buttonType + ".png")
		
		self.icontarget = QtCore.QRectF(0, 0, 48, 48)
        
	def paintEvent(self, e):
		painter = QtGui.QPainter()
		painter.begin(self)
				
		# Draw Item Thumbnail.
		painter.drawImage(self.icontarget, self.icon)
		
		#End Painter
		painter.end()
		

class Main(QtGui.QWidget):
	def __init__(self, parent = None):
		super(Main, self).__init__(parent)
		self.setWindowTitle('Side Panel')  
		
		self.grid = QtGui.QGridLayout()
		
		self.sidepanel = SidePanel(self)
		self.grid.addWidget(self.sidepanel)
		self.setLayout(self.grid)


		
if __name__ == "__main__":
	
	#print os.path.realpath(__file__)
	app = QtGui.QApplication(sys.argv)
	mainwindow = Main()
	mainwindow.show()
	sys.exit(app.exec_())
	
	
	


			
		
		
