.. corredor documentation master file, created by
   sphinx-quickstart on Wed Apr  2 22:35:51 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========
Corredor
========

    Spanish, corredor *m*, noun 1. corridor, hall 2. runner 3. broker

Corredor is a framework for building distributed test harnesses using ZeroMQ.
There are generally two reasons you might want to consider using it:

A) To create bindings for your runner in different languages.
B) To inter-changeably distribute tests across threads, processes or machines.

While the initial development focus will be on testing, the scope may be
expanded to include more general use cases at a later time. In fact, there is
no reason it couldn't be used for other applications even now.

Bindings
========

Corredor works across languages, provided there are bindings that know how to
speak the protocol. Currently there are bindings in both Python and NodeJS.

* :doc:`Python <python/index>`
* `NodeJS`_

.. _`NodeJS`: http://corredor.readthedocs.org/projects/corredor-js/en/latest/


Installation
============

libzmq
~~~~~~
If installing the python bindings, pyzmq will attempt to compile libzmq from source.
But if that doesn't work, or you wish to use only the NodeJS bindings, you'll need
to install it manually. Luckily there are packages for many operating systems:

* Ubuntu/Debian
    $ sudo apt-get install libzmq3-dev

* Fedora
    $ sudo yum install zeromq3-devel

* OSX
    $ sudo brew install zmq

If your OS isn't listed, or you'd like to install the latest version of zmq,
see the `official downloads page`_.


Python bindings
~~~~~~~~~~~~~~~

To install the Python bindings, first `install pip`_, then run:

    $ pip install corredor


NodeJS bindings
~~~~~~~~~~~~~~~

To install the NodeJS bindings, you'll first need to manually install libzmq
(see above). After that, run:

    $ npm install corredor-js


.. _`official downloads page`: http://zeromq.org/intro:get-the-software
.. _`install pip`: http://www.pip-installer.org/en/latest/installing.html

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

