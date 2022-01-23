import sys
import logging


class SqliteHandler(logging.Handler):
    def __init__(self, level, db, flush_after=100):
        super().__init__(level=level)

        self.db = db
        self._create_tables()

        def handle_exception(exc_type, exc_value, exc_traceback):
            logger = logging.getLogger()
            logger.critical("Exception %s %s %s", exc_type, exc_value, exc_traceback)
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        sys.excepthook = handle_exception

    def emit(self, record):
        cursor = self.db.cursor()

        cursor.execute("""
            INSERT INTO Logs(
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.created,
                record.filename,
                record.funcName,
                record.levelname,
                record.levelno,
                record.lineno,
                record.msg % record.args,
                record.module,
                record.name,
                record.pathname,
                record.process,
                record.processName,
                record.thread,
                record.threadName,
            )
        )

        self.db.commit()

    def _create_tables(self):
        cursor = self.db.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Logs(
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
