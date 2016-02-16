import runner
from pytelemetry.pytelemetry import Pytelemetry
import pytelemetry.transports.serialtransport as transports
import time

transport = transports.SerialTransport()
telemetry = Pytelemetry(transport)
app = runner.Runner(transport,telemetry)

def printer(topic, data, options):
    if options:
        print(topic,'[',options['index'],"] : ", data)
    else:
        print(topic," : ", data)
options = dict()
port = "COM20"
bauds = 115200

app.connect(port,bauds)

print("Connected.")

telemetry.subscribe(None, printer)
telemetry.publish('bar',1354,'int32')
time.sleep(3)

app.terminate()
print("Done.")
