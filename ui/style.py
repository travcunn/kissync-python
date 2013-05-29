from PySide import QtGui


class KissyncStyle(object):
    def __init__(self):
        object.__init__(self)
        self.BLACK = "#000000"
        self.WHITE = "#FFFFFF"
        self.BLUE = "#1BA1E2"
        self.BROWN = "#A05000"
        self.GREEN = "#339933"
        self.LIME = "#8CBF26"
        self.MAGENTA = "#FF0097"
        self.ORANGE = "#F09609"
        self.PINK = "#E671B8"
        self.PURPLE = "#A200FF"
        self.RED = "#E51400"
        self.TEAL = "#00ABA9"

        self.SQUAREOPACITY = .66

    def hexToQColor(self, value):
        value = value.strip('#')
        return QtGui.QColor(int(value[:2], 16), int(value[2:4], 16), int(value[4:], 16), 255)
