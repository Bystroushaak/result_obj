import os
import sys
import time
import json
import logging
import sqlite3
from typing import Optional
from logging.handlers import MemoryHandler

try:
    from cPickle import dumps, loads, HIGHEST_PROTOCOL as PICKLE_PROTOCOL
except ImportError:
    from pickle import dumps, loads, HIGHEST_PROTOCOL as PICKLE_PROTOCOL

import psutil

from result_obj.metrics import Metrics
from result_obj.progress import Progress
from result_obj.status_handler import StatusHandler
from result_obj.logging_handler import SqliteHandler


class ResultObj:
    metrics: Metrics
    progress: Progress
    status_handler: StatusHandler
    _sqlite_logging_handler: Optional[MemoryHandler]
    VERSION = "1.0.0"

    def __init__(self, sqlite_path=None, logger=None):
        self.path = sqlite_path
        self.db = None
        self.logger = logger if logger else logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self._sqlite_logging_handler = None
        self._debug_data_stored = False

        if sqlite_path:
            self.db = sqlite3.connect(sqlite_path)
            self._create_tables()
            self._init_sqlite_logging_handler()
            self._save_debug_data()

        self.metrics = Metrics(self.db)
        self.progress = Progress(self.db)
        self.status_handler = StatusHandler(self.db)
        self._result = None
        self._restore_point = None

    def _init_sqlite_logging_handler(self):
        sqlite_handler = SqliteHandler(logging.DEBUG, self.db)
        sqlite_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(filename)s:%(lineno)s; %(message)s"
            )
        )
        self._sqlite_logging_handler = MemoryHandler(10)
        self._sqlite_logging_handler.setTarget(sqlite_handler)
        self.logger.addHandler(self._sqlite_logging_handler)
        self.logger.setLevel(logging.DEBUG)

    @property
    def status(self):
        return self.status_handler.status

    @status.setter
    def status(self, value):
        self.status_handler.set_status(value)

    @property
    def restore_point(self):
        if not self.db:
            return self._restore_point

        cursor = self.db.cursor()
        cursor.execute(
            "SELECT restore_data FROM RestorePoint ORDER BY timestamp DESC LIMIT 1;"
        )
        data = cursor.fetchone()
        if not data:
            return None

        return self._sqlite_blob_decode(data[0])

    @restore_point.setter
    def restore_point(self, value):
        self._restore_point = value
        if not self.db:
            return

        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO RestorePoint(restore_data, timestamp) VALUES (?, ?)",
            (self._sqlite_blob_encode(value), time.time()),
        )

        self.db.commit()
        self._sqlite_logging_handler.flush()
        self._save_debug_data()

    @property
    def result(self):
        if not self.db:
            return self._result

        cursor = self.db.cursor()
        cursor.execute("SELECT result FROM Result")
        data = cursor.fetchone()
        if not data:
            return None

        return self._sqlite_blob_decode(data[0])

    @result.setter
    def result(self, value):
        self._result = value
        if not self.db:
            return

        cursor = self.db.cursor()
        cursor.execute("DELETE FROM Result")
        cursor.execute(
            "INSERT INTO Result(result, timestamp) VALUES (?, ?)",
            (self._sqlite_blob_encode(value), time.time()),
        )

        self.db.commit()
        self._sqlite_logging_handler.flush()
        self._save_debug_data()

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
            CREATE TABLE IF NOT EXISTS Metadata(
                timestamp REAL,
                version TEXT,
                argv TEXT,
                pwd TEXT,
                env_vars_json TEXT,
                mem_total INT,
                mem_free INT,
                mem_percent REAL,
                disc_total INT,
                disc_free INT,
                disc_percent REAL
            );
            """
        )
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

    def _save_debug_data(self):
        if not self._debug_data_stored:
            self._first_time_debug_data()
            return

        cursor = self.db.cursor()

        mem_info = psutil.virtual_memory()
        disc_info = psutil.disk_usage(os.getcwd())
        cursor.execute(
            """
            INSERT INTO Metadata(
                timestamp,
                pwd,
                mem_total,
                mem_free,
                mem_percent,
                disc_total,
                disc_free,
                disc_percent
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                time.time(),
                os.getcwd(),
                mem_info.total,
                mem_info.available,
                mem_info.percent,
                disc_info.total,
                disc_info.free,
                disc_info.percent,
            ),
        )
        self.db.commit()

    def _first_time_debug_data(self):
        cursor = self.db.cursor()

        mem_info = psutil.virtual_memory()
        disc_info = psutil.disk_usage(os.getcwd())
        cursor.execute(
            """
            INSERT INTO Metadata(
                timestamp,
                version,
                argv,
                pwd,
                env_vars_json,
                mem_total,
                mem_free,
                mem_percent,
                disc_total,
                disc_free,
                disc_percent
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                time.time(),
                self.VERSION,
                str(sys.argv),
                os.getcwd(),
                json.dumps(dict(os.environ)),
                mem_info.total,
                mem_info.available,
                mem_info.percent,
                disc_info.total,
                disc_info.free,
                disc_info.percent,
            ),
        )
        self.db.commit()

        self._debug_data_stored = True
