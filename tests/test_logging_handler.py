import sqlite3

from result_obj.result_obj import Result


def test_progress_percent():
    result = Result(":memory:")

    result.logger.info("Test")
