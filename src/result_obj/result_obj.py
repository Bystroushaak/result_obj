#! /usr/bin/env python3
import time
import sqlite3
from typing import Any
from dataclasses import field
from dataclasses import dataclass


@dataclass
class MetricInfo:
    type: int
    tags: dict
    value: Any = None
    timestamp: float = field(init=False)

    def __post_init__(self):
        self.timestamp = time.time()

    def save_to_db(self, cursor):
        cursor.execute(
            "INSERT INTO Metrics(timestamp, type, value) VALUES (?, ?, ?)",
            (self.timestamp, self.type, self.value),
        )
        metrics_tag_id = cursor.lastrowid
        if not self.tags:
            return

        for key, val in self.tags.items():
            cursor.execute(
                "INSERT INTO MetricsTags(metrics_id, name, value) VALUES (?, ?, ?)",
                (metrics_tag_id, key, str(val)),
            )


# noinspection SqlNoDataSourceInspection
class Metrics:
    commit_after = 1

    def __init__(self, db=None):
        self._stream = []
        self._db = db
        self._create_tables()
        self._counter = 0

    def add_to_stream(self, info: MetricInfo):
        self._stream.append(info)
        self._counter += 1

        if not self._db:
            return

        info.save_to_db(self._db.cursor())
        if self._counter % self.commit_after:
            self._db.commit()

    def __getattr__(self, item):
        return Metric(item, self)

    # noinspection SqlDialectInspection
    def _create_tables(self):
        if not self._db:
            return

        cursor = self._db.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS MetricsTags(
                metrics_id INT PRIMARY KEY,
                name TEXT,
                value TEXT,
                FOREIGN KEY(metrics_id) REFERENCES Metrics(metrics_id)
            );
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Metrics(
                metrics_id int PRIMARY KEY,
                timestamp real,
                type INT,
                value INT
            );
        """
        )
        self._db.commit()

    def __del__(self):
        if self._db:
            self._db.commit()


class Metric:
    TYPE_START = 0
    TYPE_STOP = 1
    TYPE_INCREMENT = 2
    TYPE_VALUE = 3

    def __init__(self, name, metrics):
        self.name = name
        self.metrics = metrics

    def start(self, **kwargs):
        self.metrics.add_to_stream(MetricInfo(self.TYPE_START, kwargs))

    def stop(self, **kwargs):
        self.metrics.add_to_stream(MetricInfo(self.TYPE_STOP, kwargs))

    def increment(self, **kwargs):
        self.metrics.add_to_stream(MetricInfo(self.TYPE_INCREMENT, kwargs))

    def value(self, value: int, **kwargs):
        self.metrics.add_to_stream(MetricInfo(self.TYPE_VALUE, kwargs, value))


class Result:
    def __init__(self, sqlite_path=None):
        self.path = sqlite_path if sqlite_path is not None else self._get_path()
        self.db = None
        if sqlite_path:
            self.db = sqlite3.connect(sqlite_path)

        self.metrics = Metrics(self.db)
        self._result = None

    def _get_path(self):
        return "/tmp"

    @property
    def result(self):
        return

    @result.setter
    def result(self, value):
        pass
