import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Check if 'price' column already exists
cur.execute("PRAGMA table_info(cakes)")
cols = [row[1] for row in cur.fetchall()]
if "price" not in cols:
    cur.execute("ALTER TABLE cakes ADD COLUMN price REAL DEFAULT 0.0")
    print("✅ 'price' column added.")
else:
    print("ℹ️ 'price' column already exists.")

conn.commit()
conn.close()
