import sys
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg


class SidePanel(QtGui.QWidget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		self.setStyleSheet("QWidget { background: #FFFFFF; }")
		self.gridLayout = QtGui.QGridLayout()
		
		font = QtGui.QFont("Roboto", 24, QtGui.QFont.Normal, False)
		
		topText = QtGui.QLabel('Information')
		topText.setFont(font)
		topText.setAlignment(QtCore.Qt.AlignHCenter)
		
		panelTextWidget = QtGui.QWidget()
		panelLayout = QtGui.QGridLayout()
		panelLayout.addWidget(topText)
		panelTextWidget.setLayout(panelLayout)
		panelTextWidget.setContentsMargins(20, 0, 20, 20)

		self.gridLayout.addWidget(panelTextWidget, 0, 0)
		self.gridLayout.setContentsMargins(0, 0, 0, 0)
		
		self.setLayout(self.gridLayout)
		
		

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
	
	
	


			
		
		
