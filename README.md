## pytelemetry command line interface

This tool enables superior communication with an embedded device.

This command line interface is for you if:

* you are using `printf` to debug your application (and looking for a better way)
* you need to finely tune your application, but so far you need to compile/flash the code all over again after each parameter change
* you want to plot parameters of your application in real-time in a clean, fast and reliable way
* you need a decent and reliable communication protocol for your application, that will run both on desktop and embedded
* your embedded device has very limited resources and will tolerate only a fast and lightweight communication library

If you agree with any of the above points, this application is for you.

## Overview
pytelemetry-cli (this repo) is a command line interface. It provides a set of commands to connect to a device, read, plot and write data on it.
pytelemetry-cli relies on the [pytelemetry](https://github.com/Overdrivr/pytelemetry) package
 [![PyPI version](https://badge.fury.io/py/pytelemetry.svg)](https://badge.fury.io/py/pytelemetry) to implement the specific communication protocol.

The communication protocol is also available in a C library ([telemetry](https://github.com/Overdrivr/pytelemetry)), specifically designed to run on all platforms and be as light as possible.

![Overview](https://github.com/Overdrivr/pytelemetrycli/overview.png)

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
