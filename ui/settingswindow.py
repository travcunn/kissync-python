from PySide import QtGui, QtCore

from ui.accountwidget import AccountWidget
from ui.style import KissyncStyle


class SettingsWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__()
        self.parent = parent
        self.style = KissyncStyle()

        self.setWindowTitle('Kissync Folder Sync Settings')
        self.setWindowIcon(QtGui.QIcon("icons/menuicon.png"))
        self.setFixedSize(520, 200)
        self.setContentsMargins(0, 0, 0, 0)
        #blue color: 699afb

        self.settingsWidget = SettingsPanel(self)

        titleBar = TitleBar()
        maingrid = QtGui.QGridLayout()
        maingrid.setContentsMargins(0, 0, 0, 0)
        maingrid.addWidget(titleBar, 0, 0)
        maingrid.addWidget(self.settingsWidget, 1, 0, 2, 2)

        self.setLayout(maingrid)
        self.centerOnScreen()

    def saveSettings(self):
        if(self.settingsWidget.checkboxNotifications.isChecked()):
            self.parent.configuration.set('LocalSettings', 'notifications', True)
        else:
            self.parent.configuration.set('LocalSettings', 'notifications', False)

        self.hide()
        self.parent.configuration.save()

    def showSettings(self):
        self.centerOnScreen()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive | QtCore.Qt.FramelessWindowHint)
        self.activateWindow()
        self.show()
        self.raise_()

    def centerOnScreen(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2), (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.draw(painter)
        painter.end()

    def draw(self, painter):
        penblank = QtGui.QPen(QtCore.Qt.black, -1, QtCore.Qt.SolidLine)
        painter.setPen(penblank)
        painter.setBrush(QtGui.QColor('#3c3c3c'))
        painter.drawRect(0, 0, self.frameSize().width(), self.frameSize().height())


class TitleBar(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TitleBar, self).__init__()
        self.parent = parent
        self.setMinimumSize(520, 60)
        self.setMaximumSize(520, 60)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("color: #FFFFFF;")
        self.setStyleSheet("QWidget { border: 0px; }")

        settingsLabel = QtGui.QLabel('settings')
        font = QtGui.QFont("Vegur", 28, QtGui.QFont.Light, False)
        settingsLabel.setFont(font)
        settingsLabel.setObjectName("settingsLabel")
        settingsLabel.setStyleSheet("color: #FFFFFF;")

        titleBarGrid = QtGui.QGridLayout()
        titleBarGrid.addWidget(settingsLabel)
        self.setAutoFillBackground(True)
        self.setLayout(titleBarGrid)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.draw(painter)
        painter.end()

    def draw(self, painter):
        penblank = QtGui.QPen(QtCore.Qt.black, -1, QtCore.Qt.SolidLine)
        painter.setPen(penblank)
        painter.setBrush(QtGui.QColor('#1763A6'))
        painter.drawRect(0, 0, self.frameSize().width(), self.frameSize().height())


class SettingsPanel(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SettingsPanel, self).__init__()
        self.parent = parent

        self.setContentsMargins(0, 0, 0, 0)

        grid = QtGui.QGridLayout()
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.checkboxNotifications = QtGui.QCheckBox('Allow Desktop Notifications', self)
        self.checkboxNotifications.setStyleSheet("color: #FFFFFF;")
        font = QtGui.QFont("Vegur", 16, QtGui.QFont.Light, False)
        self.checkboxNotifications.setFont(font)
        if self.parent.parent.configuration.get('LocalSettings', 'notifications'):
            if not self.checkboxNotifications.isChecked():
                self.checkboxNotifications.toggle()

        saveButton = SaveButton(self, 'Save')

        self.accountWidget = AccountWidget(self.parent)
        #add the objects to the grid
        grid.addWidget(self.checkboxNotifications, 1, 1, 2, 2)
        grid.addWidget(self.accountWidget, 1, 2, 1, 2)
        grid.addWidget(saveButton, 3, 3)

        self.setLayout(grid)


class SaveButton(QtGui.QWidget):
    def __init__(self, parent, text=None):
        QtGui.QWidget.__init__(self)
        self.parent = parent

        self.squareWidth = 80
        self.squareHeight = 30

        self.setMaxSize()

        #fontDatabase = QtGui.QFontDatabase()
        #fontfile = QtCore.QFile("resources/Roboto-Light-webfont.ttf")
        #fontDatabase.addApplicationFont(os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf")
        #os.path.dirname(os.path.dirname(os.path.realpath(__file__)) + "/resources/Roboto-Light-webfont.ttf")

        self.text = text
        self.font = QtGui.QFont("Vegur", 14, QtGui.QFont.Bold, False)

        self.color = '#8DBF41'
        self.initUI()

    def setMaxSize(self):
        self.setMaximumSize(self.squareWidth, self.squareHeight)
        self.setMinimumSize(self.squareWidth, self.squareHeight)

    def initUI(self):
        self.repaint()

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.drawBackground(painter)
        self.drawText(e, painter)
        painter.end()

    def drawBackground(self, painter):
        penblank = QtGui.QPen(QtCore.Qt.black, -1, QtCore.Qt.SolidLine)
        painter.setPen(penblank)
        painter.setBrush(QtGui.QColor(self.color))
        painter.drawRect(0, 0, self.squareWidth, self.squareHeight)

    def drawText(self, event, painter):
        painter.setPen(QtGui.QColor(255, 255, 255))
        painter.setFont(self.font)
        painter.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)

    def mousePressEvent(self, event):
        self.parent.parent.saveSettings()

    def enterEvent(self, event):
        self.repaint()

    def leaveEvent(self, event):
        self.repaint()
