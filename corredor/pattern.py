from handler import Handler
from zmq.eventloop import zmqstream

import json
import zmq

"""
A collection of atomic socket patterns. Each pattern corresponds to a single zmq socket type,
such as pair, pub/sub, req/rep, etc. The pattern provides a way to register callbacks for a
particular action. The callback can be processed either synchronously or asynchronously with
an arbitrary number of workers. The callbacks are also registered to tornado's ioloop for
quick polling.
"""

class SocketPattern(object):
    def __init__(self, socket_type, num_data_workers=0):
        """
        Base class for socket patterns. This should not be instanstiated directly.

        :param socket_type: the zmq socket type to create, e.g zmq.REP.
        :type socket_type: int.
        :param num_data_workers: number of worker threads used to handle callbacks,
                                 defaults to 0 which means callbacks are synchronous.
        :type num_data_workers: int.
        """

        self._address = None
        self.context = zmq.Context()
        self.socket = self.context.socket(socket_type)


        self.action_map = {}
        self.handler = Handler(self.action_map, num_data_workers)

        self.event_stream = zmqstream.ZMQStream(self.socket)

    @property
    def address(self):
        """
        Address the underlying socket is bound or connected to. Will raise zmq.ZMQError
        if accessed before a call to bind or connect.

        :raises: zmq.ZMQerror
        """
        if not hasattr(self, '_address'):
            raise zmq.ZMQError('Address not available, socket not bound or connected!')
        return self._address

    def bind(self, address):
        """
        Binds the underlying socket to address.

        :param address: Address to bind the socket to. Address is made up of a protocol,
                        location and port, e.g:
                        inproc://thread_location
                        ipc://process_location
                        tcp://127.0.0.1:5555
        :type address: str.
        """
                        
        self.socket.bind(address)
        self._address = address

    def connect(self, address):
        """
        Connects the underlying socket to address.

        :param address: Address to bind the socket to. Address is made up of a protocol,
                        location and port, e.g:
                        inproc://thread_location
                        ipc://process_location
                        tcp://127.0.0.1:5555
        :type address: str.
        """
        self.socket.connect(address)
        self._address = address

    def send_json(self, data):
        """
        Formats a dictonary as a JSON message and sends it over the connected or bound
        address.

        :param data: Dictionary to send. Must contain an 'action' key, otherwise a
                     KeyError is raised.
        :type data: dict.
        :raises KeyError:
        """
        self.socket.send_string(data['action'], zmq.SNDMORE)
        self.socket.send_json(data)

    def recv_json(self):
        """
        Receive a JSON message and pass it on to the dispatch function. This blocks
        until a message is received.
        """
        return self.on_recv(self.socket.recv_multipart())

    def on_recv(self, msg):
        """
        Take a message and pass the data on to the handler class.

        :param msg: A list of length two. The first item is an action string, the second
                    is the data string which is serialized to JSON.
        :type msg: list.
        """

        action, data = msg
        data = json.loads(data)
        self.handler(data)
        return action, data

    def cleanup(self):
        """
        Cleanup and destroy zmq context. This stop data handler threads processing
        further actions.
        """
        self.socket.close()
        self.handler.cleanup()
        self.context.destroy()


class ExclusivePair(SocketPattern):

    def __init__(self, *args, **kwargs):
        """
        Creates a zmq.PAIR socket which can only be connected to one other socket
        at a time.

        :param num_data_workers: number of worker threads used to handle callbacks,
                                 defaults to 0 which means callbacks are synchronous.
        :type num_data_workers: int.
        """
        SocketPattern.__init__(self, zmq.PAIR, *args, **kwargs)

    def wait_for_action(self, action):
        """
        Block until the specified action is received. Callbacks for other actions will
        still be processed, but the function will not return until the specified one.

        :param action: The action to wait for.
        :type action: str.
        """
        data = {}
        while data.get('action') != action:
            data = self.recv_json()
        return data

    def register_action(self, action, callback):
        """
        Register a callback for an action. Pre-existing callbacks are replaced.

        :param action: The action to register a callback for.
        :type action: str.
        :param callback: Callable invoked when the action is received.
        :type callback: callable.
        """
        self.action_map[action] = callback


class Subscriber(SocketPattern):
    def __init__(self, *args, **kwargs):
        """
        Creates a zmq.SUB socket which will only receive actions for which it has
        subscribed.

        :param num_data_workers: number of worker threads used to handle callbacks,
                                 defaults to 0 which means callbacks are synchronous.
        :type num_data_workers: int.
        """
        SocketPattern.__init__(self, zmq.SUB, *args, **kwargs)
        self.subscribe('fin')

    def subscribe(self, action, callback=None):
        """
        Blocks until 'fin' is received

        :param action: The action to subscribe to.
        :type action: str.
        :param callback: Callable invoked when the action is received.
        :type callback: callable.
        """
        if callback:
            self.action_map[action] = callback
        self.socket.setsockopt(zmq.SUBSCRIBE, action)

    def listen(self):
        """
        Listen for events until the 'fin' action is received. All subcribed actions
        are processed.
        """
        action = None
        while action != 'fin':
            action, data = self.recv_json()
        self.cleanup()
