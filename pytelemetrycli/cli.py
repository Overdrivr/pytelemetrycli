#!/usr/bin/env python
import sys
import cmd
from docopt import docopt, DocoptExit

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
    intro = 'pytelemetry terminal started.' \
          + ' (type help for a list of commands.)'
    prompt = ':> '
    file = None

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
Prints a list of all received topics.

Usage: ls
        """
        print(arg)

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
