import sqlite3

# Connect (or create) a database file
conn = sqlite3.connect("data/violations.db")
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS helmet_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    video_name TEXT,
    image_path TEXT
)
""")

conn.commit()
conn.close()
print("✅ Database and table created successfully.")