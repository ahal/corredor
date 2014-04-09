from mozlog.structured import reader

import json
import threading
import zmq

class DataStream(object):

    def __init__(self, context):
        self.socket = context.socket(zmq.PULL)
        self.socket.connect('inproc://corredor_data_stream')

    # mimic file-like object
    def readline(self):
        data = self.socket.recv_json()
        if data['action'] == 'fin':
            return ''
        return json.dumps(data)


class Handler(object):
    def __init__(self, action_map, num_workers, context=None):
        self.action_map = action_map
        self.num_workers = num_workers
        if self.num_workers:
            context = context or zmq.Context()
            self.socket = context.socket(zmq.PUSH)
            self.socket.bind('inproc://corredor_data_stream')
            for i in range(0, self.num_workers):
                thread = threading.Thread(target=worker_thread,
                                          args=(self.action_map,
                                                context))
                thread.daemon = True
                thread.start()

    def __call__(self, data):
        if self.num_workers:
            self.socket.send_json(data)
        else:
            self.action_map[data['action']](data)

    def cleanup(self):
        if self.num_workers:
            for i in range(0, self.num_workers):
                self.socket.send_json({'action': 'fin'})
            self.socket.close()


def worker_thread(action_map, context):
    stream = DataStream(context)
    reader.each_log(reader.read(stream), action_map)
    stream.socket.close()
