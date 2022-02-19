import os
import os.path
import random

from result_obj.result_obj import ResultObj


class Obj:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value


def test_store_result():
    result_obj = ResultObj(":memory:")

    result_obj.result = Obj(1)
    assert result_obj.result.get_value() == 1

    result_obj.result = Obj(2)
    assert result_obj.result.get_value() == 2

    # only one result is kept
    cursor = result_obj.db.cursor()
    cursor.execute("SELECT * FROM Result")
    data = list(cursor.fetchall())
    assert len(data) == 1


def test_empty_result():
    result_obj = ResultObj(":memory:")

    assert not result_obj.result


def test_store_restore_point():
    result_obj = ResultObj(":memory:")

    result_obj.restore_point = Obj(1)
    assert result_obj.restore_point.get_value() == 1

    result_obj.restore_point = Obj(2)
    assert result_obj.restore_point.get_value() == 2

    cursor = result_obj.db.cursor()
    cursor.execute("SELECT * FROM RestorePoint")
    data = list(cursor.fetchall())
    assert len(data) == 2


def test_empty_restore_point():
    result_obj = ResultObj(":memory:")

    assert not result_obj.restore_point


def _test_all():
    if os.path.exists("test.sqlite"):
        os.unlink("test.sqlite")

    result_obj = ResultObj("test.sqlite")

    result_obj.metrics.runtime.start()

    result_obj.logger.info("Started")
    result_obj.status = "Running"
    result_obj.metrics.hit.increment()
    result_obj.metrics.value.value(100)

    result_obj.logger.info("Metrics used")

    result_obj.restore_point = 1
    result_obj.restore_point = 2
    result_obj.restore_point = 3

    result_obj.result = 1

    result_obj.status = "Finished"
    result_obj.metrics.runtime.stop()
    result_obj.logger.info("Stopped")


def test_all_bigger():
    if os.path.exists("test.sqlite"):
        os.unlink("test.sqlite")

    result_obj = ResultObj("test.sqlite")

    result_obj.metrics.runtime.start()

    result_obj.logger.info("Started")
    result_obj.status = "Running"

    for _ in range(1000):
        result_obj.metrics.hit.increment()
        result_obj.metrics.value.value(random.randint(0, 100))

    result_obj.logger.info("Metrics used")

    for _ in range(1000):
        result_obj.logger.info("Test")

    result_obj.restore_point = 1
    result_obj.restore_point = 2
    result_obj.restore_point = 3

    result_obj.result = Obj(1)

    result_obj.status = "Finished"
    result_obj.metrics.runtime.stop()
    result_obj.logger.info("Stopped")
