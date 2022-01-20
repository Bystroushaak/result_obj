import sqlite3

from result_obj.result_obj import Progress


def test_progress_percent():
    progress = Progress(sqlite3.connect(":memory:"))

    progress.percent = 10
    progress.percent = 50
    progress.percent = 100


def test_progress_items():
    progress = Progress(sqlite3.connect(":memory:"))

    progress.number_of_items = 10

    progress.increase()
    assert progress.percent == 10

    progress.increase()
    assert progress.percent == 20

    progress.increase()
    progress.increase()
    progress.increase()
    progress.increase()
    progress.increase()
    progress.increase()
    progress.increase()
    progress.increase()
    assert  progress.percent == 100
