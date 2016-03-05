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

    def connect(self,port,bauds):
        options = dict()
        options['port'] = port
        options['baudrate'] = bauds
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

    def update(self):
        # Update protocol decoding
        self.telemetryWrapper.update()

        # Protect the self.plots data structure from
        # being modified from the main thread
        self.plotsLock.acquire()

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
