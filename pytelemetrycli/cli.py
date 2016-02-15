#!/usr/bin/env python
import sys
import cmd
from docopt import docopt, DocoptExit
from pytelemetry.pytelemetry import Pytelemetry
import pytelemetry.transports.serialtransport as transports
from pytelemetrycli.topics import Topics
from pytelemetrycli.runner import Runner
from serial.tools import list_ports
from pytelemetrycli.ui.superplot import Superplot

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
        self.telemetry = Pytelemetry(self.transport)
        self.topics = Topics()
        self.runner = Runner(self.transport,self.telemetry)
        self.telemetry.subscribe(None,self.topics.process)

        self.types_lookup = {'--s'    :  'string',
                             '--u8'   :  'uint8',
                             '--u16'  :  'uint16',
                             '--u32'  :  'uint32',
                             '--i8'   :  'int8',
                             '--i16'  :  'int16',
                             '--i32'  :  'int32',
                             '--f32'  :  'float32'}

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
        except:
            pass # Already disconnected
        try:
            b = int(arg['--bauds'])
            self.runner.connect(arg['<port>'],b)
        except:
            print("Failed to connect to :",arg['<port>']," at ",b," (bauds)")
            print("Connection error : ",sys.exc_info())
        else:
            print("Connected to :",arg['<port>']," at ",b," (bauds)")

    @docopt_cmd
    def do_print(self, arg):
        """
Prints X last received samples from <topic>.

Usage: print <topic> [options]

Options:
-a X, --amount X        Amount of samples to display [default: 1]

        """
        if not self.topics.exists(arg['<topic>']):
            print("Topic '",arg['<topic>'],"' unknown. Type 'ls' to list all available")
            return

        s = self.topics.samples(arg['<topic>'],int(arg['--amount']))
        if s is not None:
            for i in s:
                print(i)

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
        if not self.topics.exists(arg['<topic>']):
            print("Topic ",arg['<topic>']," unknown.")

        self.myplot = Superplot(arg['<topic>'])
        q = self.myplot.start()
        self.topics.transfer(arg['<topic>'],q)

        print("Plotting:", arg['<topic>'])

    @docopt_cmd
    def do_pub(self, arg):
        """
Publishes a (value | string) on <topic>.

Usage: pub <topic> <value> (--u8 | --u16 | --u32 | --i8 | --i16 | --i32 | --f32 | --s)
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
            print("Impossible to identify type of payload. pub cancelled.")
            print(arg)
            return

        print("Published on |",arg['<topic>'],"|",arg['<value>'],"[",valtype,"]")

        self.telemetry.publish(arg['<topic>'],arg['<value>'],valtype)

    @docopt_cmd
    def do_count(self, arg):
        """
Prints a count of received samples for each topic.

Usage: count
        """
        for topic in self.topics.ls():
            print(topic,":",self.topics.count(topic))

    @docopt_cmd
    def do_disconnect(self, arg):
        """
Disconnects from any open connection.

Usage: disconnect
        """
        try:
            self.runner.disconnect()
            print("Disconnected.")
        except:
            print("Already disconnected.")

    def do_quit(self, arg):
        """
Exits the terminal application.

Usage: quit
        """
        self.runner.terminate()
        print('Good Bye!')
        exit()

# Main function to start from script or from entry point
def pytlm():
    try:
        Application().cmdloop()
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    pytlm()
