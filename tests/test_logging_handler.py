from result_obj.result_obj import ResultObj


def test_logging_handler():
    result_obj = ResultObj(":memory:")

    result_obj.logger.info("Test")
    result_obj.logger.debug("Test")

    cursor = result_obj.db.cursor()
    cursor.execute("SELECT * FROM Logs")
    data = cursor.fetchall()

    assert len(data) == 0

    result_obj._sqlite_logging_handler.flush()

    cursor = result_obj.db.cursor()
    cursor.execute("SELECT * FROM Logs")
    data = cursor.fetchall()

    assert len(data) >= 2
