from logging import getLogger, Formatter, FileHandler, StreamHandler
from logging.handlers import RotatingFileHandler
import logging
import datetime
import os

def init_logging():
    # Disable default stderr handler
    root = getLogger().addHandler(logging.NullHandler())

    # Format how data will be .. formatted
    formatter = Formatter('%(asctime)s | %(levelname)s | %(message)s')
    sharedformatter = Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    streamformatter = Formatter('%(message)s')

    # Get the loggers used in pytelemetry.telemetry.telemetry file
    rx = getLogger('telemetry.rx')
    tx = getLogger('telemetry.tx')
    topics = getLogger('topics')
    cli = getLogger('cli')

    rx.setLevel(logging.DEBUG)
    tx.setLevel(logging.DEBUG)
    topics.setLevel(logging.DEBUG)
    cli.setLevel(logging.DEBUG)

    # Create a handler to save logging output to a file
    dateTag = datetime.datetime.now().strftime("%Y-%b-%d_%H-%M-%S")

    # Create a folder to store all logs for the session
    os.makedirs('logs/{0}/'.format(dateTag))

    # Handlers config
    rx_handler = FileHandler('logs/{0}/in-{0}.log'.format(dateTag))
    rx_handler.setLevel(logging.DEBUG)
    rx_handler.setFormatter(formatter)

    tx_handler = FileHandler('logs/{0}/out-{0}.log'.format(dateTag))
    tx_handler.setLevel(logging.DEBUG)
    tx_handler.setFormatter(formatter)

    app_handler = FileHandler('logs/{0}/cli-{0}.log'.format(dateTag))
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(sharedformatter)

    cli_stream_handler = StreamHandler()
    cli_stream_handler.setLevel(logging.INFO)
    cli_stream_handler.setFormatter(streamformatter)

    # Attach the logger to the handler
    rx.addHandler(rx_handler)
    tx.addHandler(tx_handler)
    topics.addHandler(app_handler)
    cli.addHandler(app_handler)
    #cli.addHandler(cli_stream_handler)
