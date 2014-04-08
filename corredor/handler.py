from mozlog.structured import reader

import json
import threading
import transport
import zmq

class DataStream(object):

    def __init__(self, location, context=None):
        self.socket = transport.Socket(zmq.PULL, 'inproc', location, context=context)
        self.socket.connect()

    # mimic file-like object
    def readline(self):
        data = self.socket.recv_json()
        if data['action'] == 'fin':
            return ''
        return json.dumps(data)



class Handler(object):
    def __init__(self, location, action_map, num_workers, context=None):
        self.num_workers = num_workers
        if self.num_workers:
            self.socket = transport.Socket(zmq.PUSH, 'inproc', '%s_data_stream' % location, context=context)
            self.socket.bind()
            for i in range(0, self.num_workers):
                thread = threading.Thread(target=worker_thread,
                                          args=(action_map,
                                                self.socket._location,
                                                context))
                thread.daemon = True
                thread.start()

    def __call__(self, data):
        if self.num_workers:
            self.socket.send_json(data)
        else:
            return self.action_map[data['action']](data)

    def cleanup(self):
        if self.num_workers:
            for i in range(0, self.num_workers):
                self.handler.send_json({'action': 'fin'})
            self.socket.cleanup()


def worker_thread(action_map, location, context=None):
    stream = DataStream(location, context=context)
    reader.each_log(reader.read(stream), action_map)
    stream.socket.close()
