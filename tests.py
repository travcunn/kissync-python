from collections import namedtuple
import datetime
import os
import shutil
import tempfile
import unittest

import fs
from fs.osfs import OSFS
try:
    import simplejson as json
except ImportError:
    import json

from app.core.common import settings_file_path
from app.core.config import Config
from app.core.errors import AuthError, NoAuthError
from app.core.auth import ApiConnection

from app.sync.definitions import FileDefinition
from app.sync.errors import BadEventError
import app.sync.events as events
from app.sync.realtime import RealtimeMessages
import app.sync.syncengine as syncengine
from app.sync.watcher import EventHandler


class MockAPI(object):
    """ Mock the SmartFile API. This mock class includes some test files. """
    def __init__(self):
        pass

    def get(self, path, *args, **kwargs):
        # Return a realtime sync key
        if path == ("/pref/user/sync.realtime-key"):
            response = {'value': 'abcdefghijklmnopqrstuvwxyz'}
            return response
        # Return a directory listing
        if path.startswith("/path/info"):
            path = path.replace("/path/info", "")
            return self._dir_listing(path)

    def put(self, path, *args, **kwargs):
        pass

    def _dir_listing(self, path):
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
                            has_attributes=False)
        folder1 = MockAPIFile('testfolder', isFile=False,
                              checksum=None, modified='2013-07-03 02:01:46')

        if path == '/':
            files = [file1.properties, file2.properties, file3.properties,
                     folder1.properties]
            return self._base_dir_listing(files)
        elif path is '/home/test/file1.txt':
            return file1.properties
        elif path is '/home/test/file2.txt':
            return file2.properties
        elif path is '/home/test/testfolder':
            return folder1.properties
        else:
            return path

    def _base_dir_listing(self, children):
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
    def __init__(self, path, isFile, checksum, modified, has_attributes=True):
        if has_attributes:
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


class MockWebsocket(object):
    def __init__(self):
        pass

    def send(self, data):
        return data


class ApiConnectionTest(unittest.TestCase):
    def test_blank_api_keys(self):
        """ Test blank api keys to make sure they are set """
        config = Config(settings_file_path())
        config.erase()

        nonblank_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        bad_secret = ''

        with self.assertRaises(NoAuthError):
            api = ApiConnection(token=nonblank_token, secret=bad_secret)
            self.assertNotEqual(api._secret, None)

    def test_blank_api_keys_callback(self):
        """ Test blank api keys with a callback """
        nonblank_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        bad_secret = ''

        def callback(api):
            self.assertNotEqual(api, None)

        ApiConnection(token=nonblank_token, secret=bad_secret,
                      login_callback=callback)

    def test_blank_user_credentials(self):
        config = Config(settings_file_path())
        config.erase()

        with self.assertRaises(NoAuthError):
            ApiConnection()

    def test_bad_api_keys(self):
        config = Config(settings_file_path())
        config.erase()

        bad_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        bad_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

        with self.assertRaises(NoAuthError):
            ApiConnection(token=bad_token, secret=bad_secret)

    def test_bad_login(self):
        """ Test bad user login credentials """
        config = Config(settings_file_path())
        config.erase()

        bad_token = ''
        bad_secret = ''

        config.set('login-token', bad_token)
        config.set('login-verifier', bad_secret)

        with self.assertRaises(NoAuthError):
            ApiConnection()


class LocalIndexerTest(unittest.TestCase):
    def setUp(self):
        # Create a temp dir
        self.temp_dir = tempfile.mkdtemp()
        self.sync_fs = OSFS(self.temp_dir)

        self.temp_files = ['/']
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
        local_indexer = syncengine.LocalIndexer(self.sync_fs)
        local_indexer.index()
        for path, definition in local_indexer.results.items():
            self.assertTrue(path in self.temp_files)

    def tearDown(self):
        # Recursively delete the temp dir
        shutil.rmtree(self.temp_dir)


