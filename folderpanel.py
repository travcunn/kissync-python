import math, sys
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg


class FolderPanel(QtGui.QWidget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		self.setStyleSheet("QWidget { background: #FFFFFF; }")
		
		font = QtGui.QFont("Roboto", 24, QtGui.QFont.Normal, False)
		fontsmall = QtGui.QFont("Roboto", 12, QtGui.QFont.Normal, False)
		fontsmallerbold = QtGui.QFont("Roboto", 10, QtGui.QFont.Bold, False)
		fontsmallbold = QtGui.QFont("Roboto", 10, QtGui.QFont.Bold, False)
		
		self.topText = QtGui.QLabel('Actions')
		self.topText.setFont(font)
		self.topText.setAlignment(QtCore.Qt.AlignHCenter)
		
		#Information section
		self.infoTextWidget = QtGui.QWidget()
		self.infoLayout = QtGui.QGridLayout()
		self.infoLayout.addWidget(self.topText, 0, 0, 1, 0, QtCore.Qt.AlignHCenter)
		self.infoTextWidget.setLayout(self.infoLayout)
		self.infoTextWidget.setContentsMargins(20, 0, 20, 20)

		self.gridLayout = QtGui.QGridLayout()
		
		self.gridLayout.addWidget(self.infoTextWidget, 0, 0)
		
		self.gridLayout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.gridLayout)
		
		self.item = None
		
		self.hide()


		
if __name__ == "__main__":
	
	#print os.path.realpath(__file__)
	app = QtGui.QApplication(sys.argv)
	mainwindow = Main()
	mainwindow.show()
	sys.exit(app.exec_())
	
	
	


			
		
		
