from ..base import BaseTestStrategy
from ..transport import ExclusivePair, Subscriber

import threading
import time

class PingPong(BaseTestStrategy):

    def __init__(self):
        BaseTestStrategy.__init__(self)
        self.worker = ExclusivePair('ipc', '/tmp/corredor_exclusivepair')

    def run_tests(self, tests):
        def append_result(result):
            self.results.append(result)
        self.worker.register_callback('test_end', append_result)
        self.worker.wait_ready()
        self.process_output()

        for test in tests:
            time.sleep(1) # simulate some processing
            self.worker.send_json({'action': 'test_start', 'test': test})
            self.worker.recv_json()

        self.worker.send_json({'action': 'fin'})
        import json
        print 'Test results: %s' % json.dumps(self.results, indent=2)
        print ''.join(self.stdout)
        print ''.join(self.stderr)

        self.worker.cleanup()
