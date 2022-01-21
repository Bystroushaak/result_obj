import sys
import logging


class SqliteHandler(logging.Handler):
    def __init__(self, level, db, flush_after=100):
        super().__init__(level=level)

        self.db = db
        self.flush_after = flush_after
        self.counter = 0
        self.buffer = []

        def handle_exception(exc_type, exc_value, exc_traceback):
            self._store_buffer()
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        sys.excepthook = handle_exception

    def emit(self, record):
        self.buffer.append(record)

        if self.counter >= self.flush_after:
            self._store_buffer()

    def __del__(self):
        self._store_buffer()

    def _store_buffer(self):
        cursor = self.db.cursor()

        for record in self.buffer:
            cursor.execute("""
                INSERT INTO Logs(
                    args,
                    asctime,
                    created,
                    filename,
                    funcName,
                    levelname,
                    levelno,
                    lineno,
                    msg,
                    module,
                    name,
                    pathname,
                    process,
                    processName,
                    thread,
                    threadName
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.args,
                    record.asctime,
                    record.created,
                    record.filename,
                    record.funcName,
                    record.levelname,
                    record.levelno,
                    record.lineno,
                    record.msg,
                    record.module,
                    record.name,
                    record.pathname,
                    record.process,
                    record.processName,
                    record.thread,
                )
            )

        self.db.commit()
        self.buffer.clear()
        self.counter = 0

    def _create_tables(self):
        cursor = self.db.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Logs(
                args TEXT,
                asctime TEXT,
                created REAL,
                filename TEXT,
                funcName TEXT,
                levelname TEXT,
                levelno INT,
                lineno INT,
                msg TEXT,
                module TEXT,
                name TEXT,
                pathname TEXT,
                process INT,
                processName TEXT,
                thread INT,
                threadName TEXT
            );
            """
        )

        self.db.commit()
