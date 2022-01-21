#! /usr/bin/env python3
import logging
import sqlite3

from result_obj.metrics import Metrics
from result_obj.progress import Progress
from result_obj.status_handler import StatusHandler
from result_obj.logging_handler import SqliteHandler


class Result:
    def __init__(self, sqlite_path=None, logger=None):
        self.path = sqlite_path
        self.db = None
        self.logger = logger if logger else logging.getLogger()
        if sqlite_path:
            self.db = sqlite3.connect(sqlite_path)
            self._init_sqlite_logging_handler()

        self.metrics = Metrics(self.db)
        self.progress = Progress(self.db)
        self.status_handler = StatusHandler(self.db)
        self._result = None

    def _init_sqlite_logging_handler(self):
        handler = SqliteHandler(logging.DEBUG, self.db)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(filename)s:%(lineno)s; %(message)s"
        ))
        self.logger.addHandler(handler)

    @property
    def status(self):
        return self.status_handler.status

    @status.setter
    def status(self, value):
        self.status_handler.set_status(value)

    @property
    def result(self):
        return

    @result.setter
    def result(self, value):
        pass
