import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import os
import re
from PIL import Image
import io
import pandas as pd

# --------------------------
# Database Functions (Multi-Group Version)
# --------------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        cursor.execute("""
            SELECT role, group_name FROM users 
            WHERE LOWER(username) = LOWER(?) AND password = ?
        """, (username, hashed_password))
        result = cursor.fetchone()
        return (result[0], result[1]) if result else (None, None)
    finally:
        conn.close()

def init_db():
    os.makedirs("data", exist_ok=True)
    db_path = "data/requests.db"
    
    try:
        # Check if we can access the database file
        if os.path.exists(db_path):
            # Verify the database is not corrupted
            try:
                test_conn = sqlite3.connect(db_path)
                test_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                test_conn.close()
            except sqlite3.DatabaseError:
                # Database is corrupted, remove it
                os.remove(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create tables with error handling
        try:
            # Your existing table creation code here
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT CHECK(role IN ('agent', 'admin')),
                    group_name TEXT DEFAULT 'General')
            """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                group_name TEXT,
                request_type TEXT,
                identifier TEXT,
                comment TEXT,
                timestamp TEXT,
                completed INTEGER DEFAULT 0)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mistakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT,
                team_leader TEXT,
                agent_name TEXT,
                ticket_id TEXT,
                error_description TEXT,
                timestamp TEXT)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT,
                sender TEXT,
                message TEXT,
                timestamp TEXT,
                mentions TEXT)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hold_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT,
                uploader TEXT,
                image_data BLOB,
                timestamp TEXT)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY DEFAULT 1,
                killswitch_enabled INTEGER DEFAULT 0,
                chat_killswitch_enabled INTEGER DEFAULT 0)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS breaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT,
                break_name TEXT,
                start_time TEXT,
                end_time TEXT,
                max_users INTEGER,
                current_users INTEGER DEFAULT 0,
                created_by TEXT,
                timestamp TEXT)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS break_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT,
                break_id INTEGER,
                user_id INTEGER,
                username TEXT,
                booking_date TEXT,
                timestamp TEXT,
                FOREIGN KEY(break_id) REFERENCES breaks(id))
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS request_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT,
                request_id INTEGER,
                user TEXT,
                comment TEXT,
                timestamp TEXT,
                FOREIGN KEY(request_id) REFERENCES requests(id))
        """)
        
        # Initialize system settings
        cursor.execute("""
            INSERT OR IGNORE INTO system_settings (id, killswitch_enabled, chat_killswitch_enabled)
            VALUES (1, 0, 0)
        """)
        
        # Create default groups
        default_groups = ['Spanish', 'French', 'English', 'General']
        for group in default_groups:
            cursor.execute("""
                INSERT OR IGNORE INTO groups (group_name, created_at)
                VALUES (?, ?)
            """, (group, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        # Create admin accounts
        admin_accounts = [
            ("taha kirri", "arise@99", "admin", "General"),
            ("Issam Samghini", "admin@2025", "admin", "General"),
            ("Loubna Fellah", "admin@99", "admin", "General"),
            ("Youssef Kamal", "admin@006", "admin", "General"),
            ("Fouad Fathi", "admin@55", "admin", "General")
        ]
        
        for username, password, role, group in admin_accounts:
            cursor.execute("""
                INSERT OR IGNORE INTO users (username, password, role, group_name)
                VALUES (?, ?, ?, ?)
            """, (username, hash_password(password), role, group))
        
        # Create agent accounts with group assignments
        spanish_agents = [
            ("Karabila Younes", "30866", "Spanish"),
            ("Kaoutar Mzara", "30514", "Spanish"),
            ("Ben Tahar Chahid", "30864", "Spanish")
        ]
        
        french_agents = [
            ("Lekhmouchi Kamal", "30869", "French"),
            ("Said Kilani", "30626", "French"),
            ("AGLIF Rachid", "30830", "French")
        ]
        
        english_agents = [
            ("Yacine Adouha", "30577", "English"),
            ("Manal Elanbi", "30878", "English"),
            ("Jawad Ouassaddine", "30559", "English")
        ]
        
        all_agents = spanish_agents + french_agents + english_agents
        
        for agent_name, workspace_id, group in all_agents:
            cursor.execute("""
                INSERT OR IGNORE INTO users (username, password, role, group_name)
                VALUES (?, ?, ?, ?)
            """, (agent_name, hash_password(workspace_id), "agent", group))
        
        conn.commit()
    finally:
        conn.close()

def is_killswitch_enabled():
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT killswitch_enabled FROM system_settings WHERE id = 1")
        result = cursor.fetchone()
        return bool(result[0]) if result else False
    finally:
        conn.close()

def is_chat_killswitch_enabled():
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_killswitch_enabled FROM system_settings WHERE id = 1")
        result = cursor.fetchone()
        return bool(result[0]) if result else False
    finally:
        conn.close()

def toggle_killswitch(enable):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE system_settings SET killswitch_enabled = ? WHERE id = 1",
                      (1 if enable else 0,))
        conn.commit()
        return True
    finally:
        conn.close()

def toggle_chat_killswitch(enable):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE system_settings SET chat_killswitch_enabled = ? WHERE id = 1",
                      (1 if enable else 0,))
        conn.commit()
        return True
    finally:
        conn.close()

def add_request(agent_name, group_name, request_type, identifier, comment):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO requests (agent_name, group_name, request_type, identifier, comment, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (agent_name, group_name, request_type, identifier, comment, timestamp))
        
        request_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO request_comments (group_name, request_id, user, comment, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (group_name, request_id, agent_name, f"Request created: {comment}", timestamp))
        
        conn.commit()
        return True
    finally:
        conn.close()

def get_requests(group_name):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM requests 
            WHERE group_name = ? 
            ORDER BY timestamp DESC
        """, (group_name,))
        return cursor.fetchall()
    finally:
        conn.close()

