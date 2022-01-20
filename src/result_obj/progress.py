import time


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
