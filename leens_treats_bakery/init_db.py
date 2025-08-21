import sqlite3

conn = sqlite3.connect("bakery.db")
c = conn.cursor()

# Cakes table create karo
c.execute("""
CREATE TABLE IF NOT EXISTS cakes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image TEXT
)
""")

print("✅ Cakes table created successfully!")

# Check karo agar cakes table empty hai
c.execute("SELECT COUNT(*) FROM cakes")
count = c.fetchone()[0]

if count == 0:
    cakes = [
        ("Butterscotch Cake", "Butterscotch flavored soft cake", 400.0, "Butterscotch cake.jpg"),
        ("Cupcakes", "Small and tasty cupcakes", 200.0, "cupcakes.jpg"),
        ("Donuts", "Sweet fried donuts", 150.0, "donuts.jpg"),
        ("Pistachio Cake", "Soft pistachio flavored cake", 500.0, "pistachio cake.jpg"),
        ("Red Velvet", "Soft and creamy red velvet cake", 500.0, "Red Velvet.jpg"),
        ("Vanilla Cake", "Classic vanilla flavor cake", 300.0, "Vanilla cake.jpg"),
        ("Special Cake", "Uploaded from WhatsApp", 450.0, "WhatsApp Image 2025-08-15 at 18.15.04_7add613b.jpg")
    ]

    c.executemany("INSERT INTO cakes (name, description, price, image) VALUES (?, ?, ?, ?)", cakes)
    print("✅ Sample cakes added successfully!")
else:
    print("⚠️ Cakes already exist, skipping insert.")

conn.commit()
conn.close()
