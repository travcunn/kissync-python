from PySide import QtGui, QtCore
from ui.accountwidget import AccountWidget

import ui.resources


class SettingsWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__()
        self.parent = parent
        self.tray = self.parent.tray
        self.settingsFile = self.parent.settingsFile

        self.setWindowTitle('SmartFile Settings')
        self.setWindowIcon(QtGui.QIcon(":/menuicon.png"))
        self.setFixedSize(375, 300)
        self.setContentsMargins(0, 0, 0, 0)

        self.settingsWidget = SettingsPanel(self)

        titleBar = TitleBar()
        maingrid = QtGui.QGridLayout()
        maingrid.setContentsMargins(0, 0, 0, 0)
        maingrid.addWidget(titleBar, 0, 0)
        maingrid.addWidget(self.settingsWidget, 1, 0, 2, 2)

        self.setLayout(maingrid)
        self.centerOnScreen()

    def saveSettings(self):
        # Save general tab
        """
        if self.settingsWidget.checkboxNotifications.isChecked():
            self.parent.configuration.set('LocalSettings', 'notifications', True)
        else:
            self.parent.configuration.set('LocalSettings', 'notifications', False)
        """

        # Save networking tab
        """
        if self.settingsWidget.radioProxyEnabled.isChecked():
            httpText = self.settingsWidget.httpAddress.text()
            httpsText = self.settingsWidget.httpsAddress.text()
            if httpText is not '' and httpsText is not '':
                self.parent.configuration.set('Network', 'http-proxy-address', str(httpText))
                self.parent.configuration.set('Network', 'https-proxy-address', str(httpsText))
                self.parent.configuration.set('Network', 'proxy-enabled', "yes")
        else:
            self.parent.configuration.set('Network', 'proxy-enabled', "no")
        """

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


class TitleBar(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TitleBar, self).__init__()
        self.parent = parent
        self.setMinimumSize(475, 60)
        self.setMaximumSize(475, 60)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("color: #FFFFFF;")
        self.setStyleSheet("QWidget { border: 0px; }")

        settingsLabel = QtGui.QLabel('SmartFile Sync Settings')
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

        tabWidget = QtGui.QTabWidget()
        generalTab = QtGui.QWidget()
        accountTab = QtGui.QWidget()
        networkTab = QtGui.QWidget()
        aboutTab = QtGui.QWidget()

        generalTabLayout = QtGui.QGridLayout(generalTab)
        accountTabLayout = QtGui.QGridLayout(accountTab)
        networkTabLayout = QtGui.QGridLayout(networkTab)
        aboutTabLayout = QtGui.QGridLayout(aboutTab)

        #tabWidget.addTab(generalTab, "General")
        tabWidget.addTab(accountTab, "Account")
        #tabWidget.addTab(networkTab, "Network")
        tabWidget.addTab(aboutTab, "About")

        """ Start General Tab """

        generalTabLayout.setAlignment(QtCore.Qt.AlignTop)
        generalTab.setContentsMargins(10, 10, 0, 10)

        self.checkboxNotifications = QtGui.QCheckBox('Allow Desktop Notifications', self)
        if self.parent.parent.configuration.get('LocalSettings', 'notifications'):
            if not self.checkboxNotifications.isChecked():
                self.checkboxNotifications.toggle()

        generalTabLayout.addWidget(self.checkboxNotifications, 1, 0, 1, 1)

        """ End General Tab """
        """ Start Account Tab """

        accountTabLayout.setAlignment(QtCore.Qt.AlignTop)
        accountTab.setContentsMargins(10, 0, 0, 10)
        self.accountWidget = AccountWidget(self.parent)

        accountTabLayout.addWidget(self.accountWidget)

        """ End Account Tab """
        """ Start Network Tab """
        formLayout = QtGui.QFormLayout()

        networkTabLayout.setAlignment(QtCore.Qt.AlignTop)
        networkTab.setContentsMargins(10, 10, 0, 10)

        radioGroup = QtGui.QButtonGroup(networkTab)
        self.radioProxyDisabled = QtGui.QRadioButton("Disabled")
        radioGroup.addButton(self.radioProxyDisabled)
        self.radioProxyEnabled = QtGui.QRadioButton("Enabled")
        radioGroup.addButton(self.radioProxyEnabled)

        self.connect(self.radioProxyDisabled, QtCore.SIGNAL("clicked()"), self.disableProxyInput)
        self.connect(self.radioProxyEnabled, QtCore.SIGNAL("clicked()"), self.enableProxyInput)

        formLayout.addRow("Proxy:", self.radioProxyDisabled)
        formLayout.addRow("", self.radioProxyEnabled)

        self.proxyWidget = QtGui.QWidget()
        self.proxyWidget.setContentsMargins(0, 0, 0, 0)
        proxyLayout = QtGui.QFormLayout()
        self.proxyWidget.setContentsMargins(0, 0, 0, 0)
        proxyLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.proxyWidget.setLayout(proxyLayout)

        self.httpAddress = QtGui.QLineEdit(self)
        self.httpAddress.setMaximumWidth(200)

        proxyLayout.addRow("HTTP Proxy:", self.httpAddress)

        self.httpsAddress = QtGui.QLineEdit(self)
        self.httpsAddress.setMaximumWidth(200)

        proxyLayout.addRow("HTTPS Proxy:", self.httpsAddress)

        networkTabLayout.addLayout(formLayout, 0, 0)
        networkTabLayout.addWidget(self.proxyWidget, 1, 0)

        """ End Network Tab """

        """ Start About Tab """

        aboutTabLayout.setAlignment(QtCore.Qt.AlignCenter)
        aboutTab.setContentsMargins(10, 10, 0, 10)

        versionText = QtGui.QLabel()
        versionText.setText("SmartFile desktop sync version: %s" % (self.parent.parent.version))

        aboutTabLayout.addWidget(versionText)

        """ End About Tab """

        if self.parent.parent.configuration.get('Network', 'proxy-enabled') == "yes":
            self.radioProxyEnabled.setChecked(True)
            self.enableProxyInput()
        else:
            self.radioProxyDisabled.setChecked(True)
            self.disableProxyInput()

        httptext = self.parent.parent.configuration.get('Network', 'http-proxy-address')
        if httptext is not None:
            self.httpAddress.setText(httptext)
        httpstext = self.parent.parent.configuration.get('Network', 'https-proxy-address')
        if httpstext is not None:
            self.httpsAddress.setText(httpstext)

        saveButton = QtGui.QPushButton("Save", self)
        saveButton.clicked.connect(self.parent.saveSettings)

        grid.addWidget(tabWidget, 1, 1, 1, 3)
        grid.addWidget(saveButton, 3, 3, 1, 1)

        self.setLayout(grid)

    def disableProxyInput(self):
        self.proxyWidget.hide()

    def enableProxyInput(self):
        self.proxyWidget.show()
