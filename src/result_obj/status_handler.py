import time


class StatusHandler:
    def __init__(self, db=None):
        self._db = db
        self.update_handler = None
        self.status = ""
        self.timestamp = 0
        self.status_log = []

        self._create_tables()

    def set_status(self, status):
        self.timestamp = time.time()
        self.status = status

        self.status_log.append((self.timestamp, status))

        self._save_to_db()
        self._call_update_handler()

    def _save_to_db(self):
        if not self._db:
            return

        cursor = self._db.cursor()
        cursor.execute(
            "INSERT INTO StatusHistory VALUES(?, ?)",
            (self.status, self.timestamp)
        )
        self._db.commit()

    def _call_update_handler(self):
        if self.update_handler:
            self.update_handler(self)

    def _create_tables(self):
        cursor = self._db.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS StatusHistory(
                status TEXT,
                timestamp REAL
            );
            """
        )

        self._db.commit()
