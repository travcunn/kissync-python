import math, os, sys
from PyQt4 import QtCore, QtGui, QtWebKit, QtSvg
from square import ItemObject
import webbrowser

from panelbutton import PanelButton

import flowlayout, shutil

#Copy and paste library.. platform independent.
import pyperclip

from usermanagementwidget import ManageUserPermissions


class BottomPanel(QtGui.QWidget):
	def __init__(self, parent):
		QtGui.QWidget.__init__(self)
		self.parent = parent
		self.setStyleSheet("QWidget { background: #FFFFFF; }")
		
		self.manageUser = ManageUserPermissions(self)
		
		self.setMinimumSize(50, 64)
		self.setMaximumHeight(68)
		
		font = QtGui.QFont("Roboto", 18, QtGui.QFont.Normal, False)
		fontsmall = QtGui.QFont("Roboto", 12, QtGui.QFont.Normal, False)
		fontsmallerbold = QtGui.QFont("Roboto", 10, QtGui.QFont.Bold, False)
		fontsmallbold = QtGui.QFont("Roboto", 10, QtGui.QFont.Bold, False)
		
		self.numberSelected = QtGui.QLabel()
		self.numberSelected.setFont(fontsmall)
		self.numberSelected.setAlignment(QtCore.Qt.AlignHCenter)
		
		#self.actionsText = QtGui.QLabel('Actions')
		#self.actionsText.setFont(font)
		#self.actionsText.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.topText = QtGui.QLabel('Information')
		self.topText.setFont(font)
		self.topText.setAlignment(QtCore.Qt.AlignHCenter)
		
		"""
		self.fileNameTitle = QtGui.QLabel()
		self.fileNameTitle.setText("Filename:")
		self.fileNameTitle.setFont(fontsmallbold)
		self.fileNameTitle.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.fileNameText = QtGui.QLabel()
		self.fileNameText.setFont(fontsmall)
		self.fileNameText.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.fileTypeTitle = QtGui.QLabel()
		self.fileTypeTitle.setText("Type:")
		self.fileTypeTitle.setFont(fontsmallbold)
		self.fileTypeTitle.setAlignment(QtCore.Qt.AlignHCenter)
		"""
		self.fileTypeText = QtGui.QLabel()
		self.fileTypeText.setFont(fontsmall)
		self.fileTypeText.setAlignment(QtCore.Qt.AlignHCenter)
		
		"""
		self.lastModifiedTitle = QtGui.QLabel()
		self.lastModifiedTitle.setText("Last Modified:")
		self.lastModifiedTitle.setFont(fontsmallbold)
		self.lastModifiedTitle.setAlignment(QtCore.Qt.AlignHCenter)
		"""
		
		self.lastModifiedText = QtGui.QLabel()
		self.lastModifiedText.setFont(fontsmall)
		self.lastModifiedText.setAlignment(QtCore.Qt.AlignHCenter)
		
		self.sizeSelectedTitle = QtGui.QLabel()
		self.sizeSelectedTitle.setFont(fontsmallbold)
		self.sizeSelectedTitle.setAlignment(QtCore.Qt.AlignHCenter)

		self.sizeSelected = QtGui.QLabel()
		self.sizeSelected.setFont(fontsmall)
		self.sizeSelected.setAlignment(QtCore.Qt.AlignHCenter)

		
		#Information section
		self.infoTextWidget = QtGui.QWidget()
		self.infoTextWidget.setMaximumWidth(300)
		self.infoLayout = QtGui.QGridLayout()
		self.infoLayout.addWidget(self.topText, 0, 0, QtCore.Qt.AlignHCenter)
		self.infoLayout.addWidget(self.numberSelected, 1, 0, QtCore.Qt.AlignHCenter)
		#self.infoLayout.addWidget(self.fileTypeText, 0, 1)
		#self.infoLayout.addWidget(self.sizeSelected, 1, 1)
		self.infoLayout.addWidget(self.lastModifiedText, 1, 0)
		self.infoTextWidget.setLayout(self.infoLayout)
		self.infoTextWidget.setContentsMargins(0, 0, 0, 0)

		self.gridLayout = QtGui.QGridLayout()
		
		#buttons
		self.buttonsWidget = QtGui.QWidget()
		self.buttonsLayout = flowlayout.FlowLayout(self)
		self.buttonsWidget.setLayout(self.buttonsLayout)
		#self.buttonsWidget.setContentsMargins(10, 10, 10, 10)
		
		#create buttons
		self.addButton = PanelButton(self, "add")
		self.deleteButton = PanelButton(self, "delete")
		self.moveButton = PanelButton(self, "move")
		self.renameButton = PanelButton(self, "rename")
		self.generateLinkButton = PanelButton(self, "generate_link")
		self.userPremissionButton = PanelButton(self, "user_premissions")
		
		#add buttons to layout
		self.buttonsLayout.addWidget(self.addButton)
		self.buttonsLayout.addWidget(self.deleteButton)
		self.buttonsLayout.addWidget(self.moveButton)
		self.buttonsLayout.addWidget(self.renameButton)
		self.buttonsLayout.addWidget(self.generateLinkButton)
		self.buttonsLayout.addWidget(self.userPremissionButton)
	
		
		self.gridLayout.addWidget(self.infoTextWidget, 0, 1)
		self.gridLayout.addWidget(self.buttonsWidget, 0, 0)
		#self.gridLayout.addWidget(self.actionsText, 1, 0)
		
		self.gridLayout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.gridLayout)
		
		self.item = None
		
		self.hide()
	
	def updateView(self):
		numberOfItems = 0
		for item in self.parent.fileview.getActive():
			numberOfItems = numberOfItems + 1
			
		if(numberOfItems > 1):
			#set the max size with less info in the info panel
			self.infoTextWidget.setMaximumHeight(130)
			self.infoLayout.removeWidget(item)
			self.item.close()
			self.topText.setText("Multiple Files")
			self.numberSelected.setText(str(numberOfItems) + " items selected.")
			#self.sizeSelectedTitle.setText("Size of Selection: ")
			self.hideSingle()
		else:
			#set the max size on one object
			self.infoTextWidget.setMaximumHeight(185)
			#self.parent.fileview.squareArray[0]
			self.item = ItemObject(self, self.parent.fileview.activeSquares[0].filePath, self.parent.fileview.activeSquares[0].fileName, self.parent.fileview.activeSquares[0].fileSize, self.parent.fileview.activeSquares[0].fileType, self.parent.fileview.activeSquares[0].isFolder, self.parent.fileview.activeSquares[0].lastModified, True)
			#self.infoLayout.addWidget(self.item, 10, 0, 1, 0, QtCore.Qt.AlignHCenter)
			self.numberSelected.setText("1 item selected.")
			#self.sizeSelectedTitle.setText("Size: ")
			
			#only details for only single files
			#filetype = self.parent.fileview.activeSquares[0].fileType
			
			## not sure why this is here... ##
			'''
			if not (len(filetype) <= 24):
				cut = len(filetype) - 24
				filetype = filetype.replace(filetype[-cut:], '...')
				
			'''
			
			#self.fileNameText.setText(self.parent.fileview.activeSquares[0].fileName)
			self.topText.setText(self.parent.fileview.activeSquares[0].fileName)
			#self.fileTypeText.setText(filetype)
			self.lastModifiedText.setText(self.item.lastModified.replace("T", " "))
			self.showSingle()
			
	def hideSingle(self):
		#self.fileNameTitle.hide()
		#self.fileNameText.hide()
		#self.fileTypeTitle.hide()
		self.fileTypeText.hide()
		#self.lastModifiedTitle.hide()
		self.lastModifiedText.hide()
		self.numberSelected.show()
		self.generateLinkButton.hide()
		self.moveButton.hide()
	
	def showSingle(self):
		#self.fileNameTitle.show()
		#self.fileNameText.show()
		#self.fileTypeTitle.show()
		self.fileTypeText.show()
		#self.lastModifiedTitle.show()
		self.lastModifiedText.show()
		self.numberSelected.hide()
		self.generateLinkButton.show()
		self.moveButton.show()
			
	
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
		#update selection count
		self.updateView()
		
		#update the size total
		#self.updateSizes()
		
		#show the widget
		self.show()
		
	def deactivate(self):
		if not(self.item == None):
			self.infoLayout.removeWidget(self.item)
			#self.sizeSelected.setText("")
			self.numberSelected.setText("")
			self.item.close()
		self.hide()

	def buttonClicked(self, buttonType):
		button = buttonType.lower()
		if (button == "add"):
			print "Add pressed."
			##Open Dialog
			source_file = QtGui.QFileDialog.getOpenFileName(self, 'Open file', os.path.expanduser("~"))
			## Print File Name
			#print str(source_file)
			destination_folder = self.parent.parent.config.get('LocalSettings', 'sync-dir') + self.parent.breadcrumb.currentPath
			print "Source: " + source_file
			print "Dest: " + destination_folder
			#if not os.path.exists(destination_folder):
				#os.makedirs(destination_folder)
			
			#Call Move File Function.
			self.moveFile(str(source_file),str(destination_folder))
			
			#deleteFileName = self.parent.fileview.squareArray[0].filePath
			#print deleteFileName
			#print self.parent.fileview.squareArray[0].filePath[:deleteFileName + 1]
			#self.parent.changePath(self.parent.fileview.squareArray[0].filePath[:deleteFileName + 1])
			
			#### NEED TO ADD REFRESH FILEVIEW #########
			self.parent.parent.tray.notification("Kissync", "New File(s) Added!")
			
			#Refresh FILEVIEW
			Filenm = self.parent.fileview.activeSquares[0].filePath.rfind('/')
			#Prints out the directory...
			#print self.parent.fileview.activeSquares[0].filePath[:deleteFileName + 1] 
			self.parent.changePath(self.parent.fileview.activeSquares[0].filePath[:Filenm + 1])
			
		elif (button == "delete"):
			print "Delete pressed."
			#Create the file path to delete.
			try:
				deleteMeFilePath = self.parent.parent.config.get('LocalSettings', 'sync-dir') + self.parent.fileview.activeSquares[0].filePath
				##Delete the file from the system.
				os.remove(deleteMeFilePath)
				
				##Instead of deleting a specific square.. just re-update the fileview.
				deleteFileName = self.parent.fileview.activeSquares[0].filePath.rfind('/')
				#Prints out the directory...
				#print self.parent.fileview.activeSquares[0].filePath[:deleteFileName + 1] 
				self.parent.changePath(self.parent.fileview.activeSquares[0].filePath[:deleteFileName + 1])
				
				self.parent.parent.tray.notification("Kissync", "Deleted")
			except:
				#print "File does not exist on computer... Deleting from Cloud!"
				try:
					self.parent.parent.smartfile.post('/path/oper/remove/', path=self.filePath)
				except:
					pass
				self.parent.parent.tray.notification("Kissync", "In Deletion Queue...")
		
		elif (button == "move"):
			#Move File...
			print self.parent.fileview.activeSquares[0].filePath
			print self.parent.fileview.activeSquares[0].downloadFile(self.parent.fileview.activeSquares[0].filePath)
			try:
				self.parent.fileview.activeSquares[0].downloadFile(self.parent.fileview.activeSquares[0].filePath)
			except:
				pass
			
			source_file = self.parent.parent.config.get('LocalSettings', 'sync-dir') + self.parent.fileview.activeSquares[0].filePath
			
			'''
			#Get file extension and type
			extension = None
			if (source_file.rfind('.') != -1):
				dotIndex = source_file.rfind('.')
				#print dotIndex
				fileNameLength = len(source_file)
				#print fileNameLength
				extension = source_file[dotIndex:fileNameLength]
			else:
				extension = None
			'''
			
			'''
			inputter = InputDialog(self, title="Move:", label="Folder:", text="/")
			inputter.exec_()
			comment = inputter.text.text()
			'''
			
			comment = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory", self.parent.parent.config.get('LocalSettings', 'sync-dir')))
			
			destination_folder = comment
			print str(source_file)
			print str(destination_folder)
			
			self.moveFile(str(source_file),str(destination_folder))
			
			Filenm = self.parent.fileview.squareArray[0].filePath.rfind('/')
			#Prints out the directory...
			#print self.parent.fileview.activeSquares[0].filePath[:deleteFileName + 1] 
			self.parent.changePath(self.parent.fileview.squareArray[0].filePath[:Filenm + 1])
			
			self.parent.parent.tray.notification("Kissync", "Moved")
		elif (button == "rename"):
			
			source_file = os.path.expanduser("~") + "/Kissync" + self.parent.fileview.activeSquares[0].filePath
			
			#Get file extension and type
			extension = None
			if (source_file.rfind('.') != -1):
				dotIndex = source_file.rfind('.')
				#print dotIndex
				fileNameLength = len(source_file)
				#print fileNameLength
				extension = source_file[dotIndex:fileNameLength]
			else:
				extension = None
			
			indFolder = self.parent.fileview.activeSquares[0].filePath.rfind('/')
			folder = "/Kissync" + self.parent.fileview.activeSquares[0].filePath[:indFolder + 1]
			
			inputter = InputDialog(self, title="Rename:", label="Folder:", text=extension)

			inputter.exec_()
			
			print source_file
			dest_file = os.path.dirname(os.path.realpath(__file__)) + folder + inputter.text.text()
			print dest_file
			self.moveFile(str(source_file),str(dest_file))
			self.parent.parent.tray.notification("Kissync", "Renamed")
			
			#Refreshes FileVIEW
			Filenm = self.parent.fileview.activeSquares[0].filePath.rfind('/')
			#Prints out the directory...
			#print self.parent.fileview.activeSquares[0].filePath[:deleteFileName + 1] 
			self.parent.changePath(self.parent.fileview.activeSquares[0].filePath[:Filenm + 1])
			
		elif (button == "generate_link"):
			print "Gen Link Pressed"
			print self.parent.fileview.activeSquares[0].filePath
			path = self.parent.fileview.activeSquares[0].filePath
			name = self.parent.fileview.activeSquares[0].fileName
			url = ""
			
			#Create a temp url in the background!
			
			#Make API call for url.
			tree = self.parent.parent.smartfile.get('/link', path=path)
			#pprint.pprint(tree['href'])
			for i in tree:
				if 'href' not in i:
					return []
				url = i['href'].encode("utf-8")
			print path
			print "-----------"
			print name
			if not (url == "" or url == None):
				pass
			else:
				print "Nothing!  Yet! GENERATE A URL!"
				p = path
				n = name
				tree2 = self.parent.parent.smartfile.post('/link', path=(p), name=(n), read=True, list=True, recursive=True)
				#pprint.pprint(tree['href'])
				for i in tree2:
					if(i == "href"):
						url = tree2[i]

			print "RESPONSE:"
			print url
			pyperclip.copy(url)
			#Share on twitter.
			#text = "Kissync"
			#webbrowser.open("http://twitter.com/share?url=" + str(url) + "&text=" + str(text))
			self.parent.parent.tray.notification("Kissync", "Link copied to clipboard.")
		elif(button == "user_premissions"):
			print "User Premissions!"
			self.manageUser.show()
			self.manageUser.path = self.parent.fileview.activeSquares[0].filePath
			
		else:
			print "Op. that button isn't alive yet!"
	def moveFile(self, source, dest):
		if not (source == "" or dest == None):
			shutil.move(source,dest)
		else:
			print "User canceled upload dialog"
		
