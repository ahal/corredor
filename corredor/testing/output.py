import threading

from mozlog.structured.structuredlog import StructuredLogger

from ..pattern import Subscriber

STRUCTURED_ACTIONS = [
  'suite_start',
  'suite_end',
  'test_start',
  'test_end',
  'test_status',
  'process_output',
  'log',
]

class StructuredLoggerBridge(object):
    """
    Class that connects to a socket streaming messages with
    the structured log protocol and forwards them to a
    StructuredLogger instance.
    """

    def __init__(self, address, logger):
        if not isinstance(logger, StructuredLogger):
            raise TypeError("Must pass in a StructuredLogger instance")

        self.address = address
        self.logger = logger
        self.ready = threading.Event()

    def _run(self):
        sub = Subscriber()
        sub.bind(self.address)

        for action in STRUCTURED_ACTIONS:
            sub.subscribe(action, self.logger.log_raw)

        self.ready.set()
        sub.listen()

    def start_listening(self):
        thread = threading.Thread(target=self._run)
        thread.daemon = True
        thread.start()

        self.ready.wait(10)
