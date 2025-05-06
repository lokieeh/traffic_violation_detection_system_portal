import os
import sqlite3
import hashlib

# Constants
USER_DB_PATH = "data/users.db"
VIOLATION_DB_PATH = "data/violations.db"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# -------------------- User Management --------------------

def create_users_table():
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(email, username, password, role):
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                  (username, email, hashed_pw, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

def authenticate_user(email, username, password):
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()
    hashed_pw = hash_password(password)
    c.execute("SELECT * FROM users WHERE email=? AND username=? AND password=?",
              (email, username, hashed_pw))
    user = c.fetchone()
    conn.close()
    return user  # Returns full user tuple (id, username, email, password, role)

def reset_password(email, username, new_password):
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()
    hashed_pw = hash_password(new_password)
    c.execute("UPDATE users SET password=? WHERE email=? AND username=?", (hashed_pw, email, username))
    conn.commit()
    updated = c.rowcount > 0
    conn.close()
    return updated

def get_all_users():
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, email, role FROM users")
    users = c.fetchall()
    conn.close()
    return users

def delete_user_by_id(user_id):
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    deleted = c.rowcount > 0
    conn.close()
    return deleted

# -------------------- Violation Management --------------------

def ensure_violations_table():
    conn = sqlite3.connect(VIOLATION_DB_PATH)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            timestamp TEXT,
            image_path TEXT
        )
    ''')

    # Ensure image_path column exists (redundant here but kept for safety)
    cursor.execute("PRAGMA table_info(violations)")
    columns = [col[1] for col in cursor.fetchall()]
    if "image_path" not in columns:
        cursor.execute("ALTER TABLE violations ADD COLUMN image_path TEXT")

    conn.commit()
    conn.close()