import sqlite3 as sq
with sq.connect('orders.db') as con:
    cur = con.cursor() # курсор позволяет делать скл запросы к базе
    cur.execute("""CREATE TABLE inbox(
    code INTEGER,
    name TEXT,
    moment DATETIME
""")
