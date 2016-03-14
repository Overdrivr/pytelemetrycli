[![PyPI version](https://badge.fury.io/py/pytelemetrycli.svg)](https://badge.fury.io/py/pytelemetrycli)
[![Join the chat at https://gitter.im/Overdrivr/pytelemetry](https://badges.gitter.im/Overdrivr/pytelemetry.svg)](https://gitter.im/Overdrivr/pytelemetry?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
*Windows:* [![Build status](https://ci.appveyor.com/api/projects/status/35jkrkiu03dfav9v/branch/master?svg=true)](https://ci.appveyor.com/project/Overdrivr/pytelemetrycli/branch/master)
*Unix* [![Build Status](https://travis-ci.org/Overdrivr/pytelemetrycli.svg?branch=master)](https://travis-ci.org/Overdrivr/pytelemetrycli)
[![Stories in Ready](https://badge.waffle.io/Overdrivr/pytelemetrycli.svg?label=ready&title=Ready)](http://waffle.io/Overdrivr/pytelemetrycli)

## pytelemetry command line interface

This tool is a command-line interface (CLI). It enables superior communication with any embedded device. It was designed for:

* **fast prototyping and debugging**. Set everything up in a few minutes and start debugging any embedded device efficiently. Forget about `printf`. Forever.
* **communication-based applications**. Stop re-writing custom protocols for each new project.
* **real-time update of embedded application parameters**. Tune your application without loosing time compiling & flashing just for parameter tuning.
* **plot** data from the device in real-time. Standard linear data is supported, but also arrays, sparse arrays. In the future, also Matrices, XYZ, and RGB-type codes.
* **Reusability**. The protocol is highly flexible, loosely coupled to your application. It can be used in a wide number of application scenarios.

## overview
This CLI provides a set of commands to connect to a device, read, plot, write data on it, log any received and sent data.

*In the future*: export to Excel and CSV and replay command in the CLI for offline inspection.

The communication protocol that carry all exchanged information is implemented in Python and C:
* [`pytelemetry`](https://github.com/Overdrivr/pytelemetry)[![PyPI version](https://badge.fury.io/py/pytelemetry.svg)](https://badge.fury.io/py/pytelemetry) for scripting the communication from your PC
* [`telemetry`](https://github.com/Overdrivr/pytelemetry): for enabling communication in the embedded device.

Officially supported embedded platforms are for now `Arduino` and `Mbed`.

See the [central documentation](https://github.com/Overdrivr/Telemetry/wiki) for installation instructions, tutorials, description of the protocol, etc.

## interface and plot widget
Aan example of listing serial ports `ls -s`, connecting to a device through COM20 `serial com20 --bauds 115200`, listing all received topics `ls` and opening a plot on topic touch `plot touch`

![Console example](https://raw.githubusercontent.com/Overdrivr/pytelemetrycli/master/console.png)

![Plot example](https://raw.githubusercontent.com/Overdrivr/pytelemetrycli/master/graph.png)

## List of commands
The command line interface can be started like this
```
python3 -m pytelemetrycli.cli
```
If everything is installed properly, `:>` should welcome you.
```
pytelemetry terminal started. (type help for a list of commands.)
:> _
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

Usage: pub (--u8 | --u16 | --u32 | --i8 | --i16 | --i32 | --f32 | --s) <topic> <value>
```

### plot
```bash
Plots <topic> in a graph window.

Usage: plot <topic>
```

### stats
```bash
Displays different metrics about the active transport (ex : serial port).
This allows you to know if for instance corrupted frames are received, what fraction
of the maximum baudrate is being used, etc.

Usage: stats
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

## installation
`pytelemetrycli` requires python 3.3+, PyQt4 and numpy.

### Windows
It is recommended to download [`numpy`](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy) and [`PyQt4`](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4) wheels python packages (courtesy of Christoph Gohlke).

In case you were wondering, **no** you **don't** have to install Qt. The binary wheel is enough.

Then install with pip the downloaded files

```bash
pip install numpy-x.xx.x+vanilla-cp3x-none-winxxx.whl
pip install PyQt4-x.xx.x-cp3x-none-winxxx.whl
```

Then, simply install `pytelemetrycli` with pip as usual

```bash
pip install pytelemetrycli
```

### Mac OS
The easiest way to install numpy and PyQt4 seem to be using `homebrew`.
lease note that you should also have installed python 3.5 with homebrew for this to work correctly.
Also, avoid to have another python 3.5 distribution on your system otherwise you will face import issues as well.

```bash
brew install python3
brew install pyqt --with-python3
pip3 install pytelemetrycli
```

### Linux

The setup used for testing relies on miniconda.
```
conda install numpy
conda install pyqt
conda install pip
pip install pytelemetrycli
```
However, if you have PyQt4 and numpy already installed in your directory, simply run
```
pip install pytelemetrycli
```
