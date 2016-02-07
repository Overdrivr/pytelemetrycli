## pytelemetry command line interface

This tool enables superior communication with any embedded device.

This command line interface is for you if:

* you are using `printf` to debug your application (and looking for a better way)
* you are all the time re-writing custom protocols on top of the serial port for each new application (and hating it)
* you need a *reliable* and *error-tolerant* communication protocol for your application, that will run both on desktop and embedded
* you need to finely tune your application, but so far you are compiling/flashing the code all over again after each parameter change
* you want to *plot* parameters of your application in *real-time* in a clean, fast and reliable way
* your embedded device has very limited resources and will tolerate only a fast and lightweight communication library
* you have found some other communication protocol but cannot manage to integrate it on your specific device

If you recognize yourself with any of the above points, this application is for you.

## Overview
pytelemetry-cli (this repo) is a **command line interface**. It provides a set of commands to connect to a device, read, plot and write data on it.
pytelemetry-cli relies on `[pytelemetry](https://github.com/Overdrivr/pytelemetry)`
[![PyPI version](https://badge.fury.io/py/pytelemetry.svg)](https://badge.fury.io/py/pytelemetry)
to implement the specific communication protocol.

The communication protocol is also available in a C library called `[telemetry](https://github.com/Overdrivr/pytelemetry))`
 that is specifically designed to run on all platforms and to be as light as possible.

![Overview](https://raw.githubusercontent.com/Overdrivr/pytelemetrycli/master/overview.png)

Explain pubsub/topics
## List of commands
Start the command line interface with
```
python -m pytelemetrycli.cli
```
To get detailed description of a command directly from the terminal
help
help command
List of commands
#### serial

#### ls

#### print

#### plot

#### pub


## Installation
pytelemetrycli requires python 3.5+, PyQt4 and numpy.

Then (To be done)
```bash
pip install pytelemetrycli
```
