.. corredor documentation master file, created by
   sphinx-quickstart on Wed Apr  2 22:35:51 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===================
Corredor for Python
===================

This is the documentation for the corredor python bindings.

Corredor is a framework for building distributed test harnesses using ZeroMQ.
There are generally two reasons you might want to consider using it:

A) To create bindings for your runner in different languages.
B) To inter-changeably distribute tests across threads, processes or machines.

While the initial development focus will be on testing, the scope may be
expanded to include more general use cases at a later time. In fact, there is
no reason it couldn't be used for other applications even now.

Installation
============

First `install pip`_, then run:

    $ pip install corredor

Corredor uses ZeroMQ as a transport, this means you'll need libzmq. Pyzmq will
attempt to compile it from source if it's not already installed. If that fails,
you may need to install libzmq manually. Luckily, there is a package for it in
most linux distros:

* Ubuntu/Debian   
    $ sudo apt-get install libzmq3-dev

* Fedora
    $ sudo yum install zeromq3-devel

* OSX
    $ sudo brew install zmq

If your OS isn't listed, or you'd like to install the latest version of zmq,
see the `official downloads page`_.


.. _`install pip`: http://www.pip-installer.org/en/latest/installing.html
.. _`official downloads page`: http://zeromq.org/intro:get-the-software

Contents
========

.. toctree::
 :maxdepth: 2

 pattern
 handler
 example 

Other Bindings
==============

This is the documentation for the Python corredor bindings. For other bindings,
see:

* `NodeJS`_

.. _`NodeJS`: http://corredor.readthedocs.org/projects/corredor-js/en/latest/


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

