import json
import zmq

class BaseTransport(object):

    def __init__(self, protocol, location, port=None):
        if protocol in ('inproc', 'ipc') and port:
            raise Exception("%s protocol doesn't support ports!" % protocol)

        self.context = zmq.Context()
        self._protocol = protocol
        self._location = location
        self._port = port
        self.address = None
        self.callbacks = {}

    def bind(self):
        bind_address = '%s://%s' % (self._protocol, self._location)

        if self._port:
            bind_address = '%s:%s' % (bind_address, self._port)

        if self._protocol in ('tcp', 'udp') and not self._port:
            self._port = self.socket.bind_to_random_port(bind_address)
            bind_address = '%s:%s' % (bind_address, self._port)
        else: 
            self.socket.bind(bind_address)
        self.address = bind_address

    def send_json(self, data):
        message = [data['action'], json.dumps(data)]
        self.socket.send_multipart(message)

    def recv_json(self):
        action, data = self.socket.recv_multipart()
        data = json.loads(data)
        if action in self.callbacks:
            self.callbacks[action](data)
        return data

    def cleanup(self):
        self.socket.close()
        self.context.destroy()


class ExclusivePair(BaseTransport):

    def __init__(self, protocol, location, port=None):
        BaseTransport.__init__(self, protocol, location, port=port)

        self.socket = self.context.socket(zmq.PAIR)
        self.bind()

        self.ready = False
        def on_ready(data):
            self.ready = True
        self.register_callback('ready', on_ready)

    def wait_ready(self):
        print 'waiting for ready...'
        while not self.ready:
            self.recv_json()
        print 'ok.'

    def register_callback(self, action, callback):
        self.callbacks[action] = callback
    

class Subscriber(BaseTransport):

    def __init__(self, protocol, location, port=None):
        BaseTransport.__init__(self, protocol, location, port=port)
        
        self.socket = self.context.socket(zmq.SUB)
        self.bind()
        self.callbacks = {}

    def subscribe(self, action, callback):
        self.callbacks[action] = callback
        self.socket.setsockopt(zmq.SUBSCRIBE, action)

    def listen(self):
        action = None
        while action != 'fin':
            action, data = self.recv_json()
        self.cleanup()
