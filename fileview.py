from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg

from TaylorSquare import ItemObject

import style, flowlayout


class FileView(QtGui.QWidget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		##get rid of the widget border
		#self.setStyleSheet("border: 0px")
		self.style = style.KissyncStyle()
		
		topText = QtGui.QLabel('Kissync File View Widget Test')
		 
		self.addButton = QtGui.QPushButton('button to add other widgets')
		self.addButton.clicked.connect(self.addWidget)
		
		# flow layout, which will be inside the scroll area called scrollArea
		self.flowLayout = flowlayout.FlowLayout(self, 0, 10)

		# make a widget called
		self.scrollWidget = QtGui.QWidget()
		self.scrollWidget.setLayout(self.flowLayout)
		#set the borders around the scroll widget
		self.scrollWidget.setContentsMargins(10, 10, 10, 10)

		# scroll area
		self.scrollArea = QtGui.QScrollArea()
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setWidget(self.scrollWidget)
		
		self.scrollArea.setContentsMargins(0, 0, 0, 0)
		self.scrollWidget.setContentsMargins(0, 0, 0, 0)
		
		# main layout
		self.mainLayout = QtGui.QVBoxLayout()

		# add all main to the main vLayout
		self.mainLayout.addWidget(self.addButton)
		self.mainLayout.addWidget(self.scrollArea)
		
		self.setLayout(self.mainLayout)
		self.mainLayout.setContentsMargins(0, 0, 0, 0)

	def addWidget(self):
		#self.flowLayout.addWidget(SquareObject(self, self.style.PINK))
		self.flowLayout.addWidget(ItemObject(self, "IAmAFileNameBecauseIAmCool.html", "I am Path", "400.0kB" , "text/application", True))
