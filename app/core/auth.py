from PySide import QtCore
from smartfileclient import OAuthClient


class Authenticator(QtCore.QThread):
    login = QtCore.Signal(object)
    done = QtCore.Signal(object)
    setup = QtCore.Signal(object)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent

    def run(self):
        token = "RcBMbit9N6Yty6VYFhSWAHCUG00PVZ"
        secret = "9nbVTipa5RazUg2TGKxi9jMKbxnq6k"

        configToken = self.parent.configuration.get("Login", "token")
        configVerifier = self.parent.configuration.get("Login", "verifier")

        if configToken and configVerifier is not None:
            try:
                self.parent.smartfile = OAuthClient(token, secret,
                                                    configToken, configVerifier)
                self.parent.smartfile.get('/whoami')
            except:
                self.showLoginWindow()
            else:
                self.success()
        else:
            try:
                self.parent.smartfile = OAuthClient(token, secret)
            except:
                raise
                self.networkError()
            else:
                self.showLoginWindow()

    def showLoginWindow(self):
        """
        Sends a signal to the Main class to open the login window with the login url
        """
        self.parent.smartfile.get_request_token("https://www.kissync.com/oauth")

        authUrl = self.parent.smartfile.get_authorization_url()
        self.login.emit(QtCore.QUrl(authUrl))

    def networkError(self):
        #TODO: make this work
        self.parent.loginwindow.networkError()

    def success(self):
        """
        When the login is successful, send a signal to the setup window or the main class
        """
        if (self.parent.configuration.get('LocalSettings', 'first-run')) is True:
            self.setup.emit('done')
        else:
            self.done.emit('done')
