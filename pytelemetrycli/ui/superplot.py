# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from multiprocessing import Process, Manager, Queue
import sched, time, threading

# This function is responsible for displaying the data
# it is run in its own process to liberate main process
class Superplot():
    def __init__(self,name):
        self.name = name
        # Process-local buffers used to host the displayed data
        self.x = []
        self.y = []

    def start(self):
        self.q = Queue()
        self.p = Process(target=self.run)
        self.p.start()
        return self.q

    def join(self):
        self.p.join()

    def _update(self):
        item = self.q.get()
        self.x.append(item[0])
        self.y.append(item[1])
        self.curve.setData(self.x,self.y)

    def run(self):
        app = QtGui.QApplication([])

        win = pg.GraphicsWindow(title="Basic plotting examples")
        win.resize(1000,600)
        win.setWindowTitle('pyqtgraph example: Plotting')
        plot = win.addPlot(title=self.name)
        self.curve = plot.plot(pen='y')

        timer = QtCore.QTimer()
        timer.timeout.connect(self._update)
        timer.start(50)

        app.exec_()
# This is function is responsible for reading some data (IO, serial port, etc)
# and forwarding it to the display
# it is run in a thread
def io(running,q):
    t = 0
    while running.is_set():
        s = np.sin(2 * np.pi * t)
        t += 0.01
        q.put([t,s])
        time.sleep(0.01)
    print("Done")

if __name__ == '__main__':
    #To stop IO thread
    run = threading.Event()
    run.set()

    # create the plot
    s = Superplot("somePlot")
    # get the queue used to exchange data
    q = s.start()

    # start IO thread
    t = threading.Thread(target=io, args=(run,q))
    t.start()


    input("Type Enter to quit.")
    run.clear()
    print("Waiting for IO thread to join...")
    t.join()
    print("Waiting for graph window process to join...")
    s.join()
    print("Process joined successfully. C YA !")
