import json
import sys
import zmq

class SocketApplication(object):
    
    def __init__(self, socket_type):
        self.context = zmq.Context()
        self.socket = self.context.socket(socket_type)

        self.receiver = self.context.socket(zmq.REQ)
        self.receiver.connect('ipc://test_agent_controller')

    def on_fin(self, data):
        self.socket.close()
        self.context.destroy()

    def on_bind(self, data):
        self.socket.bind(data['address'])

    def on_connect(self, data):
        self.socket.connect(data['address'])

    def on_send(self, data):
        data = json.loads(data['payload'])
        self.socket.send_string(data['action'], zmq.SNDMORE)
        self.socket.send_json(data)

    def on_recv(self, data):
        action, data = self.socket.recv_multipart()
        return {'payload': data}


def run_application(socket_type):
    app = SocketApplication(socket_type)
    data = {}
    response = {'action': 'ok'}
    while data.get('action') != 'fin':
        app.receiver.send_json(response)
        data = app.receiver.recv_json()
        func = 'on_%s' % data['action']
        assert hasattr(app, func)
        response = getattr(app, func)(data) or {}
        response['action'] = 'ok'

if __name__ == '__main__':
    run_application(int(sys.argv[1]))
