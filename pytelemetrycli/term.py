import os
import sys
import cmd
import argparse
from ui import Plot
import numpy as np
from pyqtgraph.Qt import QtCore


    def do_plot(self, args):
        """
            Plots a topic in a PyQtGraph plot
        """
        

    def do_count(self, args):
        """Counts amount of received samples on a given topic"""

        parser = argparse.ArgumentParser()
        parser.add_argument('--topic','-t', dest='topic', required=True)
        args = parser.parse_args(args.split())

        s = self.topics.samples(args.topic,args.amount)
        for i in s:
            print(i)



    def do_pub(self,args):
        """Publish data on a topic"""
        # Parse args
        parser = argparse.ArgumentParser()
        parser.add_argument('--topic','-t', dest='topic', required=True)
        parser.add_argument('--data','-d', dest='data', required=True)
        parser.add_argument('--type', dest='type', required=True)

        try:
            args = parser.parse_args(args.split())
        except Exception as e:
            print("Error :",e)
            return

        valid_types = ['string','uint8','uint16','uint32','int8','int16','int32','float32']

        if not args.type in valid_types:
            print("Invalid type. Not in ",valid_types)
            return



    ## Command definitions to support Cmd object functionality ##
    def do_help(self, args):
        """Get help on commands
           'help' or '?' with no arguments prints a list of commands for which help is available
           'help <command>' or '? <command>' gives help on <command>
        """
        ## The only reason to define this method is for the help text in the doc string
        cmd.Cmd.do_help(self, args)

    ## Override methods in Cmd object ##
    def preloop(self):
        """Initialization before prompting user for commands.
           Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
        """
        cmd.Cmd.preloop(self)   ## sets up command completion
        self._hist    = []      ## No history yet
        self._locals  = {}      ## Initialize execution namespace for user
        self._globals = {}



    def precmd(self, line):
        """ This method is called after the line has been input but before
            it has been interpreted. If you want to modifdy the input line
            before execution (for example, variable substitution) do it here.
        """
        self._hist += [ line.strip() ]
        return line

    def postcmd(self, stop, line):
        """If you want to stop the console, return something that evaluates to true.
           If you want to do some post command processing, do it here.
        """
        return stop

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def default(self, line):
        """Called on an input line when the command prefix is not recognized.
           In that case we execute the line as Python code.
        """
        try:
            exec(line) in self._locals, self._globals
        except Exception as e:
            print(e.__class__, ":", e)

if __name__ == '__main__':
    console = Console()
    console . cmdloop()
