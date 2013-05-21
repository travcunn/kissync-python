from PyQt4 import QtCore, QtGui, QtWebKit


class AuthBrowser(QtWebKit.QWebView):
    def __init__(self, parent):
        self.parent = parent
        QtWebKit.QWebView.__init__(self)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.urlChanged.connect(self.checkUrl)
        self.loadStarted.connect(self._starttimer)

        self.timer = QtCore.QTimeLine()
        self.setMinimumWidth(500)

    def checkUrl(self, ok):
        currentUrl = str(self.url().toString())

        #if on kissync.com, pass verifier to smartfile client
        if(currentUrl.startswith("http://www.kissync.com/oauth?verifier=")):
            try:
                verifier = currentUrl.replace("http://www.kissync.com/oauth?verifier=", "")
                token, verifier = self.parent.parent.smartfile.get_access_token(None, verifier)
                self.parent.parent.configuration.set("Login", "token", token)
                self.parent.parent.configuration.set("Login", "verifier", verifier)
            except:
                raise
                #something happened after logging in successfully, but something happened with passing the verifier
                self.parent.badLoginError()
            else:
                #logged in successfully
                self.parent.hide()
                self.parent.parent.authenticator.success()

        self.timer.stop()

    def _starttimer(self):
        self.pagetimer()

    def pagetimer(self):
        #starts up a page timer, so after 30 seconds, we can give a network error
        self.timer.valueChanged.connect(self.netwatch)
        self.timer.setDuration(int(self.parent.parent.configuration.get('LocalSettings', 'network-timeout')) * 1000)
        self.timer.start()

    def netwatch(self, value):
        if (value == 1.0):
            self.stop()
            self.parent.networkError()