def search_requests(group_name, query):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        query = f"%{query.lower()}%"
        cursor.execute("""
            SELECT * FROM requests 
            WHERE group_name = ?
            AND (LOWER(agent_name) LIKE ? 
            OR LOWER(request_type) LIKE ? 
            OR LOWER(identifier) LIKE ? 
            OR LOWER(comment) LIKE ?)
            ORDER BY timestamp DESC
        """, (group_name, query, query, query, query))
        return cursor.fetchall()
    finally:
        conn.close()

def update_request_status(request_id, completed):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE requests SET completed = ? WHERE id = ?",
                      (1 if completed else 0, request_id))
        conn.commit()
        return True
    finally:
        conn.close()

def add_request_comment(group_name, request_id, user, comment):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO request_comments (group_name, request_id, user, comment, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (group_name, request_id, user, comment, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    finally:
        conn.close()

def get_request_comments(group_name, request_id):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM request_comments 
            WHERE group_name = ? AND request_id = ?
            ORDER BY timestamp ASC
        """, (group_name, request_id))
        return cursor.fetchall()
    finally:
        conn.close()

def add_mistake(group_name, team_leader, agent_name, ticket_id, error_description):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO mistakes (group_name, team_leader, agent_name, ticket_id, error_description, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (group_name, team_leader, agent_name, ticket_id, error_description,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    finally:
        conn.close()

def get_mistakes(group_name):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM mistakes 
            WHERE group_name = ?
            ORDER BY timestamp DESC
        """, (group_name,))
        return cursor.fetchall()
    finally:
        conn.close()

def search_mistakes(group_name, query):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        query = f"%{query.lower()}%"
        cursor.execute("""
            SELECT * FROM mistakes 
            WHERE group_name = ?
            AND (LOWER(agent_name) LIKE ? 
            OR LOWER(ticket_id) LIKE ? 
            OR LOWER(error_description) LIKE ?)
            ORDER BY timestamp DESC
        """, (group_name, query, query, query))
        return cursor.fetchall()
    finally:
        conn.close()

def send_group_message(group_name, sender, message):
    if is_killswitch_enabled() or is_chat_killswitch_enabled():
        st.error("Chat is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        mentions = re.findall(r'@(\w+)', message)
        cursor.execute("""
            INSERT INTO group_messages (group_name, sender, message, timestamp, mentions) 
            VALUES (?, ?, ?, ?, ?)
        """, (group_name, sender, message, 
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
             ','.join(mentions)))
        conn.commit()
        return True
    finally:
        conn.close()

def get_group_messages(group_name):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM group_messages 
            WHERE group_name = ?
            ORDER BY timestamp DESC LIMIT 50
        """, (group_name,))
        return cursor.fetchall()
    finally:
        conn.close()

def get_all_users():
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, group_name FROM users")
        return cursor.fetchall()
    finally:
        conn.close()

def add_user(username, password, role, group_name):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password, role, group_name) 
            VALUES (?, ?, ?, ?)
        """, (username, hash_password(password), role, group_name))
        conn.commit()
        return True
    finally:
        conn.close()

def delete_user(user_id):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def update_user_group(user_id, new_group):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET group_name = ? WHERE id = ?",
                      (new_group, user_id))
        conn.commit()
        return True
    finally:
        conn.close()

def add_hold_image(group_name, uploader, image_data):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hold_images (group_name, uploader, image_data, timestamp) 
            VALUES (?, ?, ?, ?)
        """, (group_name, uploader, image_data, 
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    finally:
        conn.close()

def get_hold_images(group_name):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM hold_images 
            WHERE group_name = ?
            ORDER BY timestamp DESC
        """, (group_name,))
        return cursor.fetchall()
    finally:
        conn.close()

def clear_hold_images(group_name=None):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        if group_name:
            cursor.execute("DELETE FROM hold_images WHERE group_name = ?", (group_name,))
        else:
            cursor.execute("DELETE FROM hold_images")
        conn.commit()
        return True
    finally:
        conn.close()

def clear_all_requests(group_name=None):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        if group_name:
            cursor.execute("DELETE FROM requests WHERE group_name = ?", (group_name,))
            cursor.execute("DELETE FROM request_comments WHERE group_name = ?", (group_name,))
        else:
            cursor.execute("DELETE FROM requests")
            cursor.execute("DELETE FROM request_comments")
        conn.commit()
        return True
    finally:
        conn.close()

def clear_all_mistakes(group_name=None):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        if group_name:
            cursor.execute("DELETE FROM mistakes WHERE group_name = ?", (group_name,))
        else:
            cursor.execute("DELETE FROM mistakes")
        conn.commit()
        return True
    finally:
        conn.close()

def clear_all_group_messages(group_name=None):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        if group_name:
            cursor.execute("DELETE FROM group_messages WHERE group_name = ?", (group_name,))
        else:
            cursor.execute("DELETE FROM group_messages")
        conn.commit()
        return True
    finally:
        conn.close()

