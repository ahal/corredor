from ..output import OutputHandler
from ..transport import ExclusivePair

import json
import time

class PingPong(object):

    def __init__(self):
        self.output = OutputHandler('ipc', '/tmp/corredor_worker_output')
        self.output.process_output()
        self.worker = ExclusivePair('ipc', '/tmp/corredor_exclusivepair')
        self.results = []
        def append_result(result):
            self.results.append(result)
        self.worker.register_callback('test_end', append_result)
    
    def synchronize(self, action):
        data = {}
        while data.get('action') != action:
            data = self.worker.recv_json()
        return data

    def send_test(self, test):
        self.worker.send_json({'action': 'test_start', 'test': test})
        self.synchronize('test_end')

    def finish(self):
        self.worker.send_json({'action': 'fin'})
        self.worker.cleanup()

        print 'Test results: %s' % json.dumps(self.results, indent=2)
        print 'stdout:\n%s' % ''.join(self.output.stdout)
        print 'stderr:\n%s' % ''.join(self.output.stderr)
