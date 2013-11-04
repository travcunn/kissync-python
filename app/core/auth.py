import logging

from PySide import QtCore
from smartfile.errors import RequestError, ResponseError

import common
from errors import AuthException, NetConnectionException
from configuration import Configuration
from smartfileclient import OAuthClient


log = logging.getLogger(__name__)


class ApiConnection(object):
    """ A simple SmartFile auth object with callbacks """
    def __init__(self, token=None, secret=None, success_callback=None,
                 neterror_callback=None, login_callback=None, **kwargs):
        self.success_callback = success_callback
        self.neterror_callback = neterror_callback
        self.login_callback = login_callback

        if token or secret is None:
            self._token = "RcBMbit9N6Yty6VYFhSWAHCUG00PVZ"
            self._secret = "9nbVTipa5RazUg2TGKxi9jMKbxnq6k"

        # create an instance of the configuration
        self.__configuration = Configuration(common.settingsFile())

        # get the token and verifier from the configuration
        self._configToken = self.__configuration.get("Login", "token")
        self._configVerifier = self.__configuration.get("Login", "verifier")

        self._isAuthenticated = False

        self.doLogin()

    def doLogin(self):
        try:
            if self._configToken and self._configVerifier is not None:
                log.debug('Attempting to login using all credentials.')
                # try connecting to smartfile using existing credentials
                self._api = OAuthClient(self._token,
                                        self._secret,
                                        self._configToken,
                                        self._configVerifier)
                self._api.get('/whoami')
            else:
                log.debug('Attempting to login using only the token and secret.')
                self._api = OAuthClient(self._token, self._secret)
        except RequestError as e:
            self._isAuthenticated = False
            if e.detail.startswith("HTTPSConnectionPool"):
                log.warning('HTTPS connection error during login.')
                if self.neterror_callback is not None:
                    return self.neterror_callback()
                else:
                    # raise an exception if there is no network connectivity
                    raise NetConnectionException(e)
            else:
                log.warning('Uncaught exception raised with RequestError.')
                # raise an exception if there is no connection issue
                raise
        except ResponseError as e:
            if e.status_code == 403:
                log.warning('Bad login credentials.')
                if self.login_callback is not None:
                    return self.login_callback(self._api)
                else:
                    # raise an exception if auth is bad
                    raise AuthException('Invalid Login: The credentials were invalid.')
            else:
                log.warning('ResponseError was raised with HTTP status: ' + e.status_code)
                # raise an exception if there is an error other than 403
                raise
        else:
            if self._configToken and self._configVerifier is not None:
                log.info('Client successfully authenticated.')
                self._isAuthenticated = True
                if self.success_callback is not None:
                    return self.success_callback(self._api)
            else:
                log.info('Credentials not found. Prompting for a login.')
                if self.login_callback is not None:
                    self.login_callback(self._api)
                else:
                    # raise an exception if there is no auth yet
                    raise AuthException('Login required: Credentials are required to login.')

    def __getattr__(self, name):
        if self._isAuthenticated:
            return self._api
        else:
            if self.doLogin():
                return self._api


class Authenticator(QtCore.QThread):
    login = QtCore.Signal(object)
    done = QtCore.Signal(object)
    setup = QtCore.Signal(object)
    neterror = QtCore.Signal(object)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent

        # create an instance of the configuration
        self.__configuration = Configuration(common.settingsFile())

    def run(self):
        self.api = ApiConnection(success_callback=self.success,
                                 neterror_callback=self.networkError,
                                 login_callback=self.showLoginWindow)

    def showLoginWindow(self, api):
        """
        Sends a signal to the Main class to open the login window
        """
        try:
            self.parent.api = api
            api.get_request_token("http://www.kissync.com/oauth")

            authUrl = api.get_authorization_url()
            self.login.emit(QtCore.QUrl(authUrl))
        except:
            self.networkError()

    def networkError(self):
        self.neterror.emit('error')

    def success(self, api):
        """
        When the login is successful, send signal to the appropriate ui
        """
        self.parent.api = api
        if (self.__configuration.get('LocalSettings', 'first-run')) is True:
            self.setup.emit('done')
        else:
            self.done.emit('done')
