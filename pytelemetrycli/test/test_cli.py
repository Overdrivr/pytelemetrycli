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
        self.counter = 0
    def authorizeConnect(self,value):
        self.canConnect = value
    def connect(self,options):
        if not self.canConnect:
            raise IOError("TransportMock denied connection")
    def disconnect(self):
        pass
    def read(self, maxbytes=1):
        amount = maxbytes if self.q.qsize() > maxbytes else self.q.qsize()
        self.counter += amount
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
    def resetStats(self):
        self.counter = 0
    def stats(self):
        return {
        "rx_bytes": self.counter
        }

# To be done
class SuperplotMock:
    def __init__(self):
        pass

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

    tlm.onecmd("pub --i16 topicC 0.0") # Casting from float to int generates negligeable error. Publish will succeed
    tlm.runner.update()
    assert outstream.getvalue() == "Published on topic 'topicC' : 0 [int16]\n"

    clear(outstream)

    tlm.onecmd("pub --i16 topicC 0.1") # Casting from float to int generates non-negligeable error. Publish will fail
    tlm.runner.update()
    assert outstream.getvalue() == "Aborted : Wrote decimal number (0.1) with integer flag.\n"

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

    tlm.onecmd("pub --s hello world")
    tlm.runner.update()
    assert outstream.getvalue() == "Published on topic 'hello' : world [string]\n"

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

    tlm.onecmd("print qux")
    tlm.runner.update()
    assert outstream.getvalue() == "Topic 'qux' unknown. Type 'ls' to list all available topics.\n"

    clear(outstream)

    tlm.onecmd("print hello")
    tlm.runner.update()
    assert outstream.getvalue() == "world\n"

    clear(outstream)

    tlm.onecmd("print foo -a 2.3")
    tlm.runner.update()
    assert outstream.getvalue() == "Could not cast --amount = '2.3' to integer. Using 1.\n4\n"

    clear(outstream)

def test_count(fixturefortests):
    tr, outstream, tlm = fixturefortests
    clear(outstream)
    tlm.topics.clear() # Clear all topics

    tlm.onecmd("count")
    tlm.runner.update()
    assert outstream.getvalue() == ""

    clear(outstream)

    tlm.onecmd("pub --i32 foo 2")
    tlm.runner.update()
    assert outstream.getvalue() == "Published on topic 'foo' : 2 [int32]\n"

    clear(outstream)

    tlm.onecmd("count")
    tlm.runner.update()
    assert outstream.getvalue() == "foo : 1\n"

    clear(outstream)

    tlm.onecmd("pub --i32 foo 3")
    tlm.runner.update()
    assert outstream.getvalue() == "Published on topic 'foo' : 3 [int32]\n"

    clear(outstream)

    tlm.onecmd("count")
    tlm.runner.update()
    assert outstream.getvalue() == "foo : 2\n"

    clear(outstream)

    tlm.onecmd("pub --f32 bar 4.2")
    tlm.runner.update()
    assert outstream.getvalue() == "Published on topic 'bar' : 4.2 [float32]\n"

    clear(outstream)

    tlm.onecmd("count")
    tlm.runner.update()
    assert outstream.getvalue() == "bar : 1\nfoo : 2\n"

    clear(outstream)

def test_disconnect_quit(fixturefortests):
    tr, outstream, tlm = fixturefortests
    clear(outstream)
    tlm.topics.clear() # Clear all topics

    tlm.onecmd("disconnect")
    assert outstream.getvalue() == "Disconnected.\n"

    clear(outstream)

    pytest.raises(SystemExit, tlm.onecmd, "quit")
    assert outstream.getvalue() == "Disconnected.\nGood Bye!\n"

    clear(outstream)

def test_wrong_command(fixturefortests):
    tr, outstream, tlm = fixturefortests
    clear(outstream)
    tlm.topics.clear() # Clear all topics

    # Just check it doesn't raises
    tlm.onecmd("pub foo --i32 123")

    clear(outstream)

def test_info(fixturefortests):
    tr, outstream, tlm = fixturefortests
    clear(outstream)
    tlm.topics.clear() # Clear all topics

    # Just check it doesn't raise
    tlm.onecmd("info")

    clear(outstream)

def test_topics_are_cleared_after_reconnect(fixturefortests):
    tr, outstream, tlm = fixturefortests
    tr.authorizeConnect(True)
    clear(outstream)
    tlm.topics.clear() # Clear all topics

    tlm.onecmd("serial com123")
    tlm.runner.update()
    assert outstream.getvalue() == "Connected to com123 at 9600 (bauds).\n"

    clear(outstream)

    tlm.onecmd("pub --f32 bar 4.2")
    tlm.runner.update()
    assert outstream.getvalue() == "Published on topic 'bar' : 4.2 [float32]\n"

    clear(outstream)

    tlm.onecmd("count")
    tlm.runner.update()
    assert outstream.getvalue() == "bar : 1\n"

    clear(outstream)

    tlm.onecmd("disconnect")
    assert outstream.getvalue() == "Disconnected.\n"

    clear(outstream)

    tlm.onecmd("count")
    tlm.runner.update()
    assert outstream.getvalue() == "bar : 1\n"

    clear(outstream)

    tlm.onecmd("ls")
    tlm.runner.update()
    assert outstream.getvalue() == "bar\n"

    clear(outstream)

    tlm.onecmd("serial com123")
    tlm.runner.update()
    assert outstream.getvalue() == "Connected to com123 at 9600 (bauds).\n"

    clear(outstream)

    # After the re-connection all previous topics should be cleared
    tlm.onecmd("count")
    tlm.runner.update()
    assert outstream.getvalue() == ""

    clear(outstream)

    tlm.onecmd("ls")
    tlm.runner.update()
    assert outstream.getvalue() == ""

    clear(outstream)


