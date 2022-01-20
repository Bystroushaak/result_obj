#! /usr/bin/env python3
import sqlite3

from result_obj.metrics import Metrics
from result_obj.progress import Progress
from result_obj.status_handler import StatusHandler


class Result:
    def __init__(self, sqlite_path=None):
        self.path = sqlite_path if sqlite_path is not None else self._get_path()
        self.db = None
        if sqlite_path:
            self.db = sqlite3.connect(sqlite_path)

        self.metrics = Metrics(self.db)
        self.progress = Progress(self.db)
        self.status_handler = StatusHandler(self.db)
        self._result = None

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
