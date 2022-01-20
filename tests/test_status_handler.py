import sqlite3

from result_obj.status_handler import StatusHandler


def test_progress_percent():
    status_handler = StatusHandler(sqlite3.connect(":memory:"))

    status_handler.set_status("something")
    status_handler.set_status("something else")

    assert status_handler.status_log
    assert [x[1] for x in status_handler.status_log] == ["something", "something else"]
