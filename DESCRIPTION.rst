Pytelemetry Command Line Interface
====================================

This module is a powerful command line interface for extremely fast debugging and communication with embedded systems.

It allows for plotting embedded device's data on-the-fly, publishing values on any topics, listing serial ports and much more.

The CLI relies on custom protocol, implemented in Python and C languages.
The main strength of this protocol is strong decoupling between communicating devices, simplicity yet flexibility.

For instance, the protocol supports sending standard linear data, but also arrays and sparse arrays in a network-friendly manner.

-  `Project page <https://github.com/Overdrivr/pytelemetrycli>`__

.. image:: https://raw.githubusercontent.com/Overdrivr/pytelemetrycli/master/console.png

.. image:: https://raw.githubusercontent.com/Overdrivr/pytelemetrycli/master/graph.png

pytelemetry
============

This module is the Python implementation of the communication protocol.

It can be used directly (without the CLI) to script communications with an embedded device.

.. code:: python

    from pytelemetry import Pytelemetry
    from pytelemetry.transports.serialtransport import SerialTransport
    import time

    transport = SerialTransport()
    tlm = Pytelemetry(transport)
    transport.connect({port:'com9',baudrate:'9600'})

    # publish once on topic 'throttle' (a named communication channel)
    tlm.publish('throttle',0.8,'float32')

    def printer(topic, data, opts):
        print(topic," : ", data)

    # Subscribe a `printer` function called on every frame with topic 'feedback'.
    tlm.subscribe("feedback", printer)

    # Update during 3 seconds
    timeout = time.time() + 3
    while True:
        tlm.update()
        if time.time() > timeout:
            break

    # disconnect
    transport.disconnect()
    print("Done.")

Language C implementation
=========================

Telemetry is the same protocol implemented in C language.

-  `Project page <https://github.com/Overdrivr/Telemetry>`__

Centralized documentation
=========================

The documentation for all three projects is centralized `here <https://github.com/Overdrivr/Telemetry/wiki>`_.

MIT License, (C) 2015-2016 Rémi Bèges (remi.beges@gmail.com)
