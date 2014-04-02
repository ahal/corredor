import json
import zmq

class Socket(object):

    def __init__(self, socket_type, protocol, location, port=None):
        if protocol in ('inproc', 'ipc') and port:
            raise Exception("%s protocol doesn't support ports!" % protocol)
        self._protocol = protocol
        self._location = location
        self._port = port
        self.address = None
        self.callbacks = {}

        self.context = zmq.Context()
        self._socket = self.context.socket(socket_type)

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
        message = [data['action'], json.dumps(data)]
        self._socket.send_multipart(message)

    def recv_json(self):
        action, data = self._socket.recv_multipart()
        data = json.loads(data)
        if action in self.callbacks:
            self.callbacks[action](data)
        return data

    def setsockopt(self, option, value):
        self._socket.setsockopt(option, value)

    def cleanup(self):
        self._socket.close()
        self.context.destroy()


class ExclusivePair(object):

    def __init__(self, protocol, location, port=None):
        self.socket = Socket(zmq.PAIR, protocol, location, port=port)
        self.socket.bind()

        self.ready = False
        def on_ready(data):
            self.ready = True
        self.register_callback('ready', on_ready)

    def wait_ready(self):
        print 'waiting for ready...'
        while not self.ready:
            self.socket.recv_json()
        print 'ok.'

    def register_callback(self, action, callback):
        self.socket.callbacks[action] = callback

    def send_json(self, data):
        self.socket.send_json(data)

    def recv_json(self):
        return self.socket.recv_json()

    def cleanup(self):
        self.socket.cleanup()
    

class Subscriber(object):

    def __init__(self, protocol, location, port=None):
        self.socket = Socket(zmq.SUB, protocol, location, port=port)
        self.socket.bind()

    def subscribe(self, action, callback):
        self.socket.callbacks[action] = callback
        self.socket.setsockopt(zmq.SUBSCRIBE, action)

    def listen(self):
        action = None
        while action != 'fin':
            action, data = self.socket.recv_json()
        self.cleanup()

    def cleanup(self):
        self.socket.cleanup()
