import hashlib
from Queue import Queue
import ssl
import thread
import threading
import time
import uuid

import websocket
try:
    import simplejson as json
except ImportError:  # pragma: no cover
    import json

import events


class RealtimeMessages(threading.Thread):
    def __init__(self, api, on_moved=None, on_created=None,
                 on_deleted=None, on_modified=None):
        self.api = api

        self.on_moved = on_moved
        self.on_created = on_created
        self.on_deleted = on_deleted
        self.on_modified = on_modified

        self.websocket_address = "wss://www.kissync.com/sync"

        # The default auth data is blank
        self.auth_data = {}

        # Generate a unique authentication UUID for this client
        hash = hashlib.sha1()
        hash.update(str(time.time()))
        self.auth_uuid = hash.hexdigest()[:10]

        # Queue for offline messages
        self.offline_queue = Queue()

        self.connected = False
        self.authenticated = False

        super(RealtimeMessages, self).__init__()

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

    def update(self, event):
        """ Send an event to the websocket. """
        send_data = {'event_type': event.__class__.__name__,
                'path': event.path}
        if hasattr(event, 'src'):
            destination = {'src': event.src}
            send_data.update(destination)
        if hasattr(event, 'isDir'):
            isDir = {'isDir': event.isDir}
            send_data.update(isDir)

        return self._sendChanges(send_data)

    def _sendChanges(self, changes):
        """ Prepares data to be sent to the websocket. """
        # Prepare the dictionary to send
        send_data = {}
        send_data.update(self.auth_data)
        send_data.update(changes)
        data = json.dumps(send_data)

        # Check if the websocket is available
        if self.connected and self.authenticated:
            # send the json encoded message
            return self.ws.send(data)
        else:
            # process the message when the websocket is available
            self.offline_queue.put(data)

    def _processSendQueue(self, *args):
        """
        Send changes that occured when the client was offline to the realtime
        sync server.
        """
        while True:
            while self.connected and self.authenticated:
                # This blocks until it gets a task
                task = self.offline_queue.get()
                if self.connected is False or self.authenticated is False:
                    break
                self.ws.send(task)
                self.offline_queue.task_done()
            time.sleep(.01)

    def _on_message(self, ws, message):
        """ Reads messages from the websocket. """
        json_data = json.loads(message)

        if 'event_type' in json_data:
            try:
                if json_data['uuid'] == self.auth_uuid:
                    return
            except KeyError:
                return
            message_type = json_data['event_type']
            if message_type == 'LocalMovedEvent':
                # Remote moved event
                path = json_data['path']
                src = json_data['src']
                moved_event = events.RemoteMovedEvent(src, path)
                if self.on_moved is not None:
                    self.on_moved(moved_event)
            elif message_type == 'LocalCreatedEvent':
                # Remote created event
                path = json_data['path']
                isDir = json_data['isDir']
                created_event = events.RemoteCreatedEvent(path, isDir)
                if self.on_created is not None:
                    self.on_created(created_event)
            elif message_type == 'LocalDeletedEvent':
                # Remote deleted event
                path = json_data['path']
                deleted_event = events.RemoteDeletedEvent(path)
                if self.on_deleted is not None:
                    self.on_deleted(deleted_event)
            elif message_type == 'LocalModifiedEvent':
                # Remote modified event
                path = json_data['path']
                modified_event = events.RemoteModifiedEvent(path)
                if self.on_modified is not None:
                    self.on_modified(modified_event)

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
            response = self.api.get("/pref/user/sync.realtime-key/")
            realtime_key = response['value']
        except:
            generated_key = str(uuid.uuid4())
            auth_hash = hashlib.md5()
            auth_hash.update("%s" % (generated_key))
            realtime_key = auth_hash.hexdigest()

            # Store the  generated key on SmartFile in user preferences
            self.api.put("/pref/user/sync.realtime-key",
                         value=realtime_key)

        self.auth_data = {'authentication': realtime_key,
                          'uuid': self.auth_uuid}
        json_data = json.dumps(self.auth_data)

        # send the auth data directly to the server
        self.ws.send(json_data)

        self.authenticated = True

        # start the thread to process the queue of changes
        thread.start_new_thread(self._processSendQueue, ())
