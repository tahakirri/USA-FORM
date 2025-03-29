import streamlit as st
import sqlite3
from datetime import datetime
import os

# Initialize database with proper path handling
def init_db():
    # Get absolute path to database file
    db_path = os.path.abspath("break_schedule.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        team TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS breaks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        break_name TEXT,
        start_time TEXT,
        end_time TEXT,
        max_users INTEGER,
        created_by TEXT,
        timestamp TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS break_bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        break_id INTEGER,
        user_id INTEGER,
        username TEXT,
        booking_date TEXT,
        timestamp TEXT,
        FOREIGN KEY(break_id) REFERENCES breaks(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    # Create admin users if they don't exist
    admin_users = [
        ("admin", "admin123", "admin", "Management"),
        ("taha_kirri", "taha123", "admin", "Management")
    ]
    
    for username, password, role, team in admin_users:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, role, team) VALUES (?, ?, ?, ?)",
                (username, password, role, team)
            )
    
    conn.commit()
    conn.close()

# [Keep all the helper functions from previous version unchanged]
# ... (Include all the helper functions exactly as in previous response)

# Initialize the database
init_db()

# [Keep the rest of the code exactly as in previous response]
# ... (Include login_section, breaks_section, and main function unchanged)
