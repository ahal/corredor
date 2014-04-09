from collections import Iterable
from zmq.eventloop import ioloop

ioloop.install()

def poll(socket_patterns):
    if not isinstance(socket_patterns, Iterable):
        socket_patterns = (socket_patterns,)

    for sp in socket_patterns:
        sp.event_stream.on_recv(sp.on_recv)

    ioloop.IOLoop.instance().start()

def stop():
    ioloop.IOLoop.instance().stop()
