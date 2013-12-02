from collections import namedtuple
import datetime
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

from app.sync.definitions import FileDefinition
from app.sync.errors import BadEventException
import app.sync.events as events
import app.sync.syncengine as syncengine
from app.sync.watcher import EventHandler


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


class MockWorker(object):
    def __init__(self, current_task=None):
        self.current_task = current_task

    def cancel(self):
        pass


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
            basename = i
            # produce a file that wont be picked up due to the indexer filter
            if i is 9:
                basename = str(i) + '~'
            path = os.path.join(self.temp_dir, str(basename))
            with open(path, "a+") as f:
                f.write("test contents")
            absolute_name = fs.path.abspath(str(basename))
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
        dummy_dir = '/'
        self.syncEngine = syncengine.SyncEngine(api, dummy_dir)

        # create a dummy download worker
        dummy_remote_event = events.RemoteCreatedEvent('/helloworld.txt', isDir=False)
        self.syncEngine.downloadWorkers = [MockWorker(dummy_remote_event)]

        # create a dummy upload worker
        dummy_local_event = events.LocalCreatedEvent('/helloworld.txt', isDir=False)
        self.syncEngine.uploadWorkers = [MockWorker(dummy_local_event)]

    def test_local_created_events(self):
        created_events = [
                        events.LocalCreatedEvent('/test.txt', isDir=False),
                        events.LocalCreatedEvent('/links.txt', isDir=False),
                        events.LocalCreatedEvent('/test.txt', isDir=False)
                ]
        for event in created_events:
            self.syncEngine.createdEvent(event)

        # Make sure the redundant task was deleted
        self.assertTrue(self.syncEngine.uploadQueue.qsize() == 2)

    def test_remote_created_events(self):
        created_events = [
                        events.RemoteCreatedEvent('/helloworld.txt', isDir=False),
                        events.RemoteCreatedEvent('/family.jpg', isDir=False),
                        events.RemoteCreatedEvent('/helloworld.txt', isDir=False)
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

    def test_local_moved_event(self):
        deleted_events = [
                        events.LocalDeletedEvent('/destination.txt'),
                        events.LocalDeletedEvent('/source.txt')
                ]
        for event in deleted_events:
            self.syncEngine.deletedEvent(event)

        moved_events = [
                        events.LocalMovedEvent('/source.txt',
                            '/destination.txt'),
                        events.LocalMovedEvent('/source.txt',
                            '/destination.txt')
                ]
        for event in moved_events:
            self.syncEngine.movedEvent(event)

        for event in self.syncEngine.simpleTasks.queue:
            if isinstance(event, events.LocalDeletedEvent):
                # Since the event path is moved, make sure other events are moved
                self.assertTrue(event.path == '/destination.txt')

    def test_bad_moved_event(self):
        with self.assertRaises(BadEventException):
            self.syncEngine.movedEvent('bad event')


class SyncEngineComparisons(unittest.TestCase):
    def setUp(self):
        api = MockAPI()
        dummy_dir = '/'
        self.syncEngine = syncengine.SyncEngine(api, dummy_dir)

        self.local_files = [
                    FileDefinition(path='/file1.txt',
                                   checksum='fc5e038d38a57032085441e7fe7010b0',
                                   modified='2013-07-03 21:46:53',
                                   size=10000,
                                   isDir=False
                                   ),
                    FileDefinition(path='/folder1',
                                   checksum=None,
                                   modified='2013-07-03 21:45:53',
                                   size=None,
                                   isDir=True),
                    FileDefinition(path='/folder1/file2.txt',
                                   checksum='467746e92e5325503b2769c80563c870',
                                   modified='2013-03-03 21:45:53',
                                   size=5000,
                                   isDir=False),
                    FileDefinition(path='/file3.txt',
                                   checksum='sdflkjsdfkjw23ijfkljlkjdslkfjjkj',
                                   modified='2013-07-03 21:40:20',
                                   size=30,
                                   isDir=False)
                ]

        self.remote_files = [
                    FileDefinition(path='/file1.txt',
                                   checksum='fc5e038d38a57032085441e7fe7010c4',
                                   modified='2013-07-03 21:48:53',
                                   size=12000,
                                   isDir=False
                                   ),
                    FileDefinition(path='/folder1',
                                   checksum=None,
                                   modified='2013-07-03 21:45:53',
                                   size=None,
                                   isDir=True),
                    FileDefinition(path='/folder1/file2.txt',
                                   checksum='467746e92e5325503b2769c80563c875',
                                   modified='2013-03-03 21:44:53',
                                   size=5000,
                                   isDir=False),
                    FileDefinition(path='/file4.txt',
                                   checksum='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                                   modified='2013-03-03 19:44:53',
                                   size=90,
                                   isDir=False)
                ]

    def test_result_comparison(self):
        self.syncEngine.compare_results(self.remote_files, self.local_files)

        self.assertTrue(self.remote_files[0] in self.syncEngine.downloadQueue.queue)

        # Ensure that file 4 in local_files is put into the upload queue
        self.assertTrue(self.local_files[3] in self.syncEngine.uploadQueue.queue)


class WatcherEventsTest(unittest.TestCase):
    def setUp(self):
        # Create a temp dir
        self.temp_dir = tempfile.mkdtemp()
        self.syncFS = OSFS(self.temp_dir)

        self.temp_files = []

        # Put 2 files into the temporary directory
        for i in range(2):
            path = os.path.join(self.temp_dir, str(i))
            with open(path, "a+") as f:
                f.write("test contents")
            self.temp_files.append(path)

        DummyEvent = namedtuple('Event', ['src_path', 'dest_path', 'is_directory'])

        # Create a dummy event to use in each test
        self.dummy_event = DummyEvent(self.temp_files[0], self.temp_files[1], False)

    def test_moved_event(self):
        callback_called = [None, None, None, None]
        def movecallback(event):
            callback_called[0] = event
        def createcallback(event):
            callback_called[1] = event
        def deletecallback(event):
            callback_called[2] = event
        def modifycallback(event):
            callback_called[3] = event

        handler = EventHandler(sync_dir=self.temp_dir,
                               moved_callback=movecallback,
                               created_callback=createcallback,
                               deleted_callback=deletecallback,
                               modified_callback=modifycallback)
        handler.on_moved(self.dummy_event)
        handler.on_created(self.dummy_event)
        handler.on_deleted(self.dummy_event)
        handler.on_modified(self.dummy_event)

        self.assertTrue(isinstance(callback_called[0], events.LocalMovedEvent))
        self.assertTrue(isinstance(callback_called[1], events.LocalCreatedEvent))
        self.assertTrue(isinstance(callback_called[2], events.LocalDeletedEvent))
        self.assertTrue(isinstance(callback_called[3], events.LocalModifiedEvent))

    def tearDown(self):
        # Recursively delete the temp dir
        shutil.rmtree(self.temp_dir)


class EventInitTest(unittest.TestCase):
    def test_event_init(self):
        base_event = events.BaseEvent('/testfile.txt')
        self.assertTrue(isinstance(base_event.timestamp, datetime.datetime))
        self.assertTrue(hash(base_event) == hash('BaseEvent'))

        lme = events.LocalMovedEvent('/testdir', '/newdir')
        self.assertTrue(lme.src == '/testdir')
        self.assertTrue(lme.path == '/newdir')

        lce = events.LocalCreatedEvent('/testfile.txt', isDir=True)
        self.assertTrue(lce.path == '/testfile.txt')
        self.assertTrue(lce.isDir)

        lde = events.LocalDeletedEvent('/testfile.txt')
        self.assertTrue(lde.path == '/testfile.txt')

        lme = events.LocalModifiedEvent('/testfile.txt')
        self.assertTrue(lde.path == '/testfile.txt')

        rme = events.RemoteMovedEvent('/testfile.txt', '/file.txt')
        self.assertTrue(rme.src == '/testfile.txt')
        self.assertTrue(rme.path == '/file.txt')

        rce = events.RemoteCreatedEvent('/testfile.txt', isDir=False)
        self.assertTrue(rce.path == '/testfile.txt')
        self.assertTrue(rce.isDir == False)

        rde = events.RemoteDeletedEvent('/testfile.txt')
        self.assertTrue(rde.path == '/testfile.txt')

        rmode = events.RemoteModifiedEvent('/testfile.txt')
        self.assertTrue(rmode.path == '/testfile.txt')



if __name__ == '__main__':
    unittest.main()
