from result_obj.result_obj import ResultObj


def test_logging_handler():
    result = ResultObj(":memory:")
    # result._logging_handler._flush_after = 1

    result.logger.info("Test")
    result.logger.debug("Test")

    cursor = result.db.cursor()
    cursor.execute("SELECT * FROM Logs")
    data = cursor.fetchall()

    assert len(data) >= 2
