#!/usr/bin/env python
import sys
import cmd
from docopt import docopt, DocoptExit


def docopt_cmd(func):
    """
    This decorator is used to simplify the try/except block and pass the result
    of the docopt parsing to the called action.
    """
    def fn(self, arg):
        try:
            opt = docopt(fn.__doc__, arg)

        except DocoptExit as e:
            # The DocoptExit is thrown when the args do not match.
            # We print a message to the user and the usage block.

            print('Invalid Command!')
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


class MyInteractive (cmd.Cmd):
    intro = 'pytelemetry terminal started.' \
          + ' (type help for a list of commands.)'
    prompt = ':> '
    file = None

    @docopt_cmd
    def do_serial(self, arg):
        """
            Usage: serial <port> [options]

            Options:
            -b X, --bauds X        Connection speed in bauds  [default: 9600]
        """

        print(arg)

    def do_quit(self, arg):
        """
            Quits out of Interactive Mode.
        """

        print('Good Bye!')
        exit()


try:
    MyInteractive().cmdloop()
except SystemExit:
    pass
except KeyboardInterrupt:
    pass
