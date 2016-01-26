import os
import sys
import cmd
import argparse
import runner
import pytelemetry.pytelemetry as tm
import pytelemetry.transports.serialtransport as transports

class Console(cmd.Cmd):

    def __init__(self):
        cmd.Cmd.__init__(self)

        self.mytransport = transports.SerialTransport()
        self.mytelemetry = tm.pytelemetry(self.mytransport)
        self.myrunner = runner.Runner(self.mytransport,self.mytelemetry)

        self.completekey = None
        self.prompt = ">> "
        self.intro  = "pytelemetry terminal started."  ## defaults to None

    ## Command definitions ##
    def do_ls(self, args):
        """Prints a list of received topics"""
        print(self._hist)

    def do_exit(self, args):
        """Exits from the terminal"""
        return -1

    def do_test(self,args):
        """Some tests"""
        parser = argparse.ArgumentParser(description='Test method')
        parser.add_argument('--port', dest='port')
        args = parser.parse_args(args.split())
        print(args.port)

    def do_connect(self,args):
        """Connect to a serial port"""
        # Parse args
        parser = argparse.ArgumentParser(description='Test method')
        parser.add_argument('--port', dest='port', required=True)
        parser.add_argument('--baudrate', dest='baudrate', type=int, default=9600)
        args = parser.parse_args(args.split())

        # Build the option dictionnary
        options = dict()
        options['port'] = args.port
        options['baudrate'] = args.baudrate

        try:
            self.myrunner.connect(options)
        except:
            print("Failed to connect to :",options['port']," at ",options['baudrate']," (bauds)")
            print("Connection error : ",sys.exc_info())
        else:
            print("Connected to :",options['port']," at ",options['baudrate']," (bauds)")

    def do_disconnect(self,args):
        self.myrunner.disconnect()
        print("Disconnected.")

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

    def postloop(self):
        """Take care of any unfinished business.
           Despite the claims in the Cmd documentaion, Cmd.postloop() is not a stub.
        """
        cmd.Cmd.postloop(self)   ## Clean up command completion
        self.myrunner.terminate()

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
