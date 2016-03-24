#!/usr/bin/env python
import sys
import cmd
from docopt import docopt, DocoptExit
from pytelemetry import Pytelemetry
import pytelemetry.transports.serialtransport as transports
from pytelemetrycli.topics import Topics
from pytelemetrycli.runner import Runner
from pytelemetrycli.tools import isclose
from serial.tools import list_ports
from serial import SerialTimeoutException
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
    def __init__(self, transport=None, stdout=None):
        # cmd Initialization and configuration
        cmd.Cmd.__init__(self,stdout=stdout)
        self.intro = 'pytelemetry terminal started.' \
                 + ' (type help for a list of commands.)'
        self.prompt = ':> '
        self.file = None

        # pytelemetry setup
        if not transport:
            self.transport = transports.SerialTransport()
        else:
            self.transport = transport
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
List serial ports or connect to one of them.

Usage: serial ((-l | --list) | <port> [options])

Options:
-b X, --bauds X         Connection speed in bauds  [default: 9600]
        """
        if arg['--list'] or arg['-l']:
            self.stdout.write("Available COM ports:\n")
            for port,desc,hid in list_ports.comports():
                self.stdout.write("%s \t %s\n" % (port,desc))
            return

        try:
            self.runner.disconnect()
            logger.warn("User requested connect without desconnecting first.")
        except (IOError,AttributeError) as e:
            logger.warn("Already disconnected. Continuing happily. E : {0}"
                         .format(e))
            pass

        self.topics.clear()
        logger.info("Cleared all topics for new session.")

        self.transport.resetStats(averaging_window=10)
        self.runner.resetStats()
        self.telemetry.resetStats()
        logger.info("Cleared all stats for new session.")

        try:
            b = int(arg['--bauds'])
            self.runner.connect(arg['<port>'],b)
        except IOError as e:
            self.stdout.write("Failed to connect to {0} at {1} (bauds).\n"
                    .format(arg['<port>'],b))

            logger.warn("Failed to connect to {0} at {1} (bauds). E : \n"
                          .format(arg['<port>'],b,e))
        else:
            s = "Connected to {0} at {1} (bauds).\n".format(arg['<port>'],b)
            self.stdout.write(s)
            logger.info(s)

    @docopt_cmd
    def do_print(self, arg):
        """
Prints X last received samples from <topic>.

Usage: print <topic> [options]

Options:
-a, --all        Display all received samples under <topic>
-l X, --limit X  Display X last received samples under <topic> [default: 1]

        """
        topic = arg['<topic>']
        if not self.topics.exists(topic):
            s = "Topic '{0}' unknown. Type 'ls' to list all available topics.\n".format(topic)
            self.stdout.write(s)
            logger.warn(s)
            return

        try:
            if arg['--all']:
                amount = 0 # 0 is understood as 'return all samples' by self.topics.samples()
            else:
                amount = int(arg['--limit'])
        except:
            s = "Could not cast --limit = '{0}' to integer. Using 1.\n".format(arg['--limit'])
            self.stdout.write(s)
            logger.warn(s)
            amount = 1

        s = self.topics.samples(topic,amount)

        if s is not None:
            for i in s:
                self.stdout.write("{0}\n".format(i))
        else:
            logger.error("Could not retrieve {0} sample(s) under topic '{1}'.\n".format(amount,topic))

    @docopt_cmd
    def do_ls(self, arg):
        """
Prints available topics. Topics are basically labels under which data is available (for display, plot, etc).
Data can come from remote source (a connected embedded device) or the command-line interface itself (reception speed, etc).

Without flags, prints a list of remote topics.

Usage: ls [options]

Options:
-c, --cli       Prints all CLI topics. Use this to display topics for monitoring reception speed, errors amount, etc.
        """
        if arg['--cli']:
            for topic in self.topics.ls(source='cli'):
                self.stdout.write("%s\n" % topic)
            return

        for topic in self.topics.ls(source='remote'):
            self.stdout.write("%s\n" % topic)


    @docopt_cmd
    def do_plot(self, arg):
        """
Plots <topic> in a graph window.

