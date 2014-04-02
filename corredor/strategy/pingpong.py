from ..output import OutputHandler
from ..transport import ExclusivePair

import json
import time

class PingPong(object):

    def __init__(self):
        self.output = OutputHandler('ipc', '/tmp/corredor_worker_output')
        self.worker = ExclusivePair('ipc', '/tmp/corredor_exclusivepair')
        self.results = []

    def send_tests(self, tests):
        def append_result(result):
            self.results.append(result)
        self.worker.register_callback('test_end', append_result)
        self.worker.wait_ready()
        self.output.process_output()

        for test in tests:
            time.sleep(1) # simulate some processing
            self.worker.send_json({'action': 'test_start', 'test': test})
            self.worker.recv_json()

        self.worker.send_json({'action': 'fin'})
        self.worker.cleanup()

        print 'Test results: %s' % json.dumps(self.results, indent=2)
        print ''.join(self.output.stdout)
        print ''.join(self.output.stderr)