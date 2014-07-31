from StringIO import StringIO
import json
import unittest

from mozlog.structured import (
    structuredlog,
    handlers,
    formatters,
)
import zmq

from corredor.testing.output import StructuredLoggerBridge
from client import agent

class TestStructuredLoggerBridge(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.agent = agent.SocketAgent()

    def tearDown(self):
        self.agent.reset()

    def test_logs_processed(self):
        address = 'ipc://test_corredor_result_handler'
        buf = StringIO()

        logger = structuredlog.StructuredLogger('Result Handler Test')
        logger.add_handler(handlers.StreamHandler(buf, formatters.JSONFormatter()))

        result = StructuredLoggerBridge(address, logger)
        result.start_listening()

        self.agent.spawn_socket(zmq.PUB)
        self.agent[0].connect(address)

        messages = [
            { 'action': 'suite_start', 'tests': ['test_foo.py'] },
            { 'action': 'test_start', 'test': 'test_foo.py' },
            { 'action': 'test_status', 'test': 'test_foo.py', 'subtest': 'does it test?', 'status': 'PASS' },
            { 'action': 'test_end', 'test': 'test_foo.py', 'status': 'OK' },
            { 'action': 'suite_end' },
        ]

        for message in messages:
            self.agent[0].send(json.dumps(message))

        for i, recv in enumerate(buf.getvalue().splitlines()):
            recv = json.loads(recv)
            msg = messages[i]

            for key in msg.keys():
                self.assertEquals(recv[key], msg[key])

    def test_assert_structured_log(self):
        with self.assertRaises(TypeError):
            StructuredLoggerBridge('ipc://test', object())
