import sqlite3

conn = sqlite3.connect("data/violations.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM helmet_violations")
rows = cursor.fetchall()

print("\n📄 Logged Violations:")
for row in rows:
    print(row)

conn.close()