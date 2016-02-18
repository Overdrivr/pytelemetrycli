# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from multiprocessing import Process, Queue, Pipe
import time, threading
from sortedcontainers import SortedDict
from enum import Enum

class PlotType(Enum):
    linear = 0,
    indexed = 1

class Superplot():
    """
Self-contained plotting class that runs in its own process.
Plotting functionality (reset the graph, .. ?) can be controlled
by issuing message-based commands using a multiprocessing Pipe

    """
    def __init__(self,name,plottype=PlotType.indexed):
        self.name = name
        self.plottype = plottype
        self._clear()

    def _clear(self):
        # Process-local buffers used to host the displayed data
        if self.plottype == PlotType.linear:
            self.set = True
            self.x = []
            self.y = []
        else:
            self.xy = SortedDict()
            # TODO : use this optimization, but for now raises issue
            # Can't pickle dict_key views ??
            #self.x = self.xy.keys()
            #self.y = self.xy.values()
            self.set = False

    def start(self):
        # The queue that will be used to transfer data from the main process
        # to the plot
        self.q = Queue()
        main_pipe, self.in_process_pipe = Pipe()
        self.p = Process(target=self.run)
        self.p.start()
        # Return a handle to the data queue and the control pipe
        return self.q, main_pipe

    def join(self):
        self.p.join()

    def _update(self):
        # Empty data queue and process received data
        while not self.q.empty():
            item = self.q.get()
            if self.plottype == PlotType.linear:
                self.x.append(item[0])
                self.y.append(item[1])
            else:
                # Seems pretty slow,
                # TODO : Profile
                # TODO : Eventually, need to find high performance alternative. Maybe numpy based
                self.xy[item[0]] = item[1]

        # Initialize view on data dictionnary only once for increased performance
        if not self.set:
            self.set = True
            self.x = self.xy.keys()
            self.y = self.xy.values()

        # Refresh plot data
        self.curve.setData(self.x,self.y)

        if self.in_process_pipe.poll():
            msg = self.in_process_pipe.recv()
            self._process_msg(msg)

    def _process_msg(self, msg):
        if msg == "exit":
            self.in_process_pipe.send("closing")
            self.app.quit()
        elif msg == "clear":
            self._clear()

    def run(self):
        self.app = QtGui.QApplication([])
        win = pg.GraphicsWindow(title="Basic plotting examples")
        win.resize(1000,600)
        win.setWindowTitle('pyqtgraph example: Plotting')
        plot = win.addPlot(title=self.name)
        self.curve = plot.plot(pen='y')

        timer = QtCore.QTimer()
        timer.timeout.connect(self._update)
        timer.start(50)

        self.app.exec_()
        self.in_process_pipe.send("closing")


if __name__ == '__main__':
    # This is function is responsible for faking some data (IO, serial port, etc)
    # and forwarding it to the display
    # it is run in a thread
    def io_linear(running,q):
        t = 0
        while running.is_set():
            for i in range(32):
                s = np.sin(2 * np.pi * t)
                q.put([t,s])
                t += 0.01
            time.sleep(0.0001)
        print("Done")

    # This is function is responsible for faking some data (IO, serial port, etc)
    # and forwarding it to the display
    # it is run in a thread
    def io_indexed(running,q):
        t = 0
        while running.is_set():
            t += 0.005
            for i in range(128):
                s = np.sin(2 * np.pi * t + i/10)
                q.put([i,s])
            time.sleep(0.01)
        print("Done")
    #To stop IO thread
    run = threading.Event()
    run.set()

    # create the plot
    s = Superplot("somePlot",PlotType.linear)
    #s = Superplot("somePlot",PlotType.indexed)

    # get the queue used to exchange data
    q, ctrlPipe = s.start()

    # start IO thread
    t = threading.Thread(target=io_linear, args=(run,q))
    #t = threading.Thread(target=io_indexed, args=(run,q))
    t.start()

    while True:
        action = input("Type 'q' to quit. Type 'clear' to reset the graph. Type 'exit' to close the graph but stay on main thread.")
        if action == 'clear':
            ctrlPipe.send('clear')
        elif action == 'exit':
            ctrlPipe.send('exit')
        elif action == 'q':
            break

    run.clear()
    print("Waiting for IO thread to join...")
    t.join()
    print("Waiting for graph window process to join...")
    s.join()
    print("Process joined successfully. C YA !")
