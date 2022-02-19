import os
import sys
import time
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


class DataTypes:
    pickle = "cpython_pickle"


class ResultObj:
    metrics: Metrics
    progress: Progress
    status_handler: StatusHandler
    _sqlite_logging_handler: Optional[MemoryHandler]

    VERSION = "1.0.0"
    LOG_FMT = "%(asctime)s %(levelname)s %(filename)s:%(lineno)s; %(message)s"

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
            self.metrics = Metrics(self.db)
            self._save_debug_data()
        else:
            self.metrics = Metrics(self.db)

        self.progress = Progress(self.db)
        self.status_handler = StatusHandler(self.db)
        self._result = None
        self._restore_point = None

    def _init_sqlite_logging_handler(self):
        sqlite_handler = SqliteHandler(logging.DEBUG, self.db)
        sqlite_handler.setFormatter(logging.Formatter(self.LOG_FMT))
        self._sqlite_logging_handler = MemoryHandler(10)
        self._sqlite_logging_handler.setTarget(sqlite_handler)
        self.logger.addHandler(self._sqlite_logging_handler)
        self.logger.setLevel(logging.DEBUG)

    def add_logging_handler(self, handler):
        self.logger.addHandler(handler)

    def add_stdout_logging_handler(self, fmt=None, level=logging.INFO):
        stream_handler = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter(fmt if fmt else self.LOG_FMT)
        stream_handler.setFormatter(fmt)
        stream_handler.setLevel(level)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.DEBUG)

    def add_stderr_logging_handler(self, fmt=None, level=logging.INFO):
        stream_handler = logging.StreamHandler(sys.stderr)
        fmt = logging.Formatter(fmt if fmt else self.LOG_FMT)
        stream_handler.setFormatter(fmt)
        stream_handler.setLevel(level)
        self.logger.addHandler(stream_handler)
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
            "INSERT INTO RestorePoint(timestamp, type, restore_data) VALUES (?, ?, ?)",
            (time.time(), DataTypes.pickle, self._sqlite_blob_encode(value)),
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
            "INSERT INTO Result(timestamp, type, result) VALUES (?, ?, ?)",
            (time.time(), DataTypes.pickle, self._sqlite_blob_encode(value)),
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
                pwd TEXT
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS MetadataEnvVars(
                key TEXT,
                value TEXT
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Result(
                timestamp REAL,
                type TEXT,
                result BLOB
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS RestorePoint(
                timestamp REAL,
                type TEXT,
                restore_data BLOB
            );
            """
        )

        self.db.commit()

    def _save_debug_data(self):
        if not self._debug_data_stored:
            self._first_time_debug_data()
            return

        cursor = self.db.cursor()

        cursor.execute(
            """
            INSERT INTO Metadata(
                timestamp,
                pwd
            ) VALUES(?, ?)
            """,
            (
                time.time(),
                os.getcwd(),
            ),
        )
        self.db.commit()

        self._save_mem_disc_metrics()

    def _first_time_debug_data(self):
        self._save_mem_disc_metrics()

        cursor = self.db.cursor()

        cursor.execute(
            """
            INSERT INTO Metadata(
                timestamp,
                version,
                argv,
                pwd
            ) VALUES(?, ?, ?, ?)
            """,
            (
                time.time(),
                self.VERSION,
                str(sys.argv),
                os.getcwd(),
            ),
        )

        cursor.executemany(
            """
            INSERT INTO MetadataEnvVars(
                key,
                value
            ) VALUES (?, ?)
            """,
            ((key, val) for key, val in os.environ.items())
        )

        self.db.commit()

        self._debug_data_stored = True

    def _save_mem_disc_metrics(self):
        mem_info = psutil.virtual_memory()
        self.metrics.debug_mem_total.value(mem_info.total)
        self.metrics.debug_mem_available.value(mem_info.available)
        self.metrics.debug_mem_percent.value(mem_info.percent)

        disc_info = psutil.disk_usage(os.getcwd())
        self.metrics.debug_disc_total.value(disc_info.total)
        self.metrics.debug_disc_free.value(disc_info.free)
        self.metrics.debug_disc_percent.value(disc_info.percent)

    def __del__(self):
        self._sqlite_logging_handler.flush()
