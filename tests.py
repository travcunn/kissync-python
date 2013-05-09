from smartfile import OAuthClient
import unittest


class LoginTestCase(unittest.TestCase):
    def test_login(self):
        api = OAuthClient("zGSJpILRq2889Ne2bPBdEmEZLsRHpe", "KOb97irJG84PJ8dtEkoYt2Kqwz3VJa")
        try:
            api.get_request_token()
            client_token = api.get_authorization_url()
        except:
            oauthtest = False
        else:
            oauthtest = True

        self.assertTrue(oauthtest)

if __name__ == '__main__':
    unittest.main()