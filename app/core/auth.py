import logging

from smartfile.errors import RequestError, ResponseError

import common
from app.core.errors import AuthError, NetConnectionError
from app.core.configuration import Config
from app.core.smartfileclient import OAuthClient


log = logging.getLogger(__name__)


class ApiConnection(object):
    """ A simple SmartFile auth object with callbacks """
    def __init__(self, token=None, secret=None, success_callback=None,
                 neterror_callback=None, login_callback=None):
        self.success_callback = success_callback
        self.neterror_callback = neterror_callback
        self.login_callback = login_callback

        if token or secret is None:
            self._token = "RcBMbit9N6Yty6VYFhSWAHCUG00PVZ"
            self._secret = "9nbVTipa5RazUg2TGKxi9jMKbxnq6k"

        # create an instance of the configuration
        self.__configuration = Config(common.settings_file_path())

        # get the token and verifier from the configuration
        self._config_token = self.__configuration.get('login-token')
        self._config_verifier = self.__configuration.get('login-verifier')

        self._authenticated = False

        self.do_login()

    def do_login(self):
        try:
            if self._config_token and self._config_verifier is not None:
                log.debug('Attempting to login using all credentials.')
                # try connecting to smartfile using existing credentials
                self._api = OAuthClient(self._token,
                                        self._secret,
                                        self._config_token,
                                        self._config_verifier)
                self._api.get('/whoami')
            else:
                log.debug('Attempting to login using only the token and secret.')
                self._api = OAuthClient(self._token, self._secret)
        except RequestError as e:
            self._authenticated = False
            log.warning('Connection error during login.')
            if self.neterror_callback is not None:
                return self.neterror_callback()
            else:
                # raise an exception if there is no network connectivity
                raise NetConnectionError(e)
        except ResponseError as e:
            if e.status_code == 403:
                log.warning('Bad login credentials.')
                if self.login_callback is not None:
                    return self.login_callback(self._api)
                else:
                    # raise an exception if auth is bad
                    raise AuthError('Invalid Login: The credentials were invalid.')
            else:
                log.warning('ResponseError was raised with HTTP status: ' + e.status_code)
                # raise an exception if there is an error other than 403
                raise
        else:
            if self._config_token and self._config_verifier is not None:
                log.info('Client successfully authenticated.')
                self._authenticated = True
                if self.success_callback is not None:
                    return self.success_callback(self._api)
            else:
                log.info('Credentials not found. Prompting for a login.')
                if self.login_callback is not None:
                    self.login_callback(self._api)
                else:
                    # raise an exception if there is no auth yet
                    raise AuthError('Login required: Credentials are required to login.')

    def __getattr__(self, name):
        if self._authenticated:
            return self._api
        else:
            if self.doLogin():
                return self._api

try:
    from PySide import QtCore

    # Use the PySide authenticator if it is available

    class Authenticator(QtCore.QThread):
        login = QtCore.Signal(object)
        done = QtCore.Signal(object)
        setup = QtCore.Signal(object)
        neterror = QtCore.Signal(object)

        def __init__(self, parent=None):
            QtCore.QThread.__init__(self, parent)
            self.parent = parent

            self.api = None

            # create an instance of the configuration
            self.__config = Config(common.settings_file_path())

        def run(self):
            self.api = ApiConnection(success_callback=self.success,
                                     neterror_callback=self.network_error,
                                     login_callback=self.show_login_window)

        def show_login_window(self, api):
            """
            Sends a signal to the Main class to open the login window
            """
            try:
                self.parent.api = api
                api.get_request_token("http://www.kissync.com/oauth")

                auth_url = api.get_authorization_url()
                self.login.emit(QtCore.QUrl(auth_url))
            except Exception:
                self.network_error()

        def network_error(self):
            self.neterror.emit('error')

        def success(self, api):
            """
            When the login is successful, send signal to the appropriate ui
            """
            self.parent.api = api
            if self.__config.get('first-run'):
                self.setup.emit('done')
            else:
                self.done.emit('done')


except ImportError:
    # Pyside is not available
    def Authenticator(*args, **kwargs):
        raise NotImplementedError('PySide is not available. Install it '
                                  'using your system package manager.')
