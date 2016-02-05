#!/usr/bin/env python
import sys
import cmd
from docopt import docopt, DocoptExit
import pytelemetry.pytelemetry as tm
import pytelemetry.transports.serialtransport as transports
import topics
import runner
from serial.tools import list_ports

def docopt_cmd(func):
    def fn(self, arg):
        try:
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
        self.telemetry = tm.pytelemetry(self.transport)
        self.topics = topics.Topics()
        self.runner = runner.Runner(self.transport,self.telemetry)
        self.telemetry.subscribe(None,self.topics.process)

    @docopt_cmd
    def do_serial(self, arg):
        """
Connects pytelemetry to the serial port.

Usage: serial <port> [options]

Options:
-b X, --bauds X        Connection speed in bauds  [default: 9600]

        """
        print(arg)

    @docopt_cmd
    def do_print(self, arg):
        """
Prints X last received samples from <topic>.

Usage: print <topic> [options]

Options:
-a X, --amount X        Amount of samples to display [default: 1]

        """
        print(arg)

    @docopt_cmd
    def do_ls(self, arg):
        """
By default, prints a list of all received topics.
With the --serial flag, prints a list of all available COM ports

Usage: ls [options]

Options:
-s, --serial     Use this flag to print a list of all available serial ports

        """
        print(arg)
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
        print(arg)

    @docopt_cmd
    def do_pub(self, arg):
        """
Publishes a (value | string) on <topic>.

Usage: pub <topic> <value> (-ui8 | -ui16 | -ui32 | -i8 | -i16 | -i32 | -f32 | -s)
        """
        print(arg)

    @docopt_cmd
    def do_disconnect(self, arg):
        """
Disconnects from any open connection.

Usage: disconnect
        """
        print(arg)

    def do_quit(self, arg):
        """
Quits out of Interactive Mode.
        """

        print('Good Bye!')
        exit()

try:
    Application().cmdloop()
except SystemExit:
    pass
except KeyboardInterrupt:
    pass
