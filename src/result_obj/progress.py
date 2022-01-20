import time


class Progress:
    def __init__(self, db=None):
        self._db = db
        self._percent = 0
        self.update_handler = None

        self.pointer = 0
        self.number_of_items = 0

        self._create_tables()
        self._save_to_db()

    @property
    def percent(self):
        return self._percent

    @percent.setter
    def percent(self, value):
        self._percent = value
        self._save_to_db()
        self._call_update_handler()

    def increase(self):
        self.pointer += 1
        if self.pointer > self.number_of_items:
            self.number_of_items = self.pointer

        self._percent = self.pointer / (self.number_of_items / 100)
        self._save_to_db()
        self._call_update_handler()

    def _save_to_db(self):
        if not self._db:
            return

        cursor = self._db.cursor()
        cursor.execute(
            "INSERT INTO Progress VALUES(?, ?, ?, ?)",
            (self._percent, self.pointer, self.number_of_items, time.time())
        )
        self._db.commit()

    def _call_update_handler(self):
        if self.update_handler:
            self.update_handler(self)

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
