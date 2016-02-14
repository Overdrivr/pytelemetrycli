from pytelemetrycli.cli import Application
import pytest

class TransportMock:
    def __init__(self):
        pass
    def read(self):
        pass
    def readable(self):
        pass
    def write(self):
        pass
    def writeable(self):
        pass
    def connect(self):
        pass

class RunnerMock:
    def __init__(self):
        pass

    def connect(self,options):
        print(options)

    def disconnect(self):
        pass

@pytest.fixture(scope="module")
def tlmcli():
    pycli = Application()
    # Mock hardware tied stuff
    pycli.transport = TransportMock()
    pycli.runner = RunnerMock()
    return pycli

def test_connect(tlmcli):
    tlmcli.onecmd("serial com23 -b 115200")
