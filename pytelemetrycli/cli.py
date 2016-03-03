#!/usr/bin/env python
import sys
import cmd
from docopt import docopt, DocoptExit
from pytelemetry import Pytelemetry
import pytelemetry.transports.serialtransport as transports
from pytelemetrycli.topics import Topics
from pytelemetrycli.runner import Runner
from serial.tools import list_ports
from pytelemetrycli.ui.superplot import Superplot, PlotType
from threading import Lock
from pytelemetrycli.initialization import init_logging
import logging
from logging import getLogger
import os

logger = getLogger('cli')

def docopt_cmd(func):
    def fn(self, arg):
        try:
            if fn.__name__ == "do_pub":
                # Fix for negative numbers
                opt = docopt(fn.__doc__, arg, options_first=True)
            else:
                opt = docopt(fn.__doc__, arg)

        except DocoptExit as e:
            print('Command is invalid. See :')
            print(e)
            return

        except SystemExit:
            # The SystemExit exception prints the usage for --help
            # We do not need to do the print here.
            return

        return func(self, opt)

    fn.__name__ = func.__name__
    fn.__doc__ = func.__doc__
    fn.__dict__.update(func.__dict__)
    return fn

class Application (cmd.Cmd):
    def __init__(self):
        # cmd Initialization and configuration
        cmd.Cmd.__init__(self)
        self.intro = 'pytelemetry terminal started.' \
                 + ' (type help for a list of commands.)'
        self.prompt = ':> '
        self.file = None

        # pytelemetry setup
        self.transport = transports.SerialTransport()
        self.telemetry = Pytelemetry(self.transport)
        self.topics = Topics()
        self.plots = []
        self.plotsLock = Lock()
        self.runner = Runner(self.transport,
                             self.telemetry,
                             self.plots,
                             self.plotsLock,
                             self.topics)
        self.telemetry.subscribe(None,self.topics.process)

        self.types_lookup = {'--s'    :  'string',
                             '--u8'   :  'uint8',
                             '--u16'  :  'uint16',
                             '--u32'  :  'uint32',
                             '--i8'   :  'int8',
                             '--i16'  :  'int16',
                             '--i32'  :  'int32',
                             '--f32'  :  'float32'}
        logger.info("Module path : %s" % os.path.dirname(os.path.realpath(__file__)))
        try:
            logger.info("Module version : %s" % __version__)
        except:
            logger.warning("Module version : not found.")

    @docopt_cmd
    def do_serial(self, arg):
        """
Connects pytelemetry to the serial port.

Usage: serial <port> [options]

Options:
-b X, --bauds X        Connection speed in bauds  [default: 9600]

        """
        try:
            self.runner.disconnect()
            logger.warn("User requested connect without desconnecting first.")
        except (IOError,AttributeError) as e:
            logger.warn("Already disconnected. Continuing happily. E : {0}"
                         .format(e))
            pass

        try:
            b = int(arg['--bauds'])
            self.runner.connect(arg['<port>'],b)
        except IOError as e:
            print("Failed to connect to {0} at {1} (bauds)."
                    .format(arg['<port>'],b))

            logger.warn("Failed to connect to {0} at {1} (bauds). E : "
                          .format(arg['<port>'],b,e))
        else:
            s = "Connected to {0} at {1} (bauds).".format(arg['<port>'],b)
            print(s)
            logger.info(s)

    @docopt_cmd
    def do_print(self, arg):
        """
Prints X last received samples from <topic>.

Usage: print <topic> [options]

Options:
-a X, --amount X        Amount of samples to display [default: 1]

        """
        topic = arg['<topic>']
        if not self.topics.exists(topic):
            s = "Topic '{0}' unknown. Type 'ls' to list all available topics.".format(topic)
            print(s)
            logger.warn(s)
            return

        try:
            amount = int(arg['--amount'])
        except:
            s = "Could not cast --amount = '{0}' to integer. Using 1.".format(amount)
            print(s)
            logger.warn(s)
            amount = 1

        s = self.topics.samples(topic,amount)

        if s is not None:
            for i in s:
                print(i)
        else:
            logger.error("Could not retrieve {0} sample(s) under topic '{1}'.".format(amount,topic))

    @docopt_cmd
    def do_ls(self, arg):
        """
Without options, prints a list of all received topics.
With the --serial flag, prints a list of all available COM ports

Usage: ls [options]

Options:
-s, --serial     Use this flag to print a list of all available serial ports

        """
        if arg['--serial']:
            print("Available COM ports:")
            for port,desc,hid in list_ports.comports():
                print(port,'\t',desc)
        else:
            for topic in self.topics.ls():
                print(topic)

    @docopt_cmd
    def do_plot(self, arg):
        """
Plots <topic> in a graph window.

Usage: plot <topic>
        """

        topic = arg['<topic>']

        if not self.topics.exists(topic):
            s = "Topic '{0}' unknown. Type 'ls' to list all available topics.".format(topic)
            print(s)
            logger.warn(s)
            return

        if self.topics.intransfer(topic):
            s = "Topic '{0}' already plotting.".format(topic)
            print(s)
            logger.warn(s)
            return

        plotTypeFlag = self.topics.xytype(arg['<topic>'])
        plotType = PlotType.linear

        if plotTypeFlag == 'indexed':
            plotType = PlotType.indexed

        p = Superplot(topic,plotType)
        q, ctrl = p.start()

        # Protect self.plots from modifications from the runner thread
        self.plotsLock.acquire()

        self.plots.append({
            'topic': topic,
            'plot': p,     # Plot handler
            'queue': q,    # Data queue
            'ctrl': ctrl   # Plot control pipe
        })

        self.plotsLock.release()

        self.topics.transfer(topic,q)

        s = "Plotting '{0}' in mode [{1}].".format(topic,plotTypeFlag)
        logger.info(s)
        print(s)

    @docopt_cmd
    def do_pub(self, arg):
        """
Publishes a (value | string) on <topic>.

Usage: pub (--u8 | --u16 | --u32 | --i8 | --i16 | --i32 | --f32 | --s) <topic> <value>
        """

        if arg['--f32']:
            arg['<value>'] = float(arg['<value>'])
        elif not arg['--s']:
            arg['<value>'] = int(arg['<value>'])

        subset = {k: arg[k] for k in ("--u8","--u16","--u32","--i8","--i16","--i32","--f32","--s")}

        valtype = None
        for i, k in subset.items():
            if k:
                valtype = self.types_lookup[i]

        if not valtype:
            logger.error(
                "Payload type [{0}] unkown."
                .format(arg))
            return

        self.telemetry.publish(arg['<topic>'],arg['<value>'],valtype)

        s = "Published on topic '{0}' : {1} [{2}]".format(arg['<topic>'], arg['<value>'],valtype)
        print(s)
        logger.info(s)

    @docopt_cmd
    def do_count(self, arg):
        """
Prints a count of received samples for each topic.

Usage: count
        """
        for topic in self.topics.ls():
            print("{0} : {1}".format(topic, self.topics.count(topic)))

    @docopt_cmd
    def do_disconnect(self, arg):
        """
Disconnects from any open connection.

Usage: disconnect
        """
        try:
            self.runner.disconnect()
            print("Disconnected.")
            logger.info("Disconnected.")
        except:
            logger.warn("Already disconnected. Continuing happily.")

    @docopt_cmd
    def do_info(self, arg):
        """
Disconnects from any open connection.

Usage: info
        """
        print("- CLI path : %s" % os.path.dirname(os.path.realpath(__file__)))
        try:
            print("- version : %s" % __version__)
        except:
            print("- version : not found.")

    def do_quit(self, arg):
        """
Exits the terminal application.

Usage: quit
        """
        self.runner.terminate()
        print("Good Bye!")
        logger.info("Application quit.")
        exit()

# Main function to start from script or from entry point
def pytlm():
    init_logging()
    try:
        Application().cmdloop()
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    pytlm()
