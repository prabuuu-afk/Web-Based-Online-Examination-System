import sqlite3
import os

DB_PATH = "database/exam.db"

# Ensure database folder exists
os.makedirs("database", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -----------------------------
# CREATE STAFF TABLE
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)
""")

# -----------------------------
# CREATE STUDENTS TABLE
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)
""")

# -----------------------------
# INSERT DEFAULT ADMIN
# -----------------------------
cursor.execute("""
INSERT OR IGNORE INTO staff (username, password, email)
VALUES ('admin', 'admin123', 'admin@example.com')
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully!")
print("👉 Admin login: admin / admin123")
