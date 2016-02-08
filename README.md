## pytelemetry command line interface

This tool enables superior communication with any embedded device.

This command line interface is for you if:

* you are using `printf` to debug your application (and looking for a better way)
* you are all the time re-writing custom protocols on top of the serial port for each new application (and hating it)
* you need a **reliable** and **error-tolerant** communication protocol for your application, that will run both on desktop and embedded
* you need to finely tune your application, but so far you are compiling/flashing the code all over again after each parameter change
* you want to **plot** parameters of your application in **real-time** in a clean, fast and reliable way
* your embedded device has very limited resources and will tolerate only a fast and lightweight communication library
* you have found some other communication protocol but cannot manage to integrate it on your specific device

If you recognize yourself with any of the above points, this application is for you.

## Overview
pytelemetry-cli is a **command line interface**. It provides a set of commands to connect to a device, read, plot and write data on it.
pytelemetry-cli relies on [`pytelemetry`](https://github.com/Overdrivr/pytelemetry)
[![PyPI version](https://badge.fury.io/py/pytelemetry.svg)](https://badge.fury.io/py/pytelemetry)
to implement the specific communication protocol.

The communication protocol is also available in a C library called [`telemetry`](https://github.com/Overdrivr/pytelemetry)
 that is specifically designed to run on all platforms and to be as light as possible.

![Overview](https://raw.githubusercontent.com/Overdrivr/pytelemetrycli/master/overview.png)

## Principle
The underlying communication protocol mostly follows the [PubSub](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)(publish/subscribe) messaging pattern.

> [..] messages are published to "topics" or named logical channels. Subscribers in a topic-based system will receive all messages published to
> the topics to which they subscribe [..].
> *Source: Wikipedia*

## Installation
`pytelemetrycli` requires python 3.5+, PyQt4 and numpy.

### Windows
It is recommended to download [`numpy`](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy) and [`PyQt4`](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4) wheels python packages (courtesy of Christoph Gohlke).

In case you were wondering, **no** you **don't** have to install Qt. The binary wheel is enough.

Then install with pip the downloaded files

```bash
pip install numpy-x.xx.x+vanilla-cp3x-none-winxxx.whl
pip install PyQt4-x.xx.x-cp3x-none-winxxx.whl
```

Then, install `pytelemetrycli` from the pypi repository

```bash
pip install pytelemetrycli
```

### Mac OS
The easiest way to install numpy and PyQt4 seem to be using `homebrew`.

```bash
brew install pyqt
pip install pytelemetrycli
```

### Linux

?

## Telemetry on embedded devices
To setup telemetry on any embedded device, please refer to the [`Telemetry`](https://github.com/Overdrivr/Telemetry) repository.

If you only wish to test the command-line interface, you can also directly flash a test firmware from our own [collection](#)
*Note: in process. In the future we will support a variety of devices so you can quickly start on with the command line.*

## List of commands
The command line interface can be started like this
```
python -m pytelemetrycli.cli
```

### help [command]
Without arguments, you get a list of all available commands. Otherwise the full `command` documentation.

### ls
```bash
Without options, prints a list of all received topics.
With the --serial flag, prints a list of all available COM ports

Usage: ls [options]

Options:
-s, --serial     Use this flag to print a list of all available serial ports
```

### serial
```bash
Connects pytelemetry to the serial port.

Usage: serial <port> [options]

Options:
-b X, --bauds X        Connection speed in bauds  [default: 9600]
```

### print
```bash
Prints X last received samples from <topic>.

Usage: print <topic> [options]

Options:
-a X, --amount X        Amount of samples to display [default: 1]
```

### pub
```bash
Publishes a (value | string) on <topic>.

Usage: pub <topic> <value> (--u8 | --u16 | --u32 | --i8 | --i16 | --i32 | --f32 | --s)
```

### plot
```bash
Plots <topic> in a graph window.

Usage: plot <topic>
```

### disconnect
```bash
Disconnects from any open connection.

Usage: disconnect
```

### quit
```bash
Exits the terminal application.

Usage: quit
```
