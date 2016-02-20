from logging import getLogger, Formatter, FileHandler
from logging.handlers import RotatingFileHandler
import logging
import datetime
import os

def init_logging():
    # Disable default stderr handler
    root = getLogger().addHandler(logging.NullHandler())

    # Format how data will be .. formatted
    formatter = Formatter('%(asctime)s | %(levelname)s | %(message)s')

    # Get the loggers used in pytelemetry.telemetry.telemetry file
    rx = getLogger('telemetry.rx')
    tx = getLogger('telemetry.tx')
    topics = getLogger('topics')

    rx.setLevel(logging.DEBUG)
    tx.setLevel(logging.DEBUG)
    topics.setLevel(logging.DEBUG)

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

    topics_handler = FileHandler('logs/{0}/topics-{0}.log'.format(dateTag))
    topics_handler.setLevel(logging.DEBUG)
    topics_handler.setFormatter(formatter)

    # Attach the logger to the handler
    rx.addHandler(rx_handler)
    tx.addHandler(tx_handler)
    topics.addHandler(topics_handler)
