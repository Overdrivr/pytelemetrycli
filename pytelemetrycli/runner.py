import threading
import time

# Main class
class Runner:
    def __init__(self, transport, telemetry, plots, plotsLock, topics):

        self.transport = transport
        self.telemetryWrapper = telemetry
        self.plots = plots
        self.plotsLock = plotsLock
        self.topics = topics

        self.thread = None
        self.running = threading.Event()
        self.running.set()

        self.connected = threading.Event()
        self.connected.clear()

        self.resetStats()

    def connect(self,port,bauds):
        # Create monitoring topics
        self.topics.create("baudspeed",source="cli")
        self.topics.create("baudspeed_avg",source="cli")

        # Connection options
        options = dict()
        options['port'] = port
        options['baudrate'] = bauds

        self.baudrate = bauds
        self.transport.connect(options)
        self.connected.set()
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def disconnect(self):
        self.connected.clear()
        self.transport.disconnect()

    def terminate(self):
        self.running.clear()
        if self.thread:
            self.thread.join()
        try:
            self.transport.disconnect()
        except:
            pass # Already disconnected

    def stats(self):
        return {
            "baudspeed" : self.baudspeed,
            "baudspeed_avg" : self.baudspeed_avg,
            "baudratio" : self.baudspeed / self.baudrate,
            "baudratio_avg" : self.baudspeed_avg / self.baudrate
        }

    def resetStats(self):
        self.baudrate = 1.0
        self.baudspeed = 0.0
        self.lasttime = time.time()
        self.lastamount = 0.0
        self.baudspeed_avg = 0.0

    def update(self):
        # Update protocol decoding
        self.telemetryWrapper.update()

        # Protect the self.plots data structure from
        # being modified from the main thread
        self.plotsLock.acquire()

        # Update baudspeed value
        current = time.time()
        difft = current - self.lasttime

        if difft > 0.05 :
            self.lasttime = current

            current = self.transport.stats()['rx_bytes']
            diff = current - self.lastamount
            self.lastamount = current

            self.baudspeed = diff / difft

            # Compute rolling average baud speed on about 1 second window
            n = 20
            self.baudspeed_avg = (self.baudspeed + n * self.baudspeed_avg) / (n + 1)

            # Send cli system data to the topics so that they can be plotted.
            self.topics.process("baudspeed",self.baudspeed)
            self.topics.process("baudspeed_avg",self.baudspeed_avg)

        # Poll each poll pipe to see if user closed them
        plotToDelete = None
        for p, i in zip(self.plots,range(len(self.plots))):
            if p['ctrl'].poll():
                if p['ctrl'].recv() == "closing":
                    plotToDelete = i
                    break

        # Delete a plot if needed
        if plotToDelete is not None:
            self.plots[plotToDelete]['ctrl'].close()
            topic = self.plots[plotToDelete]['topic']
            self.topics.untransfer(topic)
            self.plots.pop(plotToDelete)

        self.plotsLock.release()

    def run(self):
        while self.running.is_set():
            if self.connected.is_set():
                self.update()
            else:
                time.sleep(0.5)
