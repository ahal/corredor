import json
import os
import subprocess
import sys
import threading
import time
import zmq

from application import run_application

here = os.path.abspath(os.path.dirname(__file__))

class SocketTimeoutException(Exception):
    """Raised on socket timeout."""

class SocketAgent(object):
    _address = None
    processes = []
    sockets_dict = {}
    sockets_list = []

    def __init__(self, timeout=1):
        self.context = zmq.Context()
        self.controller = self.context.socket(zmq.ROUTER)
        self.controller.bind('ipc://test_agent_controller')
        self.set_timeout(timeout)

    def __getitem__(self, attr):
        if isinstance(attr, basestring):
            self._address = self.sockets_dict[attr]
        else:
            self._address = self.sockets_list[attr]
        return self

    def set_timeout(self, timeout):
        self.controller.RCVTIMEO = timeout * 1000

    def reset(self):
        for address in self.sockets_list + self.sockets_dict.values():
            self.controller.send_multipart([address, '', json.dumps({'action': 'fin'})])

        time.sleep(1)
        for proc in self.processes:
            proc.kill()

        self.sockets_list = []
        self.sockets_dict = {}


    def _recv(self):
        try:
            address, empty, data = self.controller.recv_multipart()
        except:
            raise SocketTimeoutException("timed out waiting for reply")
        data = json.loads(data)
        assert data['action'] == 'ok'
        return address, empty, data

    def _send(self, cmd):
        self.controller.send_multipart([self._address, '', json.dumps(cmd)])
        return self._recv()

    def _spawn_socket(self, socket_type):
        p = subprocess.Popen(['python', os.path.join(here, 'application.py'), str(socket_type)])
        self.processes.append(p)
        address, empty, msg = self._recv()
        return address

    def spawn_socket(self, socket_type):
        self.sockets_list.append(self._spawn_socket(socket_type))

    def spawn_named_socket(self, name, socket_type):
        self.sockets_dict[name] = self._spawn_socket(socket_type)
        self.sockets_dict[name] = address

    def bind(self, address):
        self._send({'action': 'bind', 'address': address})
    
    def connect(self, address):
        self._send({'action': 'connect', 'address': address})
    
    def send(self, msg):
        self._send({'action': 'send', 'payload': msg})

    def recv(self):
        return json.loads(self._send({'action': 'recv'})[2]['payload'])