def add_break_slot(group_name, break_name, start_time, end_time, max_users, created_by):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO breaks (group_name, break_name, start_time, end_time, max_users, created_by, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (group_name, break_name, start_time, end_time, max_users, created_by,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    finally:
        conn.close()

def get_all_break_slots(group_name=None):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        if group_name:
            cursor.execute("""
                SELECT * FROM breaks 
                WHERE group_name = ?
                ORDER BY start_time
            """, (group_name,))
        else:
            cursor.execute("SELECT * FROM breaks ORDER BY start_time")
        return cursor.fetchall()
    finally:
        conn.close()

def get_available_break_slots(group_name, date):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.* 
            FROM breaks b
            WHERE b.group_name = ?
            AND b.max_users > (
                SELECT COUNT(*) 
                FROM break_bookings bb 
                WHERE bb.break_id = b.id 
                AND bb.booking_date = ?
            )
            ORDER BY b.start_time
        """, (group_name, date))
        return cursor.fetchall()
    finally:
        conn.close()

def book_break_slot(group_name, break_id, user_id, username, booking_date):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO break_bookings (group_name, break_id, user_id, username, booking_date, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (group_name, break_id, user_id, username, booking_date,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    finally:
        conn.close()

def get_user_bookings(group_name, username, date):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bb.*, b.break_name, b.start_time, b.end_time
            FROM break_bookings bb
            JOIN breaks b ON bb.break_id = b.id
            WHERE bb.group_name = ? AND bb.username = ? AND bb.booking_date = ?
        """, (group_name, username, date))
        return cursor.fetchall()
    finally:
        conn.close()

def get_all_bookings(group_name, date):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bb.*, b.break_name, b.start_time, b.end_time, u.role
            FROM break_bookings bb
            JOIN breaks b ON bb.break_id = b.id
            JOIN users u ON bb.user_id = u.id
            WHERE bb.group_name = ? AND bb.booking_date = ?
            ORDER BY b.start_time, bb.username
        """, (group_name, date))
        return cursor.fetchall()
    finally:
        conn.close()

def delete_break_slot(break_id):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM breaks WHERE id = ?", (break_id,))
        cursor.execute("DELETE FROM break_bookings WHERE break_id = ?", (break_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def clear_all_break_bookings(group_name=None):
    if is_killswitch_enabled():
        st.error("System is currently locked. Please contact the developer.")
        return False
        
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        if group_name:
            cursor.execute("DELETE FROM break_bookings WHERE group_name = ?", (group_name,))
        else:
            cursor.execute("DELETE FROM break_bookings")
        conn.commit()
        return True
    finally:
        conn.close()

def get_all_groups():
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT group_name FROM groups ORDER BY group_name")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()

def add_group(group_name):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO groups (group_name, created_at)
            VALUES (?, ?)
        """, (group_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_group(group_name):
    conn = sqlite3.connect("data/requests.db")
    try:
        cursor = conn.cursor()
        
        # Delete all group-specific data
        cursor.execute("DELETE FROM requests WHERE group_name = ?", (group_name,))
        cursor.execute("DELETE FROM mistakes WHERE group_name = ?", (group_name,))
        cursor.execute("DELETE FROM group_messages WHERE group_name = ?", (group_name,))
        cursor.execute("DELETE FROM hold_images WHERE group_name = ?", (group_name,))
        cursor.execute("DELETE FROM breaks WHERE group_name = ?", (group_name,))
        cursor.execute("DELETE FROM break_bookings WHERE group_name = ?", (group_name,))
        cursor.execute("DELETE FROM request_comments WHERE group_name = ?", (group_name,))
        
        # Update users in this group to default group
        cursor.execute("UPDATE users SET group_name = 'General' WHERE group_name = ?", (group_name,))
        
        # Finally delete the group
        cursor.execute("DELETE FROM groups WHERE group_name = ?", (group_name,))
        
        conn.commit()
        return True
    finally:
        conn.close()

# --------------------------
# Fancy Number Checker Functions
# --------------------------

def is_sequential(digits, step=1):
    """Check if digits form a sequential pattern with given step"""
    try:
        return all(int(digits[i]) == int(digits[i-1]) + step for i in range(1, len(digits)))
    except:
        return False

def is_fancy_number(phone_number):
    clean_number = re.sub(r'\D', '', phone_number)
    
    # Get last 6 digits according to Lycamobile policy
    if len(clean_number) >= 6:
        last_six = clean_number[-6:]
        last_three = clean_number[-3:]
    else:
        return False, "Number too short (need at least 6 digits)"
    
    patterns = []
    
    # Special case for 13322866688
    if clean_number == "13322866688":
        patterns.append("Special VIP number (13322866688)")
    
    # Check for ABBBAA pattern (like 566655)
    if (len(last_six) == 6 and 
        last_six[0] == last_six[5] and 
        last_six[1] == last_six[2] == last_six[3] and 
        last_six[4] == last_six[0] and 
        last_six[0] != last_six[1]):
        patterns.append("ABBBAA pattern (e.g., 566655)")
    
    # Check for ABBBA pattern (like 233322)
    if (len(last_six) >= 5 and 
        last_six[0] == last_six[4] and 
        last_six[1] == last_six[2] == last_six[3] and 
        last_six[0] != last_six[1]):
        patterns.append("ABBBA pattern (e.g., 233322)")
    
    # 1. 6-digit patterns (strict matches only)
    # All same digits (666666)
    if len(set(last_six)) == 1:
        patterns.append("6 identical digits")
        
    # Consecutive ascending (123456)
    if is_sequential(last_six, 1):
        patterns.append("6-digit ascending sequence")
        
    # Consecutive descending (654321)
    if is_sequential(last_six, -1):
        patterns.append("6-digit descending sequence")
        
    # Palindrome (100001)
    if last_six == last_six[::-1]:
        patterns.append("6-digit palindrome")
    
    # 2. 3-digit patterns (strict matches from image)
    first_triple = last_six[:3]
    second_triple = last_six[3:]
    
    # Double triplets (444555)
    if len(set(first_triple)) == 1 and len(set(second_triple)) == 1 and first_triple != second_triple:
        patterns.append("Double triplets (444555)")
    
    # Similar triplets (121122)
    if (first_triple[0] == first_triple[1] and 
        second_triple[0] == second_triple[1] and 
        first_triple[2] == second_triple[2]):
        patterns.append("Similar triplets (121122)")
    
    # Repeating triplets (786786)
    if first_triple == second_triple:
        patterns.append("Repeating triplets (786786)")
    
    # Nearly sequential (457456) - exactly 1 digit difference
    if abs(int(first_triple) - int(second_triple)) == 1:
        patterns.append("Nearly sequential triplets (457456)")
    
    # 3. 2-digit patterns (strict matches from image)
    # Incremental pairs (111213)
    pairs = [last_six[i:i+2] for i in range(0, 5, 1)]
    try:
        if all(int(pairs[i]) == int(pairs[i-1]) + 1 for i in range(1, len(pairs))):
            patterns.append("Incremental pairs (111213)")
    
        # Repeating pairs (202020)
        if (pairs[0] == pairs[2] == pairs[4] and 
            pairs[1] == pairs[3] and 
            pairs[0] != pairs[1]):
            patterns.append("Repeating pairs (202020)")
    
        # Alternating pairs (010101)
        if (pairs[0] == pairs[2] == pairs[4] and 
            pairs[1] == pairs[3] and 
            pairs[0] != pairs[1]):
            patterns.append("Alternating pairs (010101)")
    
        # Stepping pairs (324252) - Fixed this check
        if (all(int(pairs[i][0]) == int(pairs[i-1][0]) + 1 for i in range(1, len(pairs))) and
            all(int(pairs[i][1]) == int(pairs[i-1][1]) + 2 for i in range(1, len(pairs)))):
            patterns.append("Stepping pairs (324252)")
    except:
        pass
    
    # 4. Exceptional cases (must match exactly)
    exceptional_triplets = ['123', '555', '777', '999']
    if last_three in exceptional_triplets:
        patterns.append(f"Exceptional case ({last_three})")
    
    # Strict validation - only allow patterns that exactly match our rules
    valid_patterns = []
    for p in patterns:
        if any(rule in p for rule in [
            "Special VIP number",
            "ABBBAA pattern",
            "ABBBA pattern",
            "6 identical digits",
            "6-digit ascending sequence",
            "6-digit descending sequence",
            "6-digit palindrome",
            "Double triplets (444555)",
            "Similar triplets (121122)",
            "Repeating triplets (786786)",
            "Nearly sequential triplets (457456)",
            "Incremental pairs (111213)",
            "Repeating pairs (202020)",
            "Alternating pairs (010101)",
            "Stepping pairs (324252)",
            "Exceptional case"
        ]):
            valid_patterns.append(p)
    
    return bool(valid_patterns), ", ".join(valid_patterns) if valid_patterns else "No qualifying fancy pattern"

# --------------------------
# Streamlit App
# --------------------------

st.set_page_config(
    page_title="Multi-Group Request System",
    page_icon=":office:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styles
st.markdown("""
<style>
    .stApp { background-color: #121212; color: #E0E0E0; }
    [data-testid="stSidebar"] { background-color: #1E1E1E; }
    .stButton>button { background-color: #2563EB; color: white; }
    .card { background-color: #1F1F1F; border-radius: 12px; padding: 1.5rem; }
    .metric-card { background-color: #1F2937; border-radius: 10px; padding: 20px; }
    .killswitch-active {
        background-color: #4A1E1E;
        border-left: 5px solid #D32F2F;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #FFCDD2;
    }
    .chat-killswitch-active {
        background-color: #1E3A4A;
        border-left: 5px solid #1E88E5;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #B3E5FC;
    }
    .comment-box {
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: #2D2D2D;
        border-radius: 8px;
    }
    .comment-user {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.25rem;
    }
    .comment-text {
        margin-top: 0.5rem;
    }
    .group-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .fancy-number { color: #00ff00; font-weight: bold; }
    .normal-number { color: #ffffff; }
    .result-box { padding: 15px; border-radius: 5px; margin: 10px 0; }
    .fancy-result { background-color: #1e3d1e; border: 1px solid #00ff00; }
    .normal-result { background-color: #3d1e1e; border: 1px solid #ff0000; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False,
        "role": None,
        "group": None,
        "username": None,
        "current_section": "requests",
        "last_request_count": 0,
        "last_mistake_count": 0,
        "last_message_ids": []
    })

# Initialize database
init_db()

# Login page
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏢 Multi-Group Request System")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if username and password:
                    role, group = authenticate(username, password)
                    if role:
                        st.session_state.update({
                            "authenticated": True,
                            "role": role,
                            "group": group,
                            "username": username,
                            "last_request_count": len(get_requests(group)),
                            "last_mistake_count": len(get_mistakes(group)),
                            "last_message_ids": [msg[0] for msg in get_group_messages(group)]
                        })
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

# Main application
else:
    # System status indicators
    if is_killswitch_enabled():
        st.markdown("""
        <div class="killswitch-active">
            <h3>⚠️ SYSTEM LOCKED ⚠️</h3>
            <p>The system is currently in read-only mode.</p>
        </div>
        """, unsafe_allow_html=True)
    elif is_chat_killswitch_enabled():
        st.markdown("""
        <div class="chat-killswitch-active">
            <h3>⚠️ CHAT LOCKED ⚠️</h3>
            <p>The chat functionality is currently disabled.</p>
        </div>
        """, unsafe_allow_html=True)

    # Notification system
    def show_notifications():
        current_requests = get_requests(st.session_state.group)
        current_mistakes = get_mistakes(st.session_state.group)
        current_messages = get_group_messages(st.session_state.group)
        
        new_requests = len(current_requests) - st.session_state.last_request_count
        if new_requests > 0 and st.session_state.last_request_count > 0:
            st.toast(f"📋 {new_requests} new request(s) in your group!")
        
        new_mistakes = len(current_mistakes) - st.session_state.last_mistake_count
        if new_mistakes > 0 and st.session_state.last_mistake_count > 0:
            st.toast(f"❌ {new_mistakes} new mistake(s) in your group!")
        
        current_message_ids = [msg[0] for msg in current_messages]
        new_messages = [msg for msg in current_messages if msg[0] not in st.session_state.last_message_ids]
        
        for msg in new_messages:
            if msg[2] != st.session_state.username:  # msg[2] is sender
                mentions = msg[5].split(',') if msg[5] else []  # msg[5] is mentions
                if st.session_state.username in mentions:
                    st.toast(f"💬 You were mentioned by {msg[2]} in group chat!")
                else:
                    st.toast(f"💬 New message from {msg[2]} in group chat!")
        
        # Update session state
        st.session_state.last_request_count = len(current_requests)
        st.session_state.last_mistake_count = len(current_mistakes)
        st.session_state.last_message_ids = current_message_ids

    show_notifications()

    # Sidebar navigation
    with st.sidebar:
        st.title(f"👋 {st.session_state.username}")
        st.markdown(f"""
        <div class="group-badge" style="background-color: #3b82f6; color: white;">
            {st.session_state.group}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        # Navigation options
        nav_options = [
            ("📋 Requests", "requests"),
            ("📊 Dashboard", "dashboard"),
            ("☕ Breaks", "breaks"),
            ("🖼️ HOLD", "hold"),
            ("❌ Mistakes", "mistakes"),
            ("💬 Group Chat", "chat"),
            ("📱 Fancy Number", "fancy_number")
        ]
        
        if st.session_state.role == "admin":
            nav_options.append(("⚙️ Admin", "admin"))
        
        for option, value in nav_options:
            if st.button(option, key=f"nav_{value}"):
                st.session_state.current_section = value
                
        st.markdown("---")
        
        # Notification summary
        pending_requests = len([r for r in get_requests(st.session_state.group) if not r[7]])  # index 7 is completed
        new_mistakes = len(get_mistakes(st.session_state.group))
        unread_messages = len([m for m in get_group_messages(st.session_state.group) 
                             if m[0] not in st.session_state.last_message_ids 
                             and m[2] != st.session_state.username])  # index 2 is sender
        
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <h4>🔔 Group Notifications</h4>
            <p>📋 Pending requests: {pending_requests}</p>
            <p>❌ Recent mistakes: {new_mistakes}</p>
            <p>💬 Unread messages: {unread_messages}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # Main content area
    st.title(f"{st.session_state.current_section.title()} - {st.session_state.group}")

    # Requests section
    if st.session_state.current_section == "requests":
        if not is_killswitch_enabled():
            with st.expander("➕ Submit New Request"):
                with st.form("request_form"):
                    cols = st.columns([1, 3])
                    request_type = cols[0].selectbox("Type", ["Email", "Phone", "Ticket"])
                    identifier = cols[1].text_input("Identifier")
                    comment = st.text_area("Comment")
                    if st.form_submit_button("Submit"):
                        if identifier and comment:
                            if add_request(st.session_state.username, st.session_state.group, 
                                         request_type, identifier, comment):
                                st.success("Request submitted successfully!")
                                st.rerun()
        
        st.subheader("🔍 Search Requests")
        search_query = st.text_input("Search requests...")
        requests = search_requests(st.session_state.group, search_query) if search_query else get_requests(st.session_state.group)
        
        st.subheader(f"{st.session_state.group} Requests")
        for req in requests:
            req_id, agent, group, req_type, identifier, comment, timestamp, completed = req
            with st.container():
                cols = st.columns([0.1, 0.9])
                with cols[0]:
                    if not is_killswitch_enabled():
                        st.checkbox("Done", value=bool(completed), 
                                   key=f"check_{req_id}", 
                                   on_change=update_request_status,
                                   args=(req_id, not completed))
                    else:
                        st.checkbox("Done", value=bool(completed), disabled=True)
                with cols[1]:
                    st.markdown(f"""
                    <div class="card">
                        <div style="display: flex; justify-content: space-between;">
                            <h4>#{req_id} - {req_type}</h4>
                            <small>{timestamp}</small>
                        </div>
                        <p>Agent: {agent}</p>
                        <p>Identifier: {identifier}</p>
                        <div style="margin-top: 1rem;">
                            <h5>Status Updates:</h5>
                    """, unsafe_allow_html=True)
                    
                    comments = get_request_comments(st.session_state.group, req_id)
                    for comment in comments:
                        cmt_id, cmt_group, req_id, user, cmt_text, cmt_time = comment
                        st.markdown(f"""
                            <div class="comment-box">
                                <div class="comment-user">
                                    <small><strong>{user}</strong></small>
                                    <small>{cmt_time}</small>
                                </div>
                                <div class="comment-text">{cmt_text}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if st.session_state.role == "admin" and not is_killswitch_enabled():
                        with st.form(key=f"comment_form_{req_id}"):
                            new_comment = st.text_input("Add status update/comment")
                            if st.form_submit_button("Add Comment"):
                                if new_comment:
                                    add_request_comment(st.session_state.group, req_id, 
                                                       st.session_state.username, new_comment)
                                    st.rerun()

    # Dashboard section
    elif st.session_state.current_section == "dashboard":
        st.subheader(f"📊 {st.session_state.group} Dashboard")
        all_requests = get_requests(st.session_state.group)
        total = len(all_requests)
        completed = sum(1 for r in all_requests if r[7])  # index 7 is completed
        rate = (completed/total*100) if total > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Requests", total)
        with col2:
            st.metric("Completed", completed)
        with col3:
            st.metric("Completion Rate", f"{rate:.1f}%")
        
        df = pd.DataFrame({
            'Date': [datetime.strptime(r[6], "%Y-%m-%d %H:%M:%S").date() for r in all_requests],  # index 6 is timestamp
            'Status': ['Completed' if r[7] else 'Pending' for r in all_requests],
            'Type': [r[3] for r in all_requests]  # index 3 is request_type
        })
        
        st.subheader("Request Trends")
        st.bar_chart(df['Date'].value_counts())
        
        st.subheader("Request Type Distribution")
        type_counts = df['Type'].value_counts().reset_index()
        type_counts.columns = ['Type', 'Count']
        st.bar_chart(type_counts.set_index('Type'))

    # Breaks section
    elif st.session_state.current_section == "breaks":
        today = datetime.now().strftime("%Y-%m-%d")
        selected_date = st.date_input("Select date", datetime.now())
        formatted_date = selected_date.strftime("%Y-%m-%d")
        
        if st.session_state.role == "admin":
            st.subheader(f"Admin: {st.session_state.group} Break Schedule")
            
            with st.expander("➕ Add New Break Slot"):
                with st.form("add_break_form"):
                    cols = st.columns(3)
                    break_name = cols[0].text_input("Break Name")
                    start_time = cols[1].time_input("Start Time")
                    end_time = cols[2].time_input("End Time")
                    max_users = st.number_input("Max Users", min_value=1, value=1)
                    
                    if st.form_submit_button("Add Break Slot"):
                        if break_name:
                            add_break_slot(
                                st.session_state.group,
                                break_name,
                                start_time.strftime("%H:%M"),
                                end_time.strftime("%H:%M"),
                                max_users,
                                st.session_state.username
                            )
                            st.rerun()
            
            st.subheader("Current Break Schedule")
            breaks = get_all_break_slots(st.session_state.group)
            for b in breaks:
                b_id, group, name, start, end, max_u, curr_u, created_by, ts = b
                with st.container():
                    cols = st.columns([3, 2, 2, 1, 1])
                    cols[0].write(f"{name} ({start} - {end})")
                    cols[1].write(f"Max: {max_u}")
                    cols[2].write(f"Created by: {created_by}")
                    
                    if cols[3].button("✏️", key=f"edit_{b_id}"):
                        pass
                    
                    if cols[4].button("❌", key=f"del_{b_id}"):
                        delete_break_slot(b_id)
                        st.rerun()
            
            st.markdown("---")
            st.subheader(f"All Bookings for {formatted_date}")
            bookings = get_all_bookings(st.session_state.group, formatted_date)
            if bookings:
                for b in bookings:
                    b_id, group, break_id, user_id, username, date, ts, break_name, start, end, role = b
                    st.write(f"{username} ({role}) - {break_name} ({start} - {end})")
            else:
                st.info("No bookings for selected date")
            
            if st.button("Clear All Group Bookings", key="clear_group_bookings"):
                clear_all_break_bookings(st.session_state.group)
                st.rerun()
        
        else:
            st.subheader("Available Break Slots")
            available_breaks = get_available_break_slots(st.session_state.group, formatted_date)
            
            if available_breaks:
                for b in available_breaks:
                    b_id, group, name, start, end, max_u, curr_u, created_by, ts = b
                    
                    conn = sqlite3.connect("data/requests.db")
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM break_bookings 
                        WHERE break_id = ? AND booking_date = ? AND group_name = ?
                    """, (b_id, formatted_date, st.session_state.group))
                    booked_count = cursor.fetchone()[0]
                    conn.close()
                    
                    remaining = max_u - booked_count
                    
                    with st.container():
                        cols = st.columns([3, 2, 1])
                        cols[0].write(f"*{name}* ({start} - {end})")
                        cols[1].write(f"Available slots: {remaining}/{max_u}")
                        
                        if cols[2].button("Book", key=f"book_{b_id}"):
                            conn = sqlite3.connect("data/requests.db")
                            cursor = conn.cursor()
                            cursor.execute("SELECT id FROM users WHERE username = ?", 
                                         (st.session_state.username,))
                            user_id = cursor.fetchone()[0]
                            conn.close()
                            
                            book_break_slot(st.session_state.group, b_id, user_id, 
                                          st.session_state.username, formatted_date)
                            st.rerun()
            
            st.markdown("---")
            st.subheader("Your Bookings")
            user_bookings = get_user_bookings(st.session_state.group, st.session_state.username, formatted_date)
            
            if user_bookings:
                for b in user_bookings:
                    b_id, group, break_id, user_id, username, date, ts, break_name, start, end = b
                    st.write(f"{break_name} ({start} - {end})")
            else:
                st.info("You have no bookings for selected date")

    # Mistakes section
    elif st.session_state.current_section == "mistakes":
        if not is_killswitch_enabled():
            with st.expander("➕ Report New Mistake"):
                with st.form("mistake_form"):
                    cols = st.columns(3)
                    agent_name = cols[0].text_input("Agent Name")
                    ticket_id = cols[1].text_input("Ticket ID")
                    error_description = st.text_area("Error Description")
                    if st.form_submit_button("Submit"):
                        if agent_name and ticket_id and error_description:
                            add_mistake(st.session_state.group, st.session_state.username, 
                                       agent_name, ticket_id, error_description)
        
        st.subheader("🔍 Search Mistakes")
        search_query = st.text_input("Search mistakes...")
        mistakes = search_mistakes(st.session_state.group, search_query) if search_query else get_mistakes(st.session_state.group)
        
        st.subheader(f"{st.session_state.group} Mistakes Log")
        for mistake in mistakes:
            m_id, group, tl, agent, ticket, error, ts = mistake
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between;">
                    <h4>#{m_id}</h4>
                    <small>{ts}</small>
                </div>
                <p>Agent: {agent}</p>
                <p>Ticket: {ticket}</p>
                <p>Error: {error}</p>
            </div>
            """, unsafe_allow_html=True)

    # Group Chat section
    elif st.session_state.current_section == "chat":
        if is_chat_killswitch_enabled():
            st.warning("Chat functionality is currently disabled by the administrator.")
        else:
            messages = get_group_messages(st.session_state.group)
            for msg in reversed(messages):
                msg_id, group, sender, message, ts, mentions = msg
                is_mentioned = st.session_state.username in (mentions.split(',') if mentions else [])
                st.markdown(f"""
                <div style="background-color: {'#3b82f6' if is_mentioned else '#1F1F1F'};
                            padding: 1rem;
                            border-radius: 8px;
                            margin-bottom: 1rem;">
                    <strong>{sender}</strong>: {message}<br>
                    <small>{ts}</small>
                </div>
                """, unsafe_allow_html=True)
            
            if not is_killswitch_enabled():
                with st.form("chat_form"):
                    message = st.text_input("Type your message...")
                    if st.form_submit_button("Send"):
                        if message:
                            send_group_message(st.session_state.group, st.session_state.username, message)
                            st.rerun()

    # HOLD section
    elif st.session_state.current_section == "hold":
        if st.session_state.role == "admin" and not is_killswitch_enabled():
            with st.expander("📤 Upload Image"):
                img = st.file_uploader("Choose image", type=["jpg", "png", "jpeg"])
                if img:
                    add_hold_image(st.session_state.group, st.session_state.username, img.read())
        
        images = get_hold_images(st.session_state.group)
        if images:
            for img in images:
                iid, group, uploader, data, ts = img
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between;">
                        <h4>Image #{iid}</h4>
                        <small>{ts}</small>
                    </div>
                    <p>Uploaded by: {uploader}</p>
                </div>
                """, unsafe_allow_html=True)
                st.image(Image.open(io.BytesIO(data)), use_column_width=True)
        else:
            st.info("No images in HOLD")

    # Fancy Number section
    elif st.session_state.current_section == "fancy_number":
        st.header("📱 Lycamobile Fancy Number Checker")
        st.subheader("Official Policy: Analyzes last 6 digits only for qualifying patterns")

        phone_input = st.text_input("Enter Phone Number", 
                                  placeholder="e.g., 1555123456 or 44207123456")

        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("🔍 Check Number"):
                if not phone_input:
                    st.warning("Please enter a phone number")
                else:
                    is_fancy, pattern = is_fancy_number(phone_input)
                    clean_number = re.sub(r'\D', '', phone_input)
                    
                    # Extract last 6 digits for display
                    last_six = clean_number[-6:] if len(clean_number) >= 6 else clean_number
                    formatted_num = f"{last_six[:3]}-{last_six[3:]}" if len(last_six) == 6 else last_six

                    if is_fancy:
                        st.markdown(f"""
                        <div class="result-box fancy-result">
                            <h3><span class="fancy-number">✨ {formatted_num} ✨</span></h3>
                            <p>FANCY NUMBER DETECTED!</p>
                            <p><strong>Pattern:</strong> {pattern}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="result-box normal-result">
                            <h3><span class="normal-number">{formatted_num}</span></h3>
                            <p>Standard phone number</p>
                            <p><strong>Reason:</strong> {pattern}</p>
                        </div>
                        """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            ### Lycamobile Fancy Number Policy
            **Qualifying Patterns (last 6 digits only):**
            
            #### 6-Digit Patterns
            - 123456 (ascending)
            - 987654 (descending)
            - 666666 (repeating)
            - 100001 (palindrome)
            
            #### 3-Digit Patterns  
            - 444 555 (double triplets)
            - 121 122 (similar triplets)
            - 786 786 (repeating triplets)
            - 457 456 (nearly sequential)
            
            #### 2-Digit Patterns
            - 11 12 13 (incremental)
            - 20 20 20 (repeating)
            - 01 01 01 (alternating)
            - 32 42 52 (stepping)
            
            #### Exceptional Cases
            - Ending with 123/555/777/999
            """)

    # Admin section
    elif st.session_state.current_section == "admin" and st.session_state.role == "admin":
        if st.session_state.username.lower() == "taha kirri":
            st.subheader("🚨 System Killswitch")
            current = is_killswitch_enabled()
            status = "🔴 ACTIVE" if current else "🟢 INACTIVE"
            st.write(f"Current Status: {status}")
            
            col1, col2 = st.columns(2)
            if current:
                if col1.button("Deactivate Killswitch"):
                    toggle_killswitch(False)
                    st.rerun()
            else:
                if col1.button("Activate Killswitch"):
                    toggle_killswitch(True)
                    st.rerun()
            
            st.markdown("---")
            
            st.subheader("💬 Chat Killswitch")
            current_chat = is_chat_killswitch_enabled()
            chat_status = "🔴 ACTIVE" if current_chat else "🟢 INACTIVE"
            st.write(f"Current Status: {chat_status}")
            
            col1, col2 = st.columns(2)
            if current_chat:
                if col1.button("Deactivate Chat Killswitch"):
                    toggle_chat_killswitch(False)
                    st.rerun()
            else:
                if col1.button("Activate Chat Killswitch"):
                    toggle_chat_killswitch(True)
                    st.rerun()
            
            st.markdown("---")
        
        st.subheader("🧹 Data Management")
        
        with st.expander("❌ Clear All Requests (Current Group)"):
            with st.form("clear_requests_form"):
                st.warning("This will permanently delete ALL requests for your group!")
                if st.form_submit_button("Clear Group Requests"):
                    if clear_all_requests(st.session_state.group):
                        st.success("All group requests deleted!")
                        st.rerun()

        with st.expander("❌ Clear All Mistakes (Current Group)"):
            with st.form("clear_mistakes_form"):
                st.warning("This will permanently delete ALL mistakes for your group!")
                if st.form_submit_button("Clear Group Mistakes"):
                    if clear_all_mistakes(st.session_state.group):
                        st.success("All group mistakes deleted!")
                        st.rerun()

        with st.expander("❌ Clear All Chat Messages (Current Group)"):
            with st.form("clear_chat_form"):
                st.warning("This will permanently delete ALL chat messages for your group!")
                if st.form_submit_button("Clear Group Chat"):
                    if clear_all_group_messages(st.session_state.group):
                        st.success("All group chat messages deleted!")
                        st.rerun()

        with st.expander("❌ Clear All HOLD Images (Current Group)"):
            with st.form("clear_hold_form"):
                st.warning("This will permanently delete ALL HOLD images for your group!")
                if st.form_submit_button("Clear Group HOLD Images"):
                    if clear_hold_images(st.session_state.group):
                        st.success("All group HOLD images deleted!")
                        st.rerun()

        with st.expander("❌ Clear All Break Bookings (Current Group)"):
            with st.form("clear_breaks_form"):
                st.warning("This will permanently delete ALL break bookings for your group!")
                if st.form_submit_button("Clear Group Break Bookings"):
                    if clear_all_break_bookings(st.session_state.group):
                        st.success("All group break bookings deleted!")
                        st.rerun()

        st.markdown("---")
        st.subheader("Group Management")
        
        # Add new group
        with st.expander("➕ Add New Group"):
            with st.form("new_group_form"):
                new_group = st.text_input("Group Name")
                if st.form_submit_button("Create Group"):
                    if new_group:
                        if add_group(new_group):
                            st.success(f"Group '{new_group}' created!")
                            st.rerun()
                        else:
                            st.error("Group already exists!")
        
        # List all groups
        st.subheader("Existing Groups")
        groups = get_all_groups()
        for group in groups:
            cols = st.columns([3, 1])
            cols[0].write(group)
            if cols[1].button("Delete", key=f"del_group_{group}") and group != "General":
                if delete_group(group):
                    st.success(f"Group '{group}' deleted!")
                    st.rerun()
                else:
                    st.error("Could not delete group")
        
        st.markdown("---")
        st.subheader("User Management")
        
        # Add new user
        if not is_killswitch_enabled():
            with st.expander("➕ Add New User"):
                with st.form("add_user_form"):
                    user = st.text_input("Username")
                    pwd = st.text_input("Password", type="password")
                    role = st.selectbox("Role", ["agent", "admin"])
                    group = st.selectbox("Group", get_all_groups())
                    if st.form_submit_button("Add User"):
                        if user and pwd:
                            if add_user(user, pwd, role, group):
                                st.success("User added!")
                                st.rerun()
                            else:
                                st.error("Username already exists")
        
        # User list with group assignment
        st.subheader("Existing Users")
        users = get_all_users()
        for uid, uname, urole, ugroup in users:
            cols = st.columns([3, 1, 2, 1])
            cols[0].write(uname)
            cols[1].write(urole)
            new_group = cols[2].selectbox("Group", get_all_groups(), 
                                        index=get_all_groups().index(ugroup), 
                                        key=f"group_{uid}")
            if cols[3].button("Update", key=f"upd_{uid}"):
                update_user_group(uid, new_group)
                st.rerun()
if __name__ == "__main__":
    try:
        init_db()
        st.write("Multi-Group Request Management System")
    except Exception as e:
        st.error(f"Application failed to start: {str(e)}")
        st.error("Please contact support if this error persists.")
        
if __name__ == "__main__":
    st.write("Multi-Group Request Management System")
