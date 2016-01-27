import threading
import time

# Main class
class Runner:
    def __init__(self, transport, telemetry):

        self.transport = transport
        self.telemetryWrapper = telemetry

        self.running = threading.Event()
        self.running.set()

        self.connected = threading.Event()
        self.connected.clear()

    def connect(self,options):
        self.transport.connect(options)
        self.connected.set()
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def disconnect(self):
        self.connected.clear()
        self.transport.disconnect()

    def terminate(self):
        self.running.clear()
        self.thread.join()
        try:
            self.transport.disconnect()
        except:
            pass # Already disconnected

    def run(self):
        while self.running.is_set():
            if self.connected.is_set():
                self.telemetryWrapper.update()
            else:
                time.sleep(0.5)
