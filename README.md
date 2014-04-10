corredor
========

> Spanish, corredor *m*, noun 1. corridor, hall 2. runner 3. broker

Corredor is a framework designed for creating distributed test runners. It acts as a message broker
for communication across threads, processes or machines. Corredor does not know anything about test
runners itself, instead it provides the transport via ZeroMQ as well as some common strategies for splitting
up a test job.

It forces separation of test runners into two parts, a service and one or more workers. The service is written
in Python and is responsible for sending tests for the workers(s) to run. The workers can be
written in any language, and are what actually runs the tests. The service collects results and
output from the workers and forwards them on to the test harness.

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

Documentation
=============

Please [readthedocs](http://corredor.readthedocs.org/en/latest/index.html).
