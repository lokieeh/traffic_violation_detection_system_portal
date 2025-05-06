# database/init_db.py

import sqlite3
import os

# Create the database folder if it doesn't exist
os.makedirs("database", exist_ok=True)

# Connect to the database file (it will be created if it doesn't exist)
conn = sqlite3.connect("database/violations.db")
c = conn.cursor()

# Create the violations table
c.execute("""
    CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        timestamp TEXT,
        snapshot TEXT,
        video TEXT
    )
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully at 'database/violations.db'")