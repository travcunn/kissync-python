import hashlib
import os
from Queue import Queue
import shutil
import ssl
import thread
import threading
import time
import uuid
import websocket
try:
    import simplejson as json
except ImportError:
    import json

import common
from definitions import FileDefinition


class RealtimeMessages(threading.Thread):
    def __init__(self, api, moved_callback=None, created_callback=None,
                 deleted_callback=None, modified_callback=None):
        threading.Thread.__init__(self)

        self.moved_callback = moved_callback
        self.created_callback = created_callback
        self.deleted_callback = deleted_callback
        self.modified_callback = modified_callback

        self.websocket_address = "wss://www.kissync.com/sync"

        # Generate a unique authentication UUID for this client
        hash = hashlib.sha1()
        hash.update(str(time.time()))
        self.auth_uuid = hash.hexdigest()[:10]

        # Queue for offline messages
        self.offline_queue = Queue()

        self.connected = False
        self.authenticated = False

    def run(self):
        while True:
            self.create_connection()
            self.ws.run_forever(sslopt={"ssl_version": ssl.PROTOCOL_TLSv1},
                                ping_interval=45)

            # if the client disconnects, delay, then reconnect
            time.sleep(10)

    def create_connection(self):
        self.ws = websocket.WebSocketApp(self.websocket_address,
                                         on_message=self._on_message,
                                         on_error=self._on_error,
                                         on_close=self._on_close,
                                         on_open=self._on_open)

    def _processSendQueue(self, *args):
        """
        Send changes that occured when the client was offline to the realtime
        sync server.
        """
        taskInQueue = False
        while True:
            while self.connected and self.authenticated:
                # Check if a task is already loaded
                if taskInQueue is False:
                    # This blocks until it gets a task
                    object = self.offline_queue.get()
                taskInQueue = True
                if self.connected is False or self.authenticated is False:
                    break
                self.ws.send(object)
                self.offline_queue.task_done()
                taskInQueue = False
            time.sleep(.01)

    def _sendChanges(self, changes):
        """ Prepares data to be sent to the websocket. """
        # Prepare the dictionary to send
        send_data = {'uuid': self.auth_uuid}
        send_data.update(changes)
        data = json.dumps(send_data)

        # Check if the websocket is available
        if self.connected and self.authenticated:
            # send the json encoded message
            self.ws.send(data)
        else:
            # process the message when the websocket is available
            self.parent.changesQueue.put(data)

    def update(self, event):
        """ Send an event to the websocket. """
        send_data = {'event_type': event.path, 'path': event.path}
        if hasattr(event, 'src'):
            destination = {'src': event.src}
            send_data.update(destination)

        self._sendChanges(send_data)

    def _on_message(self, ws, message):
        json_data = json.loads(message)

        if 'type' in json_data:
            if json_data['uuid'] == self.auth_uuid:
                return
            message_type = json_data['type']
            if message_type == 'created_file':
                path = json_data['path']
                checksum = "123"  # Provide something not None
                modified = None
                size = json_data['size']
                isDir = False
                remotefile = FileDefinition(path, checksum, modified,
                                            size, isDir)

                print "file created on the realtime"
                print path

                # Ignore this file in the watcher
                self.parent.ignoreFiles.append(path)

                self.parent.downloadQueue.put(remotefile)
            elif message_type == 'created_dir':
                path = json_data['path']
                checksum = "123"
                modified = None
                size = 0
                isDir = True
                remotefile = FileDefinition(path, checksum, modified,
                                            size, isDir)

                # Ignore this file in the watcher
                self.parent.ignoreFiles.append(path)

                self.parent.downloadQueue.put(remotefile)
            elif message_type == 'modified':
                path = json_data['path']
                checksum = "123"
                modified = None
                size = json_data['size']
                isDir = False
                remotefile = FileDefinition(path, checksum, modified,
                                            size, isDir)

                # Ignore this file in the watcher
                self.parent.ignoreFiles.append(path)

                if self.parent.syncLoaded:
                    self.parent.syncDownQueue.put(remotefile)
                else:
                    self.parent.downloadQueue.put(remotefile)
            elif message_type == 'deleted':
                serverPath = json_data['path']
                path = common.basePath(serverPath)
                absolutePath = os.path.join(self.parent._syncDir, path)

                # Ignore this file in the watcher
                self.parent.ignoreFiles.append(serverPath)

                # Throw delete fu at that file!
                try:
                    os.remove(absolutePath)
                except:
                    pass
                try:
                    # notice: this thing goes ham
                    shutil.rmtree(absolutePath)
                except:
                    pass
                try:
                    os.rmdir(absolutePath)
                except:
                    pass
            elif message_type == 'moved':
                serverPath = json_data['path']
                path = common.basePath(serverPath)
                absolutePath = os.path.join(self.parent._syncDir, path)

                destination = json_data['dest']
                destPath = common.basePath(destination)
                absoluteDest = os.path.join(self.parent._syncDir,
                                            destPath)
                try:
                    common.createLocalDirs(os.path.dirname(os.path.realpath(absoluteDest)))
                except:
                    # the file/folder is not accessible
                    pass
                else:

                    # Ignore this file in the watcher
                    self.parent.ignoreFiles.append(serverPath)
                    self.parent.ignoreFiles.append(destination)

                    try:
                        os.rename(absolutePath, absoluteDest)
                    except:
                        # again, paths arent accessible, so let the user handle it
                        pass

    def _on_error(self, ws, error):
        self.connected = False
        self.authenticated = False
        self.create_connection()

    def _on_close(self, ws):
        self.connected = False
        self.authenticated = False

    def _on_open(self, ws):
        self.connected = True

        # Get the user realtime_key from the SmartFile preferences
        # or generate one
        try:
            realtime_key = self.parent.api.get("/pref/user/sync.realtime-key/")
        except:
            generated_key = str(uuid.uuid4())
            auth_hash = hashlib.md5()
            auth_hash.update("%s" % (generated_key))
            realtime_key = auth_hash.hexdigest()
            self.parent.api.put("/pref/user/sync.realtime-key",
                    value=realtime_key)
        else:
            realtime_key = realtime_key['value']

        auth_data = {'authentication': realtime_key,
                     'uuid': self.auth_uuid}
        json_data = json.dumps(auth_data)

        # send the auth data to the server
        self.ws.send(json_data)

        self.authenticated = True

        # start the thread to process the queue of changes
        thread.start_new_thread(self._processSendQueue, ())
