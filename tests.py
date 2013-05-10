from smartfile import OAuthClient
from configuration import Configuration
from filedatabase import FileDatabase

import os
import unittest


class LoginTestCase(unittest.TestCase):
    def test_login(self):
        api = OAuthClient("zGSJpILRq2889Ne2bPBdEmEZLsRHpe", "KOb97irJG84PJ8dtEkoYt2Kqwz3VJa")
        api.get_request_token()
        api.get_authorization_url()


class FileDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.database = FileDatabase(self)

    def test_database_indexlocalfiles(self):
        self.assertTrue(self.database.indexLocalFiles())

    def test_database_loadremotelisting(self):
        self.database.loadRemoteListingFile()


class ConfigurationTest(unittest.TestCase):
    def test_blank_config_file(self):
        self.assertRaises(Configuration())

    def test_initial_setup(self):
        if not os.path.exists(os.path.join(os.path.expanduser("~"), ".kissync")):
            os.makedirs(os.path.join(os.path.expanduser("~"), ".kissync"))
        Configuration(os.path.join(os.path.expanduser("~"), ".kissync", "configuration.cfg"))

if __name__ == '__main__':
    unittest.main()