class RemoteIndexerTest(unittest.TestCase):
    def test_index(self):
        api = MockAPI()
        remote_indexer = syncengine.RemoteIndexer(api)
        remote_indexer.index()
        expected_paths = [
                '/file1.txt', 
                '/file2.txt',
                '/file3.txt',
                '/testfolder'
                ]
        for path, definition in remote_indexer.results.items():
            self.assertTrue(path in expected_paths)


class SyncEngineEvents(unittest.TestCase):
    def setUp(self):
        api = MockAPI()
        dummy_dir = '/'
        self.sync_engine = syncengine.SyncEngine(api, dummy_dir)

        # create a dummy download worker
        dummy_remote_event = events.RemoteCreatedEvent('/helloworld.txt',
                                                       isDir=False)
        self.sync_engine.download_workers = [MockWorker(dummy_remote_event)]

        # create a dummy upload worker
        dummy_local_event = events.LocalCreatedEvent('/helloworld.txt',
                                                     isDir=False)
        self.sync_engine.upload_workers = [MockWorker(dummy_local_event)]

    def test_local_created_events(self):
        created_events = [
                        events.LocalCreatedEvent('/test.txt', isDir=False),
                        events.LocalCreatedEvent('/links.txt', isDir=False),
                        events.LocalCreatedEvent('/test.txt', isDir=False)
                ]
        for event in created_events:
            self.sync_engine.created_event(event)

        # Make sure the redundant task was deleted
        self.assertTrue(self.sync_engine.upload_queue.qsize() == 2)

    def test_remote_created_events(self):
        created_events = [
                        events.RemoteCreatedEvent('/helloworld.txt',
                                                  isDir=False),
                        events.RemoteCreatedEvent('/family.jpg',
                                                  isDir=False),
                        events.RemoteCreatedEvent('/helloworld.txt',
                                                  isDir=False)
                ]
        for event in created_events:
            self.sync_engine.created_event(event)

        # Make sure the redundant task was deleted.
        # Also make sure '/helloworld.txt' is not put into the queue,
        # since one of the dummy download workers is already processing it.
        self.assertTrue(self.sync_engine.download_queue.qsize() == 1)
        self.assertTrue(self.sync_engine.download_queue.queue[0].path == "/family.jpg")

    def test_bad_created_event(self):
        with self.assertRaises(BadEventError):
            self.sync_engine.created_event("bad event")


    def test_local_deleted_events(self):
        Task = namedtuple('Task', ['path'])
        self.sync_engine.upload_queue.put(Task('/helloworld.txt'))
        self.sync_engine.download_queue.put(Task('/helloworld.txt'))

        deleted_events = [
                        events.LocalDeletedEvent('/helloworld.txt'),
                        events.LocalDeletedEvent('/hellomoon.txt'),
                        events.LocalDeletedEvent('/helloworld.txt')
                ]
        for event in deleted_events:
            self.sync_engine.deleted_event(event)

        # Make sure matching tasks in the queues were deleted
        self.assertTrue(self.sync_engine.download_queue.qsize() == 0)
        self.assertTrue(self.sync_engine.upload_queue.qsize() == 0)

    def test_bad_deleted_event(self):
        with self.assertRaises(BadEventError):
            self.sync_engine.deleted_event("bad event")

    def test_local_modified_event(self):
        Task = namedtuple('Task', ['path'])
        self.sync_engine.upload_queue.put(Task('/modifiedfile.txt'))

        modified_events = [
                        events.LocalModifiedEvent('/modifiedfile.txt'),
                        events.LocalModifiedEvent('/anothermodifiedfile.txt')
                ]
        for event in modified_events:
            self.sync_engine.modified_event(event)

        # Make sure the redundant task was removed
        self.assertTrue(self.sync_engine.upload_queue.qsize() == 2)

    def test_remote_modified_event(self):
        Task = namedtuple('Task', ['path'])
        self.sync_engine.download_queue.put(Task('/remotemodified.txt'))

        modified_events = [
                        events.RemoteModifiedEvent('/remotemodified.txt'),
                        events.RemoteModifiedEvent('/remotefile.txt')
                ]
        for event in modified_events:
            self.sync_engine.modified_event(event)

        # Maks sure the redundant task was removed
        self.assertTrue(self.sync_engine.download_queue.qsize() == 2)

    def test_bad_modified_event(self):
        with self.assertRaises(BadEventError):
            self.sync_engine.modified_event("bad event")

    def test_local_moved_event(self):
        mock_upload_worker = MockWorker(events.LocalCreatedEvent('/source.txt',
                                                                 isDir=False))
        mock_download_worker = MockWorker(events.LocalCreatedEvent('/source.txt',
                                                                   isDir=False))
        self.sync_engine.upload_workers.append(mock_upload_worker)
        self.sync_engine.download_workers.append(mock_download_worker)

        self.sync_engine.upload_queue.put(events.LocalCreatedEvent('/source.txt',
                                                                 isDir=False))
        self.sync_engine.upload_queue.put(events.LocalCreatedEvent('/source.txt',
                                                                 isDir=False))
        self.sync_engine.download_queue.put(events.RemoteCreatedEvent('/source.txt',
                                                                 isDir=False))
        self.sync_engine.download_queue.put(events.RemoteCreatedEvent('/source.txt',
                                                                 isDir=False))

        deleted_events = [
                        events.LocalDeletedEvent('/destination.txt'),
                        events.LocalDeletedEvent('/source.txt')
                ]
        for event in deleted_events:
            self.sync_engine.deleted_event(event)

        moved_events = [
                        events.LocalMovedEvent('/source.txt',
                            '/destination.txt'),
                        events.LocalMovedEvent('/source.txt',
                            '/destination.txt')
                ]
        for event in moved_events:
            self.sync_engine.moved_event(event)

        # Make sure events were moved in the simple tasks queue
        for event in self.sync_engine.simple_tasks.queue:
            if isinstance(event, events.LocalDeletedEvent):
                # Since the event path is moved, make sure other events are moved
                self.assertTrue(event.path == '/destination.txt')

        # Make sure events were moved in the download queue
        for event in self.sync_engine.download_queue.queue:
            self.assertTrue(event.path == '/destination.txt')

        # Make sure events were moved in the upload queue
        for event in self.sync_engine.upload_queue.queue:
            self.assertTrue(event.path == '/destination.txt')

    def test_bad_moved_event(self):
        with self.assertRaises(BadEventError):
            self.sync_engine.moved_event('bad event')


