from PySide import QtCore, QtGui, QtWebKit

import app.core.common as common
from app.core.configuration import Config


class AuthBrowser(QtWebKit.QWebView):
    def __init__(self, parent):
        self.parent = parent
        QtWebKit.QWebView.__init__(self)

        # create an instance of the configuration
        self.__config = Config(common.settings_file_path())

        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.setMinimumWidth(500)

        self.urlChanged.connect(self.checkUrl)
        self.loadStarted.connect(self._starttimer)

        page = self.page()
        # Warning: This could be dangerous
        page.networkAccessManager().sslErrors.connect(self.sslErrorHandler)

        self.timer = QtCore.QTimeLine()

    def checkUrl(self, ok):
        api = self.parent.parent.api

        currentUrl = str(self.url().toString())
        url = 'http://www.kissync.com/oauth?verifier='

        # if on kissync.com, pass verifier to smartfile client
        if currentUrl.startswith(url):
            try:
                verifier = currentUrl.replace(url, "")
                token, verifier = api.get_access_token(None, verifier)
                self.__config.set('login-token', token)
                self.__config.set('login-verifier', verifier)
            except:
                # error getting the verifier from smartfile
                self.parent.parent.authenticator.networkError()
            else:
                #logged in successfully
                self.parent.hide()
                if self.__config.get('first-run'):
                    self.parent.parent.authenticator.setup.emit('done')
                else:
                    self.parent.parent.authenticator.done.emit('done')

        self.timer.stop()

    def _starttimer(self):
        self.pagetimer()

    def pagetimer(self):
        # throws an error after amount of time defined in config
        self.timer.valueChanged.connect(self.netwatch)
        timeout = int(self.__config.get('network-timeout') * 1000)
        self.timer.setDuration(timeout)
        self.timer.start()

    def netwatch(self, value):
        if value >= 1.0:
            self.stop()
            self.parent.networkError()

    def sslErrorHandler(self, reply, errors):
        reply.ignoreSslErrors()
