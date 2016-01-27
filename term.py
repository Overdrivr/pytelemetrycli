import os
import sys
import cmd
import argparse
import runner
import topics
import pytelemetry.pytelemetry as tm
import pytelemetry.transports.serialtransport as transports

class Console(cmd.Cmd):

    def __init__(self):
        cmd.Cmd.__init__(self)

        self.transport = transports.SerialTransport()
        self.telemetry = tm.pytelemetry(self.transport)
        self.topics = topics.Topics(self.telemetry)
        self.runner = runner.Runner(self.transport,self.telemetry)

        self.completekey = None
        self.prompt = ">> "
        self.intro  = "pytelemetry terminal started."  ## defaults to None

    ## Command definitions ##
    def do_ls(self, args):
        """Prints a list of received topics"""
        t = self.topics.ls()
        for i in t:
            print(i)

    def do_print(self, args):
        """Prints X last received samples on a given topic"""

        parser = argparse.ArgumentParser()
        parser.add_argument('--topic','-t', dest='topic', required=True)
        parser.add_argument('--amount','-a', dest='amount', type=int, default=10)
        args = parser.parse_args(args.split())

        s = self.topics.samples(args.topic,args.amount)
        if s is not None:
            for i in s:
                print(i)

    def do_count(self, args):
        """Counts amount of received samples on a given topic"""

        parser = argparse.ArgumentParser()
        parser.add_argument('--topic','-t', dest='topic', required=True)
        args = parser.parse_args(args.split())

        s = self.topics.samples(args.topic,args.amount)
        for i in s:
            print(i)

    def do_exit(self, args):
        """Exits from the terminal"""
        return -1

    def do_connect(self,args):
        """Connect to a serial port"""
        # Parse args
        parser = argparse.ArgumentParser()
        parser.add_argument('--port','-p', dest='port', required=True)
        parser.add_argument('--baudrate','-b', dest='baudrate', type=int, default=9600)
        args = parser.parse_args(args.split())

        # Build the option dictionnary
        options = dict()
        options['port'] = args.port
        options['baudrate'] = args.baudrate

        try:
            self.runner.connect(options)
        except:
            print("Failed to connect to :",options['port']," at ",options['baudrate']," (bauds)")
            print("Connection error : ",sys.exc_info())
        else:
            print("Connected to :",options['port']," at ",options['baudrate']," (bauds)")

    def do_disconnect(self,args):
        self.runner.disconnect()
        print("Disconnected.")

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

        if args.type == 'float32':
            args.data = float(args.data)
        elif args.type != 'string':
            args.data = int(args.data)

        print("Published on |",args.topic,"|",args.data,"[",args.type,"]")

        self.telemetry.publish(args.topic,args.data,args.type)

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
        self.runner.terminate()

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
