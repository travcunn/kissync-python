from smartfile import OAuthClient
from filedatabase import FileDatabase
import unittest


class LoginTestCase(unittest.TestCase):
    def test_login(self):
        api = OAuthClient("zGSJpILRq2889Ne2bPBdEmEZLsRHpe", "KOb97irJG84PJ8dtEkoYt2Kqwz3VJa")
        api.get_request_token()
        api.get_authorization_url()


class FileDatabaseTest(unittest.TestCase):
    def __init__(self, parent=None):
        super(FileDatabaseTest, self).__init__(parent)
        self.database = FileDatabase(self)

    def test_database_indexlocalfiles(self):
        self.assertTrue(self.database.indexLocalFiles())

    def test_database_loadremotelisting(self):
        self.assertTrue(self.database.loadRemoteListingFile())


if __name__ == '__main__':
    unittest.main()
