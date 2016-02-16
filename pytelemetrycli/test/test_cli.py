from pytelemetrycli.cli import Application
import pytest
import unittest.mock as mock
from unittest.mock import patch
"""
class TransportMock:
    def __init__(self):
        pass
    def read(self):
        pass
    def readable(self):
        pass
    def write(self, data):
        pass
    def writeable(self):
        pass

class RunnerMock:
    def __init__(self):
        pass

    def connect(self,port,bauds):
        pass

    def disconnect(self):
        pass

@pytest.fixture(scope="module")
def tlmcli():
    pycli = Application()
    # Mock hardware tied stuff
    pycli.transport = TransportMock()
    pycli.telemetry.transport = TransportMock()
    pycli.runner = RunnerMock()
    return pycli

def test_connect(tlmcli):
    with patch.object(tlmcli.runner, 'connect') as mock:
        tlmcli.onecmd("serial com23 --bauds 115200")
    mock.assert_called_with("com23",115200)

def test_connect_short(tlmcli):
    with patch.object(tlmcli.runner, 'connect') as mock:
        tlmcli.onecmd("serial com23 -b 115200")
    mock.assert_called_with("com23",115200)

def test_list_topics(tlmcli):
    # TODO: Test stdout ?
    tlmcli.onecmd("ls -s")
    tlmcli.topics.process("topicA",123)
    tlmcli.topics.process("topicB","hello")
    # TODO: Test stdout ?
    tlmcli.onecmd("ls")

def test_print_existing_topic(tlmcli):
    # TODO: Test stdout ?
    tlmcli.onecmd("print topicA")

# TODO: Test plots ?

def test_pub_to_exisiting_topic(tlmcli):
    with patch.object(tlmcli.transport, 'writeable') as mock:
        tlmcli.onecmd("pub topicA 0.4 --f32") # TODO : Fix issue. Mocking doesn't seem to work
    mock.assert_called_with()
"""
