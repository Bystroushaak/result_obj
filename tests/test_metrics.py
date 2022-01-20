import sqlite3

from result_obj.result_obj import Metrics


def test_metrics_attribute_acces():
    m = Metrics()
    assert m.something


def test_metrics_start_stop():
    m = Metrics(sqlite3.connect("test.sqlite"))
    m.timer.start(tag=1)
    m.timer.stop(tag=1)
    m.timer.increment()
    m.timer.value(100)

    assert m._stream
