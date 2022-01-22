import sqlite3

from result_obj.result_obj import Result


class Obj:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value


def test_store_result():
    result_obj = Result(":memory:")

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
    result_obj = Result(":memory:")

    assert not result_obj.result


def test_store_restore_point():
    result_obj = Result(":memory:")

    result_obj.restore_point = Obj(1)
    assert result_obj.restore_point.get_value() == 1

    result_obj.restore_point = Obj(2)
    assert result_obj.restore_point.get_value() == 2

    cursor = result_obj.db.cursor()
    cursor.execute("SELECT * FROM RestorePoint")
    data = list(cursor.fetchall())
    assert len(data) == 2


def test_empty_restore_point():
    result_obj = Result(":memory:")

    assert not result_obj.restore_point
