#! /usr/bin/env python3
import time
import sqlite3

from result_obj.metrics import Metrics


class Progress:
    def __init__(self, db=None):
        self._percent = 0
        self._pointer = 0
        self._db = db

        self.number_of_items = 0

        self._create_tables()
        self.percent = 0

    @property
    def percent(self):
        return self._percent

    @percent.setter
    def percent(self, value):
        self._percent = value

    def increase(self):
        self._pointer += 1
        if self._pointer > self.number_of_items:
            self.number_of_items = self._pointer

        self._percent = self._pointer / (self.number_of_items / 100)

        if not self._db:
            return

        cursor = self._db.cursor()
        cursor.execute(
            "INSERT INTO Progress VALUES(?, ?, ?, ?)",
            (self._percent, self._pointer, self.number_of_items, time.time())
        )
        self._db.commit()

    def _create_tables(self):
        cursor = self._db.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Progress(
                percent INT,
                item_number INT,
                number_of_items INT,
                timestamp REAL
            );
            """
        )

        self._db.commit()


class Result:
    def __init__(self, sqlite_path=None):
        self.path = sqlite_path if sqlite_path is not None else self._get_path()
        self.db = None
        if sqlite_path:
            self.db = sqlite3.connect(sqlite_path)

        self.metrics = Metrics(self.db)
        self.progress = Progress(self.db)
        self._result = None

    def _get_path(self):
        return "/tmp"

    @property
    def result(self):
        return

    @result.setter
    def result(self, value):
        pass
