import sqlite3
from datetime import datetime

class UsageTracker:
    def __init__(self, database_file="usage.db"):
        self.database_file = database_file
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS usage_data
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                action TEXT,
                duration REAL)"""
        )
        conn.commit()
        conn.close()

    def track_usage(self, action, duration):
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        c.execute(
            "INSERT INTO usage_data (timestamp, action, duration) VALUES (?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action, duration)
        )
        conn.commit()
        conn.close()

    def get_usage_statistics(self):
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        c.execute("SELECT action, AVG(duration) AS avg_duration FROM usage_data GROUP BY action")
        results = c.fetchall()
        conn.close()
        return results