Usage: plot <topic>
        """

        topic = arg['<topic>']

        if not self.topics.exists(topic):
            s = "Topic '{0}' unknown. Type 'ls' to list all available topics.\n".format(topic)
            self.stdout.write(s)
            logger.warn(s)
            return

        if self.topics.intransfer(topic):
            s = "Topic '{0}' already plotting.\n".format(topic)
            self.stdout.write(s)
            logger.warn(s)
            return

        has_indexes = self.topics.has_indexed_data(arg['<topic>'])

        if has_indexes:
            plotType = PlotType.indexed
            transferType = "indexed"
        else:
            plotType = PlotType.linear
            transferType = "linear"

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

        self.topics.transfer(topic,q, transfer_type=transferType)

        s = "Plotting '{0}' in mode [{1}].\n".format(topic,transferType)
        logger.info(s)
        self.stdout.write(s)

    @docopt_cmd
    def do_pub(self, arg):
        """
Publishes a (value | string) on <topic>.

Usage: pub (--u8 | --u16 | --u32 | --i8 | --i16 | --i32 | --f32 | --s) <topic> <value>
        """

        if arg['--f32']:
            arg['<value>'] = float(arg['<value>'])
        elif not arg['--s']:
            try:
                arg['<value>'] = int(arg['<value>'])
            except:
                # User most likely entered a float with an integer flag
                inter = float(arg['<value>'])
                rounded = int(inter)

                if isclose(inter,rounded):
                    arg['<value>'] = rounded
                else:
                    s = "Aborted : Wrote decimal number ({0}) with integer flag.".format(arg['<value>'])
                    self.stdout.write(s + "\n")
                    logger.warning(s)
                    return


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

        try:
            self.telemetry.publish(arg['<topic>'],arg['<value>'],valtype)
        except SerialTimeoutException as e:
            self.stdout.write("Pub failed. Connection most likely terminated.")
            logger.error("Pub failed. Connection most likely terminated. exception : %s" % e)
            return
        except AttributeError as e:
            self.stdout.write("Pub failed because you are not connected to any device. Connect first using `serial` command.")
            logger.warning("Trying to publish while not connected. exception : %s" % e)
            return

        s = "Published on topic '{0}' : {1} [{2}]".format(arg['<topic>'], arg['<value>'],valtype)
        self.stdout.write(s + "\n")
        logger.info(s)

    @docopt_cmd
    def do_count(self, arg):
        """
Prints a count of received samples for each topic.

Usage: count
        """
        for topic in self.topics.ls():
            self.stdout.write("{0} : {1}\n".format(topic, self.topics.count(topic)))

    @docopt_cmd
    def do_disconnect(self, arg):
        """
Disconnects from any open connection.

Usage: disconnect
        """
        try:
            self.runner.disconnect()
            self.stdout.write("Disconnected.\n")
            logger.info("Disconnected.")

            measures = self.transport.stats()

            for key,item in measures.items():
                logger.info("Raw IO : %s : %s" % (key,item))

            measures = self.runner.stats()

            for key,item in measures.items():
                logger.info("IO speeds : %s : %s" % (key,item))

            measures = self.telemetry.stats()

            for key,item in measures['framing'].items():
                logger.info("Framing : %s : %s" % (key,item))

            for key,item in measures['protocol'].items():
                logger.info("Protocol : %s : %s" % (key,item))

            logger.info("Logged session statistics.")


        except:
            logger.warn("Already disconnected. Continuing happily.")

    @docopt_cmd
    def do_info(self, arg):
        """
Prints out cli.py full path, module version.

Usage: info
        """
        self.stdout.write("- CLI path : %s\n" % os.path.dirname(os.path.realpath(__file__)))
        try:
            self.stdout.write("- version : %s\n" % __version__)
        except:
            self.stdout.write("- version : not found.\n")

    @docopt_cmd
    def do_stats(self, arg):
        """
Displays different metrics about the active transport (ex : serial port).
This allows you to know if for instance corrupted frames are received, what fraction
of the maximum baudrate is being used, etc.

Usage: stats
        """
        measures = self.transport.stats()

        self.stdout.write("Raw IO:\n")
        for key,item in measures.items():
            self.stdout.write("\t%s : %s\n" % (key,item))

        measures = self.runner.stats()

        self.stdout.write("IO speeds:\n")
        for key,item in measures.items():
            self.stdout.write("\t%s : %s\n" % (key,item))

        measures = self.telemetry.stats()

        self.stdout.write("Framing:\n")
        for key,item in measures['framing'].items():
            self.stdout.write("\t%s : %s\n" % (key,item))

        self.stdout.write("Protocol:\n")
        for key,item in measures['protocol'].items():
            self.stdout.write("\t%s : %s\n" % (key,item))

    def do_quit(self, arg):
        """
Exits the terminal application.

Usage: quit
        """
        self.runner.terminate()
        self.do_disconnect("")
        self.stdout.write("Good Bye!\n")
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
