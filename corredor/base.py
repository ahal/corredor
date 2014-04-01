from abc import ABCMeta, abstractmethod
from transport import Subscriber

import threading

class BaseTestStrategy(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.results = []
        self.stdout = []
        self.stderr = []
    
    @abstractmethod
    def run_tests(self, tests):
        pass

    def process_output(self, on_stdout=None, on_stderr=None):
        def store_stdout(data):
            self.stdout.append(data['message'])
        def store_stderr(data):
            self.stderr.append(data['message'])

        def _process_output():
            sub = Subscriber('ipc', '/tmp/corredor_worker_output')
            sub.subscribe('stdout', on_stdout or store_stdout)
            sub.subscribe('stderr', on_stderr or store_stderr)
            sub.listen()
        
        output_thread = threading.Thread(target=_process_output)
        output_thread.daemon = True
        output_thread.start()
