from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg

from square import ItemObject

import style, flowlayout, pprint


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
		
		#Get JSON for root
		tree = self.parent.parent.smartfile.get('/path/info', children = True)
		if 'children' not in tree:
			return []
		# Returns all directories and files in root!
		self.rootD = [i['path'].encode("utf-8") for i in tree['children']]
		#rootDisDir = [i['isdir'].encode("utf-8") for i in tree['children']]
		
		for i in tree['children']:
			print i['path']
			self.flowLayout.addWidget(ItemObject(self, i['path'][0:len(i['path'])], i['size'] , "text/application", i['isdir']))
