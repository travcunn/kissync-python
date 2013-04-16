from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
from fileview import FileView
from breadcrumb import BreadCrumb
from folderpanel import FolderPanel
from sidepanel import SidePanel

class FileBrowserGUI(QtGui.QWidget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		
		self.breadcrumb = BreadCrumb(self)	
		self.fileview = FileView(self)	
		self.sidepanel = SidePanel(self)
		self.folderpanel = FolderPanel(self)

		self.layoutgrid = QtGui.QGridLayout()
		self.layoutgrid.addWidget(self.breadcrumb, 0, 0, 1, 2, QtCore.Qt.AlignLeft)
		self.layoutgrid.addWidget(self.fileview, 1, 0)
		self.layoutgrid.addWidget(self.sidepanel, 1, 1)
		self.layoutgrid.addWidget(self.folderpanel, 1, 1)
		self.folderpanel.show()
		
		self.layoutgrid.setContentsMargins(0, 0, 0, 0)
		
		self.setLayout(self.layoutgrid)
	
	def changePath(self, path):
		print "Changing path to " + path
		self.breadcrumb.setPath(path)
		self.fileview.setPath(path)
