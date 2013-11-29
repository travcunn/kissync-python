from collections import namedtuple
import os
import shutil
import tempfile
import unittest

import fs
from fs.osfs import OSFS

from app.core.common import settingsFile
from app.core.configuration import Configuration
from app.core.errors import AuthException
from app.core.auth import ApiConnection

from app.sync.errors import BadEventException
import app.sync.events as events
import app.sync.syncengine as syncengine


class MockAPI(object):
    """ Mock the SmartFile API. This mock class includes some test files. """
    def __init__(self):
        pass

    def get(self, path, *args, **kwargs):
        if path.startswith("/path/info"):
            path = path.replace("/path/info", "")
        return self._dirListing(path)

    def _dirListing(self, path):
        """ Create a directory listing. """
        file1 = MockAPIFile('file1.txt', isFile=True,
                            checksum='098f6bcd4621d373cade4e832627b4f6',
                            modified='2013-07-03 05:01:46')
        file2 = MockAPIFile('file2.txt', isFile=True,
                            checksum='8c7dd922ad47494fc02c388e12c00eac',
                            modified='2013-07-03 06:01:46')
        file3 = MockAPIFile('file3.txt', isFile=True,
                            checksum='16fe50845e10b5fa815dbfa2bc566f1a',
                            modified='2013-07-03 06:01:46', 
                            hasAttributes=False)
        folder1 = MockAPIFile('testfolder', isFile=False,
                              checksum=None, modified='2013-07-03 02:01:46')

        if path == '/':
            files = [file1.properties, file2.properties, file3.properties,
                     folder1.properties]
            return self._baseDirListing(files)
        elif path is '/home/test/file1.txt':
            return file1.properties
        elif path is '/home/test/file2.txt':
            return file2.properties
        elif path is '/home/test/testfolder':
            return folder1.properties
        else:
            return path

    def _baseDirListing(self, children):
        """ Create a base directory listing. """
        mock_response = {
            "acl": {
                "list": True,
                "read": True,
                "remove": True,
                "write": True
            },
            "attributes": {},
            "children": children,
            "extension": "",
            "id": 1,
            "isdir": True,
            "isfile": False,
            "items": 0,
            "mime": "application/x-directory",
            "name": "",
            "owner": None,
            "path": "/",
            "size": 0,
            "tags": [],
            "time": "2013-10-21T15:24:02",
            "url": "https://app.smartfile.com/api/2/path/info/"
            }
        return mock_response


class MockAPIFile(object):
    """ Mock the json for a single file returned by the API. """
    def __init__(self, path, isFile, checksum, modified, hasAttributes=True):
        if hasAttributes:
            attributes = {
                "checksum": checksum,
                "modified": modified
            }
        else:
            attributes = {}
        self.properties = {
            "acl": {
                "list": True,
                "read": True,
                "remove": True,
                "write": True
            },
            "attributes": attributes,
            "extension": os.path.splitext(path)[1],
            "id": 1,
            "isdir": not isFile,
            "isfile": isFile,
            "items": None,
            "mime": "text/html",
            "name": path,
            "owner": {
                "email": "travcunn@umail.iu.edu",
                "first_name": "Test",
                "last_name": "Account",
                "name": "Test Account",
                "url": "https://app.smartfile.com/api/2/user/testaccount/",
                "username": "TestAccount"
            },
            "path": "/%s" % (path),
            "size": 1,
            "tags": [],
            "time": modified.split(" ")[0] + "T" + modified.split(" ")[1],
            "url": "https://app.smartfile.com/api/2/path/info/%s" % (path)
        }


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


class IndexerTest(unittest.TestCase):
    def test_require_override(self):
        with self.assertRaises(NotImplementedError):
            syncengine.Indexer()


