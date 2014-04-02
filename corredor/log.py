from mozlog.structured import reader
from transport import Socket

import json
import zmq

class DataStream(object):

    def __init__(self, location, context=None):
        self.socket = Socket(zmq.PULL, 'inproc', location, context=context)
        self.socket.connect()

    # mimic file-like object
    def readline(self):
        data = self.socket.recv_json()
        if data['action'] == 'fin':
            return ''
        return json.dumps(data)


def handle_data(action_map, location, context=None):
    stream = DataStream(location, context=context)
    reader.each_log(reader.read(stream), action_map)
    stream.socket.close()
