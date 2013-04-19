from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg

from square import ItemObject

import style, flowlayout, pprint, os, mimetypes


class FileView(QtGui.QWidget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		##get rid of the widget border
		#self.setStyleSheet("QWidget { border: 0px; }")
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
		self.scrollArea.setStyleSheet("QScrollArea { border: 0px; }")
		
		self.scrollArea.setContentsMargins(0, 0, 0, 0)
		self.scrollWidget.setContentsMargins(0, 0, 0, 0)
		
		# main layout
		self.mainLayout = QtGui.QVBoxLayout()

		# add all main to the main vLayout
		#self.mainLayout.addWidget(self.addButton)
		self.mainLayout.addWidget(self.scrollArea)
		
		self.setLayout(self.mainLayout)
		self.mainLayout.setContentsMargins(10, 0, 0, 0)
		
		self.squareArray = []
		self.activeSquares = []
		
		self.addWidget()

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
			#print i['path']
			if (i['path'].startswith('/.')):
				pass
			else:
				item = ItemObject(self, i['path'], i['name'], i['size'] , i['mime'], i['isdir'], i['time'])
				self.squareArray.append(item)
				self.flowLayout.addWidget(item)
				
		'''
		
		os.chdir(self.parent.parent.sorageDirectory)
		rootPath = self.parent.parent.sorageDirectory + "/"
		fullName = None
		
		for files in os.listdir(self.parent.parent.sorageDirectory):
			print rootPath + files
			print files
			print str(os.stat(rootPath + files).st_size)
			print str( mimetypes.guess_type(rootPath + files, strict=True))
			print str(os.path.isdir(rootPath + files))
			print str(os.stat(rootPath + files).st_mtime)
			print "******************"
			item = ItemObject(self, rootPath + files, files, os.stat(rootPath + files).st_size ,  mimetypes.guess_type(rootPath + files, strict=True)[0], os.path.isdir(rootPath + files), str(os.stat(rootPath + files).st_mtime))
			self.squareArray.append(item)
			self.flowLayout.addWidget(item)
			
			'''
	def setPath(self, path):
		
		#clear current files...
		self.clearAll()
		#print "Cleared all breadcrumbs"
		############set new path
		
		#Get JSON for root
		tree = self.parent.parent.smartfile.get('/path/info' + path, children = True)
		if 'children' not in tree:
			return []
		# Returns all directories and files in directory!
		for i in tree['children']:
			if (i['path'].startswith('/.')):
				pass
			else:
				item = ItemObject(self, i['path'], i['name'], i['size'] , i['mime'], i['isdir'], i['time'])
				self.squareArray.append(item)
				self.flowLayout.addWidget(item)
				
		'''
		self.clearAll()
		
		os.chdir(self.parent.parent.sorageDirectory)
		rootPath = self.parent.parent.sorageDirectory + path
		fullName = None
		for files in os.listdir(self.parent.parent.sorageDirectory + path):
			
			print rootPath + files
			print files
			print str(os.stat(rootPath + files).st_size)
			print str( mimetypes.guess_type(rootPath + files, strict=True))
			print str(os.path.isdir(rootPath + files))
			print str(os.stat(rootPath + files).st_mtime)
			print "******************"
			
			
			
			item = ItemObject(self, rootPath + files, files, os.stat(rootPath + files).st_size ,  mimetypes.guess_type(rootPath + files, strict=True), os.path.isdir(rootPath + files), str(os.stat(rootPath + files).st_mtime))
			self.squareArray.append(item)
			self.flowLayout.addWidget(item)
		'''

	def clearAll(self):
		
		#print self.squareArray
		#print len(self.squareArray)
		for item in self.squareArray:
			#print item
			self.flowLayout.removeWidget(item)
			item.close()
		for i in range(len(self.squareArray)):
			#print "Deleting: " + str(i)
			self.squareArray.pop()
		#print self.squareArray
		#print len(self.squareArray)
	
	def iterateActive(self):
		for item in self.squareArray:
			if(item.isActive):
				self.activeSquares.append(item)
			
	def getActive(self):
		self.activeSquares = []
		self.iterateActive()
		return self.activeSquares
		
	
		
		