class LocalIndexerTest(unittest.TestCase):
    def setUp(self):
        # Create a temp dir
        self.temp_dir = tempfile.mkdtemp()
        self.syncFS = OSFS(self.temp_dir)

        self.temp_files = []
        # Put some files in the temp dir
        for i in range(10):
            path = os.path.join(self.temp_dir, str(i))
            with open(path, "a+") as f:
                f.write("test contents")
            absolute_name = fs.path.abspath(str(i))
            self.temp_files.append(absolute_name)

    def test_index(self):
        local_indexer = syncengine.LocalIndexer(self.syncFS)
        for result in local_indexer.results:
            self.assertTrue(result.path in self.temp_files)

    def tearDown(self):
        # Recursively delete the temp dir
        shutil.rmtree(self.temp_dir)


class RemoteIndexerTest(unittest.TestCase):
    def test_index(self):
        api = MockAPI()
        remote_indexer = syncengine.RemoteIndexer(api)

        expected_paths = [
                '/file1.txt', 
                '/file2.txt',
                '/file3.txt',
                '/testfolder'
                ]
        for result in remote_indexer.results:
            self.assertTrue(result.path in expected_paths)


class SyncEngineEvents(unittest.TestCase):
    def setUp(self):
        api = MockAPI()
        self.syncEngine = syncengine.SyncEngine(api)

    def test_local_created_events(self):
        created_events = [
                        events.LocalCreatedEvent('/test.txt'),
                        events.LocalCreatedEvent('/links.txt'),
                        events.LocalCreatedEvent('/test.txt')
                ]
        for event in created_events:
            self.syncEngine.createdEvent(event)

        # Make sure the redundant task was deleted
        self.assertTrue(self.syncEngine.uploadQueue.qsize() == 2)

    def test_remote_created_events(self):
        created_events = [
                        events.RemoteCreatedEvent('/helloworld.txt'),
                        events.RemoteCreatedEvent('/family.jpg'),
                        events.RemoteCreatedEvent('/helloworld.txt')
                ]
        for event in created_events:
            self.syncEngine.createdEvent(event)

        # Make sure the redundant task was deleted
        self.assertTrue(self.syncEngine.downloadQueue.qsize() == 2)

    def test_bad_created_event(self):
        with self.assertRaises(BadEventException):
            self.syncEngine.createdEvent("bad event")


    def test_local_deleted_events(self):
        Task = namedtuple('Task', ['path'])
        self.syncEngine.uploadQueue.put(Task('/helloworld.txt'))
        self.syncEngine.downloadQueue.put(Task('/helloworld.txt'))

        deleted_events = [
                        events.LocalDeletedEvent('/helloworld.txt'),
                        events.LocalDeletedEvent('/hellomoon.txt'),
                        events.LocalDeletedEvent('/helloworld.txt')
                ]
        for event in deleted_events:
            self.syncEngine.deletedEvent(event)

        # Make sure matching tasks in the queues were deleted
        self.assertTrue(self.syncEngine.downloadQueue.qsize() == 0)
        self.assertTrue(self.syncEngine.uploadQueue.qsize() == 0)

    def test_bad_deleted_event(self):
        with self.assertRaises(BadEventException):
            self.syncEngine.deletedEvent("bad event")

    def test_local_modified_event(self):
        Task = namedtuple('Task', ['path'])
        self.syncEngine.uploadQueue.put(Task('/modifiedfile.txt'))

        modified_events = [
                        events.LocalModifiedEvent('/modifiedfile.txt'),
                        events.LocalModifiedEvent('/anothermodifiedfile.txt')
                ]
        for event in modified_events:
            self.syncEngine.modifiedEvent(event)

        # Make sure the redundant task was removed
        self.assertTrue(self.syncEngine.uploadQueue.qsize() == 2)

    def test_remote_modified_event(self):
        Task = namedtuple('Task', ['path'])
        self.syncEngine.downloadQueue.put(Task('/remotemodified.txt'))

        modified_events = [
                        events.RemoteModifiedEvent('/remotemodified.txt'),
                        events.RemoteModifiedEvent('/remotefile.txt')
                ]
        for event in modified_events:
            self.syncEngine.modifiedEvent(event)

        # Maks sure the redundant task was removed
        self.assertTrue(self.syncEngine.downloadQueue.qsize() == 2)

    def test_bad_modified_event(self):
        with self.assertRaises(BadEventException):
            self.syncEngine.modifiedEvent("bad event")


if __name__ == '__main__':
    unittest.main()
