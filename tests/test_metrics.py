from result_obj.result_obj import Metrics


def test_metrics_attribute_acces():
    m = Metrics()
    assert m.something


def test_metrics_start_stop():
    m = Metrics()
    m.timer.start()
    m.timer.stop()
    m.timer.increment()
    m.timer.value(100)

    assert m._stream
