import unittest

from app.core.errors import AuthException
from app.core.auth import ApiConnection


class ApiConnectionTest(unittest.TestCase):
    def test_blank_api_keys(self):
        good_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        bad_secret = None

        with self.assertRaises(AuthException):
            api = ApiConnection(token=good_token, secret=bad_secret)
            self.assertNotEqual(api._secret, None)

    def test_bad_api_keys(self):
        bad_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        bad_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

        with self.assertRaises(AuthException):
            ApiConnection(token=bad_token, secret=bad_secret)


if __name__ == '__main__':
    unittest.main()
