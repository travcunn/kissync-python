from PySide import QtCore, QtGui, QtWebKit


class AuthBrowser(QtWebKit.QWebView):
    def __init__(self, parent):
        self.parent = parent
        QtWebKit.QWebView.__init__(self)

        self.configuration = self.parent.parent.configuration

        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.urlChanged.connect(self.checkUrl)
        self.loadStarted.connect(self._starttimer)

        page = self.page()
        # Warning: This could be dangerous
        page.networkAccessManager().sslErrors.connect(self.sslErrorHandler)

        self.timer = QtCore.QTimeLine()
        self.setMinimumWidth(500)

    def checkUrl(self, ok):
        currentUrl = str(self.url().toString())

        #if on kissync.com, pass verifier to smartfile client
        if currentUrl.startswith("http://www.kissync.com/oauth?verifier="):
            try:
                verifier = currentUrl.replace("http://www.kissync.com/oauth?verifier=", "")
                token, verifier = self.parent.parent.smartfile.get_access_token(None, verifier)
                self.configuration.set("Login", "token", token)
                self.configuration.set("Login", "verifier", verifier)
            except:
                #logged in successfully, but something happened with passing the verifier
                self.parent.parent.authenticator.networkError()
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
        self.timer.setDuration(int(self.configuration.get('LocalSettings', 'network-timeout')) * 1000)
        self.timer.start()

    def netwatch(self, value):
        if value >= 1.0:
            self.stop()
            self.parent.networkError()

    def sslErrorHandler(self, reply, errors):
        reply.ignoreSslErrors()