def test_stats(fixturefortests):
    tr, outstream, tlm = fixturefortests
    clear(outstream)
    tlm.topics.clear() # Clear all topics

    tr.resetStats()
    tlm.runner.resetStats()
    tlm.telemetry.resetStats()
    tlm.onecmd("stats")

    assert "Raw IO:\n" in outstream.getvalue()
    assert "\trx_bytes : 0\n" in outstream.getvalue()
    assert "IO speeds:\n" in outstream.getvalue()
    assert "\tbaudspeed : 0.0\n" in outstream.getvalue()
    assert "\tbaudratio : 0.0\n" in outstream.getvalue()
    assert "\tbaudratio_avg : 0.0\n" in outstream.getvalue()
    assert "\tbaudspeed_avg : 0.0\n" in outstream.getvalue()
    assert "Framing:\n" in outstream.getvalue()
    assert "\ttx_encoded_frames : 0\n" in outstream.getvalue()
    assert "\trx_uncomplete_frames : 0\n" in outstream.getvalue()
    assert "\ttx_processed_bytes : 0\n" in outstream.getvalue()
    assert "\trx_complete_frames : 0\n" in outstream.getvalue()
    assert "\ttx_escaped_bytes : 0\n" in outstream.getvalue()
    assert "\trx_discarded_bytes : 0\n" in outstream.getvalue()
    assert "\trx_processed_bytes : 0\n" in outstream.getvalue()
    assert "\trx_escaped_bytes : 0\n" in outstream.getvalue()
    assert "Protocol:\n" in outstream.getvalue()
    assert "\ttx_encoded_frames : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_header : 0\n" in outstream.getvalue()
    assert "\trx_decoded_frames : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_payload : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_crc : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_eol : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_topic : 0\n" in outstream.getvalue()

    tlm.onecmd("pub --i32 foo 2")

    clear(outstream)

    tlm.runner.update()

    tlm.onecmd("stats")

    speeds = tlm.runner.stats()

    assert "Raw IO:\n" in outstream.getvalue()
    assert "\trx_bytes : 14\n" in outstream.getvalue()
    assert "IO speeds:\n" in outstream.getvalue()
    assert "\tbaudspeed : {0}\n".format(speeds['baudspeed']) in outstream.getvalue()
    assert "\tbaudratio : {0}\n".format(speeds['baudratio']) in outstream.getvalue()
    assert "\tbaudratio_avg : {0}\n".format(speeds['baudratio_avg']) in outstream.getvalue()
    assert "\tbaudspeed_avg : {0}\n".format(speeds['baudspeed_avg']) in outstream.getvalue()
    assert "Framing:\n" in outstream.getvalue()
    assert "\ttx_encoded_frames : 1\n" in outstream.getvalue()
    assert "\trx_uncomplete_frames : 0\n" in outstream.getvalue()
    assert "\ttx_processed_bytes : 12\n" in outstream.getvalue()
    assert "\trx_complete_frames : 1\n" in outstream.getvalue()
    assert "\ttx_escaped_bytes : 0\n" in outstream.getvalue()
    assert "\trx_discarded_bytes : 0\n" in outstream.getvalue()
    assert "\trx_processed_bytes : 14\n" in outstream.getvalue()
    assert "\trx_escaped_bytes : 0\n" in outstream.getvalue()
    assert "Protocol:\n" in outstream.getvalue()
    assert "\ttx_encoded_frames : 1\n" in outstream.getvalue()
    assert "\trx_corrupted_header : 0\n" in outstream.getvalue()
    assert "\trx_decoded_frames : 1\n" in outstream.getvalue()
    assert "\trx_corrupted_payload : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_crc : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_eol : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_topic : 0\n" in outstream.getvalue()

    # Check stats are cleaned after restart
    tr.authorizeConnect(True)
    tlm.onecmd("serial com123")

    clear(outstream)

    tlm.onecmd("stats")

    assert "Raw IO:\n" in outstream.getvalue()
    assert "\trx_bytes : 0\n" in outstream.getvalue()
    assert "IO speeds:\n" in outstream.getvalue()
    assert "\tbaudspeed : 0.0\n" in outstream.getvalue()
    assert "\tbaudratio : 0.0\n" in outstream.getvalue()
    assert "\tbaudratio_avg : 0.0\n" in outstream.getvalue()
    assert "\tbaudspeed_avg : 0.0\n" in outstream.getvalue()
    assert "Framing:\n" in outstream.getvalue()
    assert "\ttx_encoded_frames : 0\n" in outstream.getvalue()
    assert "\trx_uncomplete_frames : 0\n" in outstream.getvalue()
    assert "\ttx_processed_bytes : 0\n" in outstream.getvalue()
    assert "\trx_complete_frames : 0\n" in outstream.getvalue()
    assert "\ttx_escaped_bytes : 0\n" in outstream.getvalue()
    assert "\trx_discarded_bytes : 0\n" in outstream.getvalue()
    assert "\trx_processed_bytes : 0\n" in outstream.getvalue()
    assert "\trx_escaped_bytes : 0\n" in outstream.getvalue()
    assert "Protocol:\n" in outstream.getvalue()
    assert "\ttx_encoded_frames : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_header : 0\n" in outstream.getvalue()
    assert "\trx_decoded_frames : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_payload : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_crc : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_eol : 0\n" in outstream.getvalue()
    assert "\trx_corrupted_topic : 0\n" in outstream.getvalue()
