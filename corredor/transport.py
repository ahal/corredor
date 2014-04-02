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
    num_data_handlers = 1

    def __init__(self, socket_type, protocol, location, port=None):
        self.context = zmq.Context()
        self.socket = Socket(socket_type, protocol, location, port=port, context=self.context)
        self.socket.bind()

        # inter-thread socket used for handling received data
        self.handler = Socket(zmq.PUSH, 'inproc', '%s_data_stream' % location, context=self.context)
        self.handler.bind()

        self.action_map = {}

    def _start_data_handlers(self):
        for i in range(0, self.num_data_handlers):
            thread = threading.Thread(target=handler.handle_data,
                                      args=(self.action_map,
                                            self.handler._location,
                                            self.context))
            thread.daemon = True
            thread.start()

    def _stop_data_handlers(self):
        for i in range(0, self.num_data_handlers):
            self.handler.send_json({'action': 'fin'})

    def cleanup(self):
        self._stop_data_handlers()
        self.socket.cleanup()
        self.handler.cleanup()


class ExclusivePair(SocketPattern):

    def __init__(self, protocol, location, port=None):
        SocketPattern.__init__(self, zmq.PAIR, protocol, location, port=port)
        self._start_data_handlers()

    def register_callback(self, action, callback):
        self.action_map[action] = callback

    def send_json(self, data):
        self.socket.send_json(data)

    def recv_json(self):
        data = self.socket.recv_json()
        self.handler.send_json(data)
        return data


class Subscriber(SocketPattern):
    def __init__(self, protocol, location, port=None):
        SocketPattern.__init__(self, zmq.SUB, protocol, location, port=port)

    def subscribe(self, action, callback):
        self.action_map[action] = callback
        self.socket.setsockopt(zmq.SUBSCRIBE, action)

    def listen(self):
        self._start_data_handlers()

        action = None
        while action != 'fin':
            data = self.socket.recv_json()
            self.handler.send_json(data)
        self.cleanup()
