import math, sys
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg

from square import ItemObject

class SidePanel(QtGui.QWidget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		self.setStyleSheet("QWidget { background: #FFFFFF; }")
		self.gridLayout = QtGui.QGridLayout()
		
		font = QtGui.QFont("Roboto", 24, QtGui.QFont.Normal, False)
		fontsmall = QtGui.QFont("Roboto", 12, QtGui.QFont.Normal, False)
		
		self.topText = QtGui.QLabel('Information')
		self.topText.setFont(font)
		self.topText.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.numberSelected = QtGui.QLabel()
		self.numberSelected.setFont(fontsmall)
		self.numberSelected.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.sizeSelected = QtGui.QLabel()
		self.sizeSelected.setFont(fontsmall)
		self.sizeSelected.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.panelTextWidget = QtGui.QWidget()
		self.panelLayout = QtGui.QFormLayout()
		self.panelLayout.addRow(self.topText)
		self.panelLayout.addRow(self.numberSelected)
		self.panelLayout.addRow(self.sizeSelected)
		self.panelTextWidget.setLayout(self.panelLayout)
		self.panelTextWidget.setContentsMargins(20, 0, 20, 20)

		self.gridLayout.addWidget(self.panelTextWidget, 0, 0)
		
		self.gridLayout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.gridLayout)
		
		self.item = None
		
		self.hide()
	
	def updateView(self):
		numberOfItems = 0
		for item in self.parent.fileview.getActive():
			numberOfItems = numberOfItems + 1
			
		if(numberOfItems > 1):
			self.panelLayout.removeWidget(item)
			self.item.close()
			self.numberSelected.setText(str(numberOfItems) + " items selected.")
		else:
			#self.parent.fileview.squareArray[0]
			self.item = ItemObject(self, self.parent.fileview.activeSquares[0].filePath, self.parent.fileview.activeSquares[0].fileName, self.parent.fileview.activeSquares[0].fileSize, self.parent.fileview.activeSquares[0].fileType, self.parent.fileview.activeSquares[0].isFolder, True)
			self.panelLayout.addWidget(self.item)
			self.numberSelected.setText("1 item selected.")
			
		#update the size total
		self.updateSizes()
	
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
		self.updateView()
		self.show()
		
	def deactivate(self):
		if not(self.item == None):
			self.panelLayout.removeWidget(self.item)
			self.sizeSelected.setText("")
			self.numberSelected.setText("")
			self.item.close()
		self.hide()
		

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
	
	
	


			
		
		
