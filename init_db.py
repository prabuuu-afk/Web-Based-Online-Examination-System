import sqlite3
import os

DB_PATH = "database/exam.db"

# Ensure database folder exists
os.makedirs("database", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# STUDENTS TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully")
