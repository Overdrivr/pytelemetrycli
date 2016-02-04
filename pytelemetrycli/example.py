import runner
import pytelemetry.pytelemetry as tm
import pytelemetry.transports.serialtransport as transports
import time

transport = transports.SerialTransport()
telemetry = tm.pytelemetry(transport)
app = runner.Runner(transport,telemetry)

def printer(topic, data):
    print(topic," : ", data)

options = dict()
options['port'] = "COM20"
options['baudrate'] = 9600

app.connect(options)

telemetry.subscribe("variable", printer)
telemetry.publish('variable ',1354,'int32')
time.sleep(3)

app.terminate()
print("Done.")
