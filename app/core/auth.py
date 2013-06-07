from PySide import QtCore
from smartfileclient import OAuthClient
#from smartfile.sync import SyncClient


class Authenticator(QtCore.QThread):
    login = QtCore.Signal(object)
    done = QtCore.Signal(object)
    setup = QtCore.Signal(object)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent

    def run(self):
        configToken = self.parent.configuration.get("Login", "token")
        configVerifier = self.parent.configuration.get("Login", "verifier")
        if configToken and configVerifier is not None:
            try:
                self.parent.smartfile = OAuthClient("puchob9x94AiYWFkIPhd6eoxlvrzCK", "X4M7CNooRuhAwUd5LFookOMV0ZSqYq",
                                                    configToken, configVerifier)
                self.parent.smartfile.get('/whoami')
                #self.parent.sync = SyncClient(self.parent.smartfile)
            except:
                raise
                self.showLoginWindow()
            else:
                self.success()
        else:
            try:
                self.parent.smartfile = OAuthClient("puchob9x94AiYWFkIPhd6eoxlvrzCK", "X4M7CNooRuhAwUd5LFookOMV0ZSqYq")
                #self.parent.sync = SyncClient(self.parent.smartfile)
            except:
                self.networkError()
            else:
                self.showLoginWindow()

    def showLoginWindow(self):
        """Sends a signal to the Main class to open the login window with the login url"""
        self.parent.smartfile.get_request_token("http://www.kissync.com/oauth")

        authUrl = self.parent.smartfile.get_authorization_url()
        self.login.emit(QtCore.QUrl(authUrl))

    def networkError(self):
        #TODO: make this work
        self.parent.loginwindow.networkError()

    def success(self):
        """When the login is successful, send a signal to the setup window or the main class"""
        if (self.parent.configuration.get('LocalSettings', 'first-run')) is True:
            self.setup.emit('done')
        else:
            self.done.emit('done')
            #self.parent.filewatcher.start()
