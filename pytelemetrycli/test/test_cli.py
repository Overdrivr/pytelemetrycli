from pytelemetrycli.cli import Application
import pytest
import unittest.mock as mock
from unittest.mock import patch
import cmd
import io
import sys
import queue

class TransportMock:
    def __init__(self):
        self.q = queue.Queue()
        self.canConnect = False
    def authorizeConnect(self,value):
        self.canConnect = value
    def connect(self,options):
        if not self.canConnect:
            raise IOError("TransportMock denied connection")
    def disconnect(self):
        pass
    def read(self, maxbytes=1):
        amount = maxbytes if self.q.qsize() > maxbytes else self.q.qsize()
        data = []
        for i in range(amount):
            data.append(self.q.get())
        return data
    def readable(self):
        return self.q.qsize()
    def write(self, data):
        for c in data:
            self.q.put(c)
    def writeable(self):
        return True

"""
def test_print_existing_topic(tlmcli):
    # TODO: Test stdout ?
    tlmcli.onecmd("print topicA")

# TODO: Test plots ?

def test_pub_to_exisiting_topic(tlmcli):
    with patch.object(tlmcli.transport, 'writeable') as mock:
        tlmcli.onecmd("pub topicA 0.4 --f32") # TODO : Fix issue. Mocking doesn't seem to work
    mock.assert_called_with()
"""


@pytest.fixture(scope="module")
def fixturefortests():
    transport = TransportMock()
    outstream = io.StringIO()
    tlm = Application(transport=transport,stdout=outstream)

    return transport, outstream, tlm

def clear(stream):
    stream.truncate(0)
    stream.seek(0)

def test_pub_ls(fixturefortests):
    tr, outstream, tlm = fixturefortests

    clear(outstream)

    tlm.onecmd("ls")
    tlm.runner.update()
    assert outstream.getvalue() == ""

    clear(outstream)

    tlm.onecmd("pub --f32 topicA 0.4")
    tlm.runner.update()
    assert outstream.getvalue() == "Published on topic 'topicA' : 0.4 [float32]\n"

    clear(outstream)

    tlm.onecmd("ls")
    tlm.runner.update()
    assert outstream.getvalue() == "topicA\n"

    clear(outstream)

    tlm.onecmd("pub --f32 topicB 0.4")
    tlm.runner.update()
    assert outstream.getvalue() == "Published on topic 'topicB' : 0.4 [float32]\n"

    clear(outstream)

    tlm.onecmd("ls")
    tlm.runner.update()
    assert outstream.getvalue() == "topicA\ntopicB\n"

    clear(outstream)

def test_connect_fail(fixturefortests):
    tr, outstream, tlm = fixturefortests
    clear(outstream)

    tlm.onecmd("serial com123")
    tlm.runner.update()
    assert outstream.getvalue() == "Failed to connect to com123 at 9600 (bauds).\n"

    clear(outstream)

    tlm.onecmd("serial com123 -b 115200")
    tlm.runner.update()
    assert outstream.getvalue() == "Failed to connect to com123 at 115200 (bauds).\n"

    clear(outstream)

    tlm.onecmd("serial com123 --bauds 57600")
    tlm.runner.update()
    assert outstream.getvalue() == "Failed to connect to com123 at 57600 (bauds).\n"

    clear(outstream)

def test_print(fixturefortests):
    tr, outstream, tlm = fixturefortests
    clear(outstream)

    tlm.onecmd("pub --i32 foo 2")
    tlm.runner.update()
    assert outstream.getvalue() == "Published on topic 'foo' : 2 [int32]\n"

    clear(outstream)

    tlm.onecmd("pub --i32 foo 3")
    tlm.runner.update()
    assert outstream.getvalue() == "Published on topic 'foo' : 3 [int32]\n"

    clear(outstream)

    tlm.onecmd("pub --i32 foo 4")
    tlm.runner.update()
    assert outstream.getvalue() == "Published on topic 'foo' : 4 [int32]\n"

    clear(outstream)

    tlm.onecmd("print foo")
    tlm.runner.update()
    assert outstream.getvalue() == "4\n"

    clear(outstream)

    tlm.onecmd("print foo -a 3")
    tlm.runner.update()
    assert outstream.getvalue() == "2\n3\n4\n"

    clear(outstream)

    tlm.onecmd("print foo --amount 3")
    tlm.runner.update()
    assert outstream.getvalue() == "2\n3\n4\n"

    clear(outstream)

    tlm.onecmd("print foo --amount 10")
    tlm.runner.update()
    assert outstream.getvalue() == "2\n3\n4\n"

    clear(outstream)

    tlm.onecmd("print foo -a 0")
    tlm.runner.update()
    assert outstream.getvalue() == "2\n3\n4\n"

    clear(outstream)
