#! /usr/bin/env python3
import time
import logging
import sqlite3
try:
    from cPickle import dumps, loads, HIGHEST_PROTOCOL as PICKLE_PROTOCOL
except ImportError:
    from pickle import dumps, loads, HIGHEST_PROTOCOL as PICKLE_PROTOCOL

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
            self._create_tables()
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
        if not self.db:
            return self._result

        cursor = self.db.cursor()
        cursor.execute("SELECT result FROM Result")
        result_blob = cursor.fetchone()[0]
        return self._sqlite_blob_decode(result_blob)

    @result.setter
    def result(self, value):
        self._result = value
        if not self.db:
            return

        cursor = self.db.cursor()
        cursor.execute("DELETE FROM Result")
        cursor.execute(
            "INSERT INTO Result(result, timestamp) VALUES (?, ?)",
            (self._sqlite_blob_encode(value), time.time())
        )

        self.db.commit()

    @staticmethod
    def _sqlite_blob_encode(obj):
        return sqlite3.Binary(dumps(obj, protocol=PICKLE_PROTOCOL))

    @staticmethod
    def _sqlite_blob_decode(obj):
        return loads(bytes(obj))

    def _create_tables(self):
        cursor = self.db.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Result(
                result BLOB,
                timestamp REAL
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS RestorePoint(
                restore_data BLOB,
                timestamp REAL
            );
            """
        )

        self.db.commit()