class InputDialog(QtGui.QDialog):
	'''
	this is for when you need to get some user input text
	'''
	def __init__(self, parent=None, title='user input', label='comment', text=''):

		QtGui.QWidget.__init__(self, parent)

		#--Layout Stuff---------------------------#
		mainLayout = QtGui.QVBoxLayout()

		layout = QtGui.QHBoxLayout()
		self.label = QtGui.QLabel()
		self.label.setText(label)
		layout.addWidget(self.label)

		self.text = QtGui.QLineEdit(text)
		layout.addWidget(self.text)

		mainLayout.addLayout(layout)

		#--The Button------------------------------#
		layout = QtGui.QHBoxLayout()
		button = QtGui.QPushButton("okay") #string or icon
		self.connect(button, QtCore.SIGNAL("clicked()"), self.close)
		layout.addWidget(button)

		mainLayout.addLayout(layout)
		self.setLayout(mainLayout)

		self.resize(400, 60)
		self.setWindowTitle(title)
class Main(QtGui.QWidget):
	def __init__(self, parent = None):
		super(Main, self).__init__(parent)
		self.setWindowTitle('Side Panel')  
		
		self.grid = QtGui.QGridLayout()
		
		self.bottompanel = BottomPanel(self)
		self.grid.addWidget(self.bottompanel)
		self.setLayout(self.grid)
		self.bottompanel.show()


		
if __name__ == "__main__":
	
	#print os.path.realpath(__file__)
	app = QtGui.QApplication(sys.argv)
	mainwindow = Main()
	mainwindow.show()
	sys.exit(app.exec_())
