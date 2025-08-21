import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Option A: sabka default price set karo (example: 199)
cur.execute("UPDATE cakes SET price = 199 WHERE price IS NULL OR price = 0")

# Option B: specific names ke hisaab se (uncomment and edit):
# mapping = {
#     "Pistachio Cake": 499,
#     "Butterscotch Cake": 449,
#     "Donut": 49,
#     "Cupcake": 69
# }
# for name, p in mapping.items():
#     cur.execute("UPDATE cakes SET price = ? WHERE name = ?", (p, name))

conn.commit()
conn.close()
print("✅ Prices updated.")
