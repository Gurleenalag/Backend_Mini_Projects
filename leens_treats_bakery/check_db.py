import sqlite3

conn = sqlite3.connect("bakery.db")
c = conn.cursor()

# sabhi tables dikhao
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", c.fetchall())

# cakes ke records dikhao
c.execute("SELECT * FROM cakes;")
print("Cakes:", c.fetchall())

conn.close()