class SyncEngineComparisons(unittest.TestCase):
    def setUp(self):
        api = MockAPI()
        dummy_dir = '/'
        self.sync_engine = syncengine.SyncEngine(api, dummy_dir)

        self.local_files = {}
        self.local_files['/file1.txt'] = FileDefinition(path='/file1.txt',
                                checksum='fc5e038d38a57032085441e7fe7010b0',
                                modified='2013-07-03 21:46:53',
                                size=10000,
                                is_dir=False)
        self.local_files['/folder1'] =  FileDefinition(path='/folder1',
                                checksum=None,
                                modified='2013-07-03 21:45:53',
                                size=None,
                                is_dir=True)
        self.local_files['/folder1/file2.txt'] = FileDefinition(
                                path='/folder1/file2.txt',
                                checksum='467746e92e5325503b2769c80563c870',
                                modified='2013-03-03 21:45:53',
                                size=5000,
                                is_dir=False)
        self.local_files['/file3.txt'] = FileDefinition(path='/file3.txt',
                                checksum='sdflkjsdfkjw23ijfkljlkjdslkfjjkj',
                                modified='2013-07-03 21:40:20',
                                size=30,
                                is_dir=False)

        self.remote_files = {}
        self.remote_files['/file1.txt'] = FileDefinition(path='/file1.txt',
                                checksum='fc5e038d38a57032085441e7fe7010c4',
                                modified='2013-07-03 21:48:53',
                                size=12000,
                                is_dir=False)
        self.remote_files['/folder1'] = FileDefinition(path='/folder1',
                                checksum=None,
                                modified='2013-07-03 21:45:53',
                                size=None,
                                is_dir=True)
        self.remote_files['/folder1/file2.txt'] = FileDefinition(
                                path='/folder1/file2.txt',
                                checksum='467746e92e5325503b2769c80563c875',
                                modified='2013-03-03 21:44:53',
                                size=5000,
                                is_dir=False)
        self.remote_files['/file4.txt'] = FileDefinition(path='/file4.txt',
                                checksum='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                                modified='2013-03-03 19:44:53',
                                size=90,
                                is_dir=False)

    def test_result_comparison(self):
        self.sync_engine.compare_results(self.remote_files, self.local_files)

        r = self.remote_files['/file1.txt']
        downqueue = []
        for item in self.sync_engine.download_queue.queue:
            downqueue.append(item.path)
        self.assertTrue(r.path in downqueue)

        upqueue = []
        for item in self.sync_engine.upload_queue.queue:
            upqueue.append(item.path)
        l = self.local_files['/file3.txt']
        # Ensure that file 4 in local_files is put into the upload queue
        self.assertTrue(l.path in upqueue)


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

        def processing(path):
            return False

        handler = EventHandler(processing, sync_dir=self.temp_dir,
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


class RealTimeMessagingTest(unittest.TestCase):
    def test_messages(self):
        api = MockAPI()

        called = [False, False, False, False]
        def moved_callback(event):
            called[0] = True
        def created_callback(event):
            called[1] = True
        def deleted_callback(event):
            called[2] = True
        def modified_callback(event):
            called[3] = True

        realtime = RealtimeMessages(api=api, on_moved=moved_callback,
                on_created=created_callback, on_deleted=deleted_callback,
                on_modified=modified_callback)

        moved_data = json.dumps({
                'uuid': 'testuuid',
                'type': 'LocalMovedEvent',
                'path': '/dest.txt',
                'src': '/src.txt'
            })

        realtime._on_message(None, moved_data)

        created_data = json.dumps({
                'uuid': 'testuuid',
                'type': 'LocalCreatedEvent',
                'path': '/file.txt',
                'isDir': False
            })

        realtime._on_message(None, created_data)

        deleted_data = json.dumps({
                'uuid': 'testuuid',
                'type': 'LocalDeletedEvent',
                'path': '/file.txt'
            })

        realtime._on_message(None, deleted_data)

        modified_data = json.dumps({
                'uuid': 'testuuid',
                'type': 'LocalModifiedEvent',
                'path': '/file.txt'
            })

        realtime._on_message(None, modified_data)

        for x in called:
            self.assertTrue(x is True)

    def test_bad_messages(self):
        realtime = RealtimeMessages(None)

        missing_uuid = json.dumps({
                'type': 'LocalModifiedEvent',
                'path': '/file.txt'
            })
        realtime._on_message(None, missing_uuid)

        same_uuid = json.dumps({
                'uuid': realtime.auth_uuid,
                'type': 'LocalModifiedEvent',
                'path': '/file.txt'
            })
        realtime._on_message(None, same_uuid)

    def test_closed_state(self):
        realtime = RealtimeMessages(None)
        realtime._on_close(None)
        self.assertTrue(realtime.connected is False)
        self.assertTrue(realtime.authenticated is False)

    def test_send_to_websocket(self):
        realtime = RealtimeMessages(None)
        realtime.ws = MockWebsocket()
        realtime.auth_uuid = 'test_uuid'
        realtime.connected = True
        realtime.authenticated = True

        moved_event = events.LocalMovedEvent(src="/src.txt", path="/dest.txt")
        update = realtime.update(moved_event)
        json_data = json.loads(update)
        self.assertTrue(json_data['event_type'] == "LocalMovedEvent")

        created_event = events.LocalCreatedEvent(path="/newfolder", isDir=True)
        update = realtime.update(created_event)
        json_data = json.loads(update)
        self.assertTrue(json_data['event_type'] == "LocalCreatedEvent")

        # Now set the flag for the client being disconnected
        realtime.connected = False
        realtime.update(events.LocalCreatedEvent(path="/newfolder", isDir=True))
        task = realtime.offline_queue.get()
        json_data = json.loads(task)
        self.assertTrue(json_data['event_type'] == "LocalCreatedEvent")


if __name__ == '__main__':
    unittest.main()
