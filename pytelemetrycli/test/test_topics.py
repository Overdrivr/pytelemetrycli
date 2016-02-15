from pytelemetrycli.topics import Topics
from multiprocessing import Queue

def test_process():
    t1 = "testTopic"
    t2 = "otherTestTopic"
    t3 = "unknownTopic"
    topic = Topics()

    topic.process(t1,123)
    assert t1 in topic.ls()
    assert len(topic.ls()) == 1

    topic.process(t2,"booyaa")
    assert t1 in topic.ls()
    assert t2 in topic.ls()
    assert len(topic.ls()) == 2

    topic.process(t1,456)
    assert len(topic.ls()) == 2

    assert topic.samples(t1,amount=1) == [456]

    assert topic.samples(t1,amount=0) == [123,456]

    assert topic.count(t1) == 2

    assert not topic.exists(t3)
    assert topic.exists(t1)
    assert topic.exists(t2)

def test_transfert_queue():
    t1 = "testTopic"
    topic = Topics()
    q = Queue()

    topic.process(t1,123)
    topic.process(t1,456)
    topic.process(t1,789)

    assert q.empty()

    topic.transfer(t1,q)

    assert q.qsize() > 0
    #assert not q.empty()

    assert q.get() == [0, 123]
    assert q.get() == [1, 456]
    assert q.get() == [2, 789]
