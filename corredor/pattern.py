from .handler import Handler
from zmq.eventloop import zmqstream

import json
import zmq


class SocketPattern(object):
    def __init__(self, socket_type, num_data_workers=0):
        self._address = None
        self.context = zmq.Context()
        self.socket = self.context.socket(socket_type)


        self.action_map = {}
        self.handler = Handler(self.action_map, num_data_workers)

        self.event_stream = zmqstream.ZMQStream(self.socket)

    @property
    def address(self):
        if not hasattr(self, '_address'):
            raise zmq.ZMQError('Address not available, socket not bound or connected!')
        return self._address

    def bind(self, address):
        self.socket.bind(address)
        self._address = address

    def connect(self, address):
        self.socket.connect(address)
        self._address = address

    def send_json(self, data):
        self.socket.send_string(data['action'], zmq.SNDMORE)
        self.socket.send_json(data)

    def recv_json(self):
        return self.on_recv(self.socket.recv_multipart())

    def on_recv(self, msg):
        action, data = msg
        data = json.loads(data)
        self.handler(data)
        return action, data

    def cleanup(self):
        self.socket.close()
        self.handler.cleanup()
        self.context.destroy()


class ExclusivePair(SocketPattern):

    def __init__(self, *args, **kwargs):
        SocketPattern.__init__(self, zmq.PAIR, *args, **kwargs)

    def wait_for_action(self, action):
        data = {}
        while data.get('action') != action:
            data = self.recv_json()
        return data

    def register_action(self, action, callback):
        self.action_map[action] = callback


class Subscriber(SocketPattern):
    def __init__(self, *args, **kwargs):
        SocketPattern.__init__(self, zmq.SUB, *args, **kwargs)

    def subscribe(self, action, callback=None):
        if callback:
            self.action_map[action] = callback
        self.socket.setsockopt(zmq.SUBSCRIBE, action)

    def listen(self):
        action = None
        while action != 'fin':
            action, data = self.recv_json()
        self.cleanup()
