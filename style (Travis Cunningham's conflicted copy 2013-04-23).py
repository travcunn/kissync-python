from PyQt4 import QtGui

class KissyncStyle(object):
	BLACK = "#000000"
	WHITE = "#FFFFFF"
	BLUE = "#1BA1E2"
	BROWN = "#A05000"
	GREEN = "#339933"
	LIME = "#8CBF26"
	MAGENTA = "#FF0097"
	ORANGE = "#F09609"
	PINK = "#E671B8"
	PURPLE = "#A200FF"
	RED = "#E51400"
	TEAL = "#00ABA9"
	
	SQUAREOPACITY = .66
	
	def hexToQColor(self, value):
		value = value.strip('#')
		return QtGui.QColor(int(value[:2], 16), int(value[2:4], 16), int(value[4:], 16), 255)
