corredor
========

> Spanish, corredor *m*, noun 1. corridor, hall 2. runner 3. broker

[![Build Status](https://travis-ci.org/ahal/corredor.png?branch=master)](https://travis-ci.org/ahal/corredor)

Corredor is a framework designed for creating distributed test runners and other distributed applications. It
acts as a message broker for communication across threads, processes or machines. Corredor does not know anything
about test runners itself, instead it provides the transport via ZeroMQ as well as some handy abstractions and
leaves it up to the test harness creator to do the rest.

Documentation
=============

Please [readthedocs](http://corredor.readthedocs.org/en/latest/index.html) for more information.


Installation
============

Corredor uses ZeroMQ for the transport. To install zmq:

    # Ubuntu/Debian
    $ sudo apt-get install libzmq3-dev
    
    # Fedora
    $ sudo yum install zeromq3-devel
    
    # OSX
    $ sudo brew install zmq

To install the Python bindings, first [install pip](http://www.pip-installer.org/en/latest/installing.html), then:

    $ pip install corredor

Testing
=======

To run all unittests:

    $ python setup.py test
