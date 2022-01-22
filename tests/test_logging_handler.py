from result_obj.result_obj import ResultObj


def test_progress_percent():
    result = ResultObj(":memory:")

    result.logger.info("Test")
