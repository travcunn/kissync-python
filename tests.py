import os
import unittest

from app.core.common import settingsFile
from app.core.configuration import Configuration
from app.core.errors import AuthException
from app.core.auth import ApiConnection


class ApiConnectionTest(unittest.TestCase):
    def test_blank_api_keys(self):
        """ Test blank api keys to make sure they are set """
        if os.path.isfile(settingsFile()):
            os.remove(settingsFile())
        nonblank_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        bad_secret = None

        with self.assertRaises(AuthException):
            api = ApiConnection(token=nonblank_token, secret=bad_secret)
            self.assertNotEqual(api._secret, None)

    def test_blank_api_keys_callback(self):
        """ Test blank api keys with a callback """
        nonblank_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        bad_secret = None

        def callback(api):
            self.assertNotEqual(api, None)

        ApiConnection(token=nonblank_token, secret=bad_secret,
                      login_callback=callback)

    def test_blank_user_credentials(self):
        if os.path.isfile(settingsFile()):
            os.remove(settingsFile())

        with self.assertRaises(AuthException):
            ApiConnection()

    def test_bad_api_keys(self):
        bad_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        bad_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

        with self.assertRaises(AuthException):
            ApiConnection(token=bad_token, secret=bad_secret)

    def test_bad_login(self):
        """ Test bad user login credentials """
        if os.path.isfile(settingsFile()):
            os.remove(settingsFile())
        config = Configuration(settingsFile())

        bad_token = None
        bad_secret = None

        config.set("Login", "token", bad_token)
        config.set("Login", "verifier", bad_secret)

        with self.assertRaises(AuthException):
            ApiConnection()


if __name__ == '__main__':
    unittest.main()
