from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
from fileview import FileView

import breadcrumb

class FileBrowserGUI(QtGui.QWidget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		
		self.breadcrumb = breadcrumb.BreadCrumb(self.parent)	
		self.fileview = FileView(self.parent)	

		self.layoutgrid = QtGui.QGridLayout()
		self.layoutgrid.addWidget(self.breadcrumb)
		self.layoutgrid.addWidget(self.fileview)
		
		self.setLayout(self.layoutgrid)
