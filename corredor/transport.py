import json
import handler
import threading
import zmq

class Socket(object):

    def __init__(self, socket_type, protocol, location, port=None, context=None):
        if protocol in ('inproc', 'ipc') and port:
            raise Exception("%s protocol doesn't support ports!" % protocol)
        self._protocol = protocol
        self._location = location
        self._port = port
        self.address = None

        self.context = context or zmq.Context()
        self._socket = self.context.socket(socket_type)

    def connect(self):
        if self._protocol in ('tcp', 'udp') and not self._port:
            raise Exception("Must specify port for %s connections!" % self._protocol)

        conn_address = self._protocol + '://' + self._location

        if self._port:
            conn_address = conn_address + ':' + self._port
        self._socket.connect(conn_address)
        self.address = conn_address

    def bind(self):
        bind_address = '%s://%s' % (self._protocol, self._location)

        if self._port:
            bind_address = '%s:%s' % (bind_address, self._port)

        if self._protocol in ('tcp', 'udp') and not self._port:
            self._port = self._socket.bind_to_random_port(bind_address)
            bind_address = '%s:%s' % (bind_address, self._port)
        else:
            self._socket.bind(bind_address)
        self.address = bind_address

    def send_json(self, data):
        self._socket.send_string(data['action'], zmq.SNDMORE)
        self._socket.send_json(data)

    def recv_json(self):
        action, data = self._socket.recv_multipart()
        return json.loads(data)

    def setsockopt(self, option, value):
        self._socket.setsockopt(option, value)

    def cleanup(self):
        self._socket.close()
        self.context.destroy()


class SocketPattern(object):

    def __init__(self, socket_type, protocol, location, port=None, num_data_workers=1):
        self.context = zmq.Context()
        self.socket = Socket(socket_type, protocol, location, port=port, context=self.context)
        self.socket.bind()

        self.action_map = {}
        self.handler = handler.Handler(location, self.action_map, num_data_workers, self.context)

    def cleanup(self):
        self.socket.cleanup()
        self.handler.cleanup()


class ExclusivePair(SocketPattern):

    def __init__(self, protocol, location, port=None, **kwargs):
        SocketPattern.__init__(self, zmq.PAIR, protocol, location, port=port, **kwargs)

    def wait_for_action(self, action):
        data = {}
        while data.get('action') != action:
            data = self.recv_json()
        return data

    def register_action(self, action, callback):
        self.action_map[action] = callback

    def send_json(self, data):
        self.socket.send_json(data)

    def recv_json(self):
        data = self.socket.recv_json()
        self.handler(data)
        return data


class Subscriber(SocketPattern):
    def __init__(self, protocol, location, port=None):
        SocketPattern.__init__(self, zmq.SUB, protocol, location, port=port)

    def subscribe(self, action, callback):
        self.action_map[action] = callback
        self.socket.setsockopt(zmq.SUBSCRIBE, action)

    def listen(self):
        action = None
        while action != 'fin':
            data = self.socket.recv_json()
            self.handler(data)
        self.cleanup()
