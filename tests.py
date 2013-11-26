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

from app.sync.dictqueue import LifoDictQueue, Task
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


class LifoDictQueueTest(unittest.TestCase):
    def test_insert_task_and_get(self):
        queue = LifoDictQueue()
        task = Task("test_id", "test_properties")
        queue.put(task)
        self.assertEqual(task, queue.get())

    def test_task_order(self):
        """ Make sure the queue is LIFO. """
        queue = LifoDictQueue()
        task1 = Task("test_id1", "test_properties1")
        task2 = Task("test_id2", "test_properties2")
        task3 = Task("test_id2", "test_properties3")
        queue.put(task1)
        queue.put(task2)
        queue.put(task3)
        self.assertEqual(3, queue.qsize())
        self.assertEqual(task3, queue.get())
        self.assertEqual(2, queue.qsize())
        self.assertEqual(task2, queue.get())
        self.assertEqual(1, queue.qsize())
        self.assertEqual(task1, queue.get())
        self.assertEqual(0, queue.qsize())

    def test_regular_tasks(self):
        queue = LifoDictQueue()
        task = "test_task_object"
        queue.put(task)
        # A task object with a generated hash id will be created
        get_task = queue.get()
        self.assertTrue(hash(task) == get_task.key)
        self.assertTrue(task == get_task.properties)

    def test_update_task_key(self):
        queue = LifoDictQueue()
        task = Task("/test/path/SmartFile", "test object")
        queue.put(task)
        new_task_key = "/test/newpath/SmartFile"
        queue.updateTaskKey("/test/path/SmartFile", new_task_key)
        self.assertEqual(new_task_key, queue.get().key)
        # try updating a key that does not exist
        with self.assertRaises(KeyError):
            queue.updateTaskKey("/badkey", "/foo")


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

    """
    def test_create_event(self):
        test_event = events.LocalMovedEvent('/source.txt', '/destination.txt')
        test_deleted_event = events.LocalDeletedEvent('/home/Smartfile/test.txt')
        self.syncEngine.addEvent(test_event)
    """


if __name__ == '__main__':
    unittest.main()
