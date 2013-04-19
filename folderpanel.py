import math, sys, os
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
from panelbutton import PanelButton
import flowlayout, shutil


class FolderPanel(QtGui.QWidget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		self.setStyleSheet("QWidget { background: #FFFFFF; }")
		
		font = QtGui.QFont("Roboto", 24, QtGui.QFont.Normal, False)
		fontsmall = QtGui.QFont("Roboto", 12, QtGui.QFont.Normal, False)
		fontsmallerbold = QtGui.QFont("Roboto", 10, QtGui.QFont.Bold, False)
		fontsmallbold = QtGui.QFont("Roboto", 10, QtGui.QFont.Bold, False)
		
		self.topText = QtGui.QLabel('       ')
		self.topText.setFont(font)
		self.topText.setAlignment(QtCore.Qt.AlignHCenter)
		
		#Information section
		self.infoTextWidget = QtGui.QWidget()
		self.infoLayout = QtGui.QGridLayout()
		self.infoLayout.addWidget(self.topText, 0, 0, 1, 0, QtCore.Qt.AlignHCenter)
		self.infoTextWidget.setLayout(self.infoLayout)
		self.infoTextWidget.setContentsMargins(20, 0, 20, 20)
		
		#GRIDLAYOUT
		self.gridLayout = QtGui.QGridLayout()
		
		#buttons
		self.buttonsWidget = QtGui.QWidget()
		self.buttonsLayout = flowlayout.FlowLayout(self)
		self.buttonsWidget.setLayout(self.buttonsLayout)
		
		#self.buttonsWidget.setContentsMargins(10, 10, 10, 10)
		#buttons add to layout
		self.addButton = PanelButton(self, "add")
		self.refreshButton = PanelButton(self, "refresh")
		
		self.buttonsLayout.addWidget(self.addButton)
		self.buttonsLayout.addWidget(self.refreshButton)
		
		self.gridLayout.addWidget(self.infoTextWidget, 0, 1)
		self.gridLayout.addWidget(self.buttonsWidget, 0, 0)
		
		
		
		
		
		
		self.gridLayout.addWidget(self.infoTextWidget, 0, 0)
		
		self.gridLayout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.gridLayout)
		
		self.item = None
		
		self.hide()
	def buttonClicked(self, buttonType):
		button = buttonType.lower()
		if (button == "add"):
			print "Add pressed."
			##Open Dialog
			source_file = QtGui.QFileDialog.getOpenFileName(self, 'Open file', os.path.expanduser("~"))
			## Print File Name
			#print str(fname)
			destination_folder = os.path.expanduser("~") + "/Kissync" + self.parent.breadcrumb.currentPath
			print "Source: " + source_file
			print "Dest: " + destination_folder
			#if not os.path.exists(destination_folder):
				#os.makedirs(destination_folder)
			#os.rename(source_file,destination_folder)
			if not (str(source_file) == "" or str(source_file) == None):
				shutil.move(str(source_file),str(destination_folder))
			else:
				print "User canceled upload dialog"
			#deleteFileName = self.parent.fileview.squareArray[0].filePath
			#print deleteFileName
			#print self.parent.fileview.squareArray[0].filePath[:deleteFileName + 1]
			#self.parent.changePath(self.parent.fileview.squareArray[0].filePath[:deleteFileName + 1])
			
			#### NEED TO ADD REFRESH FILEVIEW #########
			#Refreshes FileVIEW
			Filenm = self.parent.fileview.activeSquares[0].filePath.rfind('/')
			#Prints out the directory...
			#print self.parent.fileview.activeSquares[0].filePath[:deleteFileName + 1] 
			self.parent.changePath(self.parent.fileview.activeSquares[0].filePath[:Filenm + 1])
		elif (button == "refresh"):
			
			Filenm = self.parent.fileview.squareArray[0].filePath.rfind('/')
			#Prints out the directory...
			#print self.parent.fileview.activeSquares[0].filePath[:deleteFileName + 1] 
			self.parent.changePath(self.parent.fileview.squareArray[0].filePath[:Filenm + 1])
		else:
			print "Op. that button isn't alive yet!"
		

		
if __name__ == "__main__":
	
	#print os.path.realpath(__file__)
	app = QtGui.QApplication(sys.argv)
	mainwindow = Main()
	mainwindow.show()
	sys.exit(app.exec_())
	
	
	


			
		
		
