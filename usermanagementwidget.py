from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
import os, sys


class ManageUserPremissions(QtGui.QWidget):

	def __init__(self, parent = None):
		super(ManageUserPremissions, self).__init__()
		self.parent = parent

		
		self.setWindowTitle('User Premissions')   
		#set the window type to a dialog
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog)
		
		fontDatabase = QtGui.QFontDatabase()
		#fontfile = QtCore.QFile("resources/Roboto-Light-webfont.ttf")
		#fontDatabase.addApplicationFont(os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf")
		#os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf"
		palette = QtGui.QPalette()
		#palette.setColor(QtGui.QPalette.Foreground,QtGui.QColor("#FFFFFF"))
		
		exit=QtGui.QAction(self)
		self.connect(exit,QtCore.SIGNAL('triggered()'),QtCore.SLOT('close()'))
		
		topText = QtGui.QLabel('files premissions')
		#http://pyqt.sourceforge.net/Docs/PyQt4/qfont.html#Weight-enum
		font = QtGui.QFont("Roboto", 32, QtGui.QFont.Light, False)
		topText.setFont(font)
		topText.setPalette(palette)
		topText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		#topText.setStyleSheet("color: #FFFFFF;")

		grid = QtGui.QGridLayout()
		
		#window size constraints
		self.setFixedSize(465, 325)
		
		spacer = QtGui.QWidget()
		spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		#file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		
		formwidget =  QtGui.QWidget()
		formgrid = QtGui.QFormLayout()
		formwidget.setLayout(formgrid)
		
		#Combo Box for User Selection.
		self.comboUser = QtGui.QComboBox(self)
		self.populateComboBox()
		self.comboUser.activated[str].connect(self.onActivated) 

		#self.checkboxOfflineMode = QtGui.QCheckBox('Store All Files Offline', self)
		self.cbWrite = QtGui.QCheckBox('Write', self)
		self.cbDelete = QtGui.QCheckBox('Delete', self)
		self.cbRead = QtGui.QCheckBox('Read', self)
		self.cbView = QtGui.QCheckBox('View', self)
		font = QtGui.QFont("Roboto", 16, QtGui.QFont.Normal, False)
		#self.checkboxOfflineMode.setFont(font)
		#self.checkboxNotifications.setFont(font)
		#self.checkboxOfflineMode.toggle()
		#self.checkboxNotifications.toggle()
		
		finishButton = QtGui.QPushButton('Save Premissions')
		finishButton.clicked.connect(self.savePremissions)
		
		#formgrid.addRow(self.checkboxOfflineMode)
		
		formgrid.addRow(self.comboUser)
		formgrid.addRow(spacer)
		formgrid.addRow(self.cbWrite)
		formgrid.addRow(spacer)
		formgrid.addRow(self.cbDelete)
		formgrid.addRow(spacer)
		formgrid.addRow(self.cbRead)
		formgrid.addRow(spacer)
		formgrid.addRow(self.cbView)
		formgrid.addRow(spacer)
		formgrid.addRow(finishButton)
		
		#add the objects to the grid
		grid.addWidget(spacer, 0, 0)
		grid.addWidget(spacer, 0, 2)
		grid.addWidget(topText, 0, 1)
		grid.addWidget(formwidget, 2, 1)
		grid.addWidget(spacer, 5, 1)
		#set the layout to grid layout
		self.setLayout(grid)
		self.centerOnScreen()
		
	def onActivated(self, text):
		print text
		#print self.path
	def populateComboBox(self):
		tree = self.parent.parent.parent.smartfile.get('/user', '/')
		for i in tree:
			print i['username']
			self.comboUser.addItem(i['username'])
		
			
	def savePremissions(self):
		#Save premissions based upon what is selected.
		pass
	
	def centerOnScreen (self):
		#Center window on screen!
		resolution = QtGui.QDesktopWidget().screenGeometry()
		self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
				(resolution.height() / 2) - (self.frameSize().height() / 2))

	def closeEvent(self, event):
		#Close Event!
		pass
