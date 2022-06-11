

import sqlite3

def create_db():
    with sqlite3.connect("sqlite.db") as conn:
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS inbox (
        code INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        moment DATETIME
        )""")
