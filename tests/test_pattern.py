import corredor
import json
import threading
import time
import unittest
import zmq

from client import agent

class TestSocketPattern(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.agent = agent.SocketAgent()

    def tearDown(self):
        self.agent.reset()

    def test_exclusive_pair(self):
        address = 'ipc://test_corredor_exclusive_pair'

        pair = corredor.ExclusivePair()
        pair.bind(address)
        
        self.agent.spawn_socket(zmq.PAIR)
        self.agent[0].connect(address)

        data = {'action': 'foo', 'thingy': 'bar'}

        # test recv
        self.agent[0].send(json.dumps(data))
        msg = pair.recv_json()[1]
        self.assertEquals(data, msg)

        # test send
        pair.send_json(data)
        msg = self.agent[0].recv()
        self.assertEquals(data, msg)

        # trying to connect a second socket doesn't work
        self.agent.spawn_socket(zmq.PAIR)
        self.agent[1].connect(address)
        
        pair.send_json(data)
        self.assertRaises(agent.SocketTimeoutException, self.agent[1].recv)

        pair.cleanup()

    def test_subscriber(self):
        address = 'ipc://test_corredor_subscriber'
        output = []

        context = zmq.Context()
        signal = context.socket(zmq.PULL)
        signal.bind('inproc://test_subscriber')
        signal.RCVTIMEO = 100 # milliseconds

        def _sub_listen():
            sub = corredor.Subscriber()
            sub.bind(address)

            # make sure sub is listening
            sync = context.socket(zmq.PUSH)
            sync.connect('inproc://test_subscriber')
            def on_sync(data):
                sync.send_string('ok')
            sub.subscribe('sync', on_sync)

            def on_recv(data):
                output.append(data['action'])
            sub.subscribe('foo', on_recv)
            sub.subscribe('baz', on_recv)
            sub.subscribe('fleem', on_recv)

            
            sub.listen()
            sub.cleanup()

        thread = threading.Thread(target=_sub_listen)
        thread.daemon = True
        thread.start()

        self.agent.spawn_socket(zmq.PUB)
        self.agent[0].connect(address)
        
        # sub needs to be listening before pub messages are sent
        ready = False
        while not ready:
            try:
                self.agent[0].send(json.dumps({'action': 'sync'}))
                ready = signal.recv_string()
            except KeyboardInterrupt:
                sys.exit(1)
            except:
                pass

        messages = ['foo', 'bar', 'baz']
        expected = []
        for i in range(0, 9):
            if messages[i % 3] != 'bar':
                expected.append(messages[i % 3])
            self.agent[0].send(json.dumps({'action': messages[i % 3]}))

        self.agent[0].send(json.dumps({'action': 'fin'}))
        self.assertEquals(output, expected)
