Socket Patterns
===============

A socket pattern represents a common way of sharing data. Each pattern roughly maps to a
`ZeroMQ socket type`_. Patterns wrap the ZeroMQ socket to ensure the proper message format
is always used. They also provide a mechanism for handling events, and can spawn any
number of asynchronous event handlers if desired (event handling is synchronous by
default).

Corredor provides higher level API's for common operations (e.g result collection), but
applications may still use socket patterns directly. They may want to do this if the use
case is simple or highly customized.

.. _`ZeroMQ socket type`: http://api.zeromq.org/2-1:zmq-socket

ExclusivePair
-------------

The ExclusivePair pattern maps to zmq's `PAIR sockets`_. Exclusive pairs must only
connect or bind to one other PAIR socket. They may send and receive data bi-directionally
and in any order. That is, they may call send/recv multiple times in a row.

.. _`PAIR sockets`: http://api.zeromq.org/2-1:zmq-socket#toc14

.. autoclass:: corredor.pattern.ExclusivePair
    :members:
    :inherited-members:

Subscriber
----------

The Subscriber pattern maps to zmq's `SUB sockets`_. Subscribers must first subscribe to
an action before receiving events for it. Subscribers may connect to as many publishers
as they wish. Alternatively subscribers can bind and have publishers connect to it.
Subscribers may not send data.

.. _`SUB sockets`: http://api.zeromq.org/2-1:zmq-socket#toc10

.. autoclass:: corredor.pattern.Subscriber
    :members:
    :inherited-members:

SocketPattern
-------------

The base class for all other socket patterns. Applications should not instantiate
directly. It is only exposed in the event application specific socket patterns are
desired.
