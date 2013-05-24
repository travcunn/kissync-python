from PyQt4 import QtCore
from smartfileclient import OAuthClient


class Authenticator(object):
    def __init__(self, parent=None):
        super(Authenticator, self).__init__()
        self.parent = parent
        self.go()

    def go(self):
        configToken = self.parent.configuration.get("Login", "token")
        configVerifier = self.parent.configuration.get("Login", "verifier")
        if(configToken) and (configVerifier) is not None:
            try:
                self.parent.smartfile = OAuthClient("puchob9x94AiYWFkIPhd6eoxlvrzCK", "X4M7CNooRuhAwUd5LFookOMV0ZSqYq", configToken, configVerifier)
                self.parent.smartfile.get('/whoami')
            except:
                raise
                self.showLoginWindow()
            else:
                self.success()
        else:
            try:
                self.parent.smartfile = OAuthClient("puchob9x94AiYWFkIPhd6eoxlvrzCK", "X4M7CNooRuhAwUd5LFookOMV0ZSqYq")
            except:
                self.networkError()
            else:
                self.showLoginWindow()

    def showLoginWindow(self):
        self.parent.smartfile.get_request_token("http://www.kissync.com/oauth")

        authUrl = self.parent.smartfile.get_authorization_url()
        self.parent.loginwindow.htmlView.load(QtCore.QUrl(authUrl))
        self.parent.loginwindow.show()

    def networkError(self):
        self.parent.loginwindow.networkError()

    def success(self):
        #Successfully logged in
        if(self.parent.configuration.get('LocalSettings', 'first-run')) is True:
            self.parent.setupwizard.show()
            self.parent.tray.notification("Kissync Setup", "Please complete the setup to start using Kissync")
        else:
            self.parent.start()
            #self.parent.filewatcher.start()
