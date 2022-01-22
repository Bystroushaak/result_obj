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
