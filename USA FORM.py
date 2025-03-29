import streamlit as st
import sqlite3
import os
from datetime import datetime

# Initialize database with proper path handling
def init_db():
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect("data/break_schedule.db")
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
        timestamp TEXT,
        shift_type TEXT
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
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_name TEXT UNIQUE,
        breaks_json TEXT,
        rules_json TEXT,
        created_by TEXT,
        timestamp TEXT
    )
    """)
    
    # Create default users if they don't exist
    default_users = [
        ("admin", "admin123", "admin", "Management"),
        ("taha_kirri", "taha123", "admin", "Management"),
        ("agent1", "agent123", "agent", "Team A"),
        ("agent2", "agent123", "agent", "Team B")
    ]
    
    for username, password, role, team in default_users:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, role, team) VALUES (?, ?, ?, ?)",
                (username, password, role, team)
            )
    
    # Create default templates if they don't exist
    default_templates = [
        {
            "name": "USA ENGLISH FIRST SHIFT",
            "breaks": [
                {"name": "TEABREAK", "start": "16:00", "end": "16:15", "max_users": 5},
                {"name": "TEABREAK", "start": "16:15", "end": "16:30", "max_users": 5},
                {"name": "TEABREAK", "start": "16:30", "end": "16:45", "max_users": 5},
                {"name": "TEABREAK", "start": "16:45", "end": "17:00", "max_users": 5},
                {"name": "TEABREAK", "start": "17:00", "end": "17:15", "max_users": 5},
                {"name": "TEABREAK", "start": "17:15", "end": "17:30", "max_users": 5},
                {"name": "TEABREAK", "start": "21:45", "end": "22:00", "max_users": 5},
                {"name": "TEABREAK", "start": "22:00", "end": "22:15", "max_users": 5},
                {"name": "TEABREAK", "start": "22:15", "end": "22:30", "max_users": 5}
            ],
            "rules": [
                "NO BREAK IN THE LAST HOUR WILL BE AUTHORIZED",
                "PS. ONLY 5 MINUTES BIO IS AUTHORIZED IN THE LAST HOUR BETWEEN 23:00 TILL 23:30 AND NO BREAK AFTER 23:30 !!!",
                "BREAKS SHOULD BE TAKEN AT THE NOTED TIME AND NEED TO BE CONFIRMED FROM RTA OR TEAM LEADERS"
            ]
        },
        {
            "name": "USA ENGLISH SECOND SHIFT",
            "breaks": [
                {"name": "TEABREAK", "start": "19:30", "end": "20:00", "max_users": 5},
                {"name": "TEABREAK", "start": "20:00", "end": "20:30", "max_users": 5},
                {"name": "TEABREAK", "start": "20:30", "end": "21:00", "max_users": 5},
                {"name": "TEABREAK", "start": "21:00", "end": "21:30", "max_users": 5}
            ],
            "rules": [
                "Non Respect Of Break Rules = Incident",
                "BREAKS SHOULD BE TAKEN AT THE NOTED TIME AND NEED TO BE CONFIRMED FROM RTA OR TEAM LEADERS"
            ]
        },
        {
            "name": "USA SPANISH FIRST SHIFT",
            "breaks": [
                {"name": "DESCANSO", "start": "16:00", "end": "16:15", "max_users": 5},
                {"name": "DESCANSO", "start": "16:15", "end": "16:30", "max_users": 5},
                {"name": "DESCANSO", "start": "16:30", "end": "16:45", "max_users": 5},
                {"name": "DESCANSO", "start": "16:45", "end": "17:00", "max_users": 5},
                {"name": "DESCANSO", "start": "17:00", "end": "17:15", "max_users": 5},
                {"name": "DESCANSO", "start": "17:15", "end": "17:30", "max_users": 5},
                {"name": "DESCANSO", "start": "21:45", "end": "22:00", "max_users": 5},
                {"name": "DESCANSO", "start": "22:00", "end": "22:15", "max_users": 5},
                {"name": "DESCANSO", "start": "22:15", "end": "22:30", "max_users": 5}
            ],
            "rules": [
                "NO SE AUTORIZARÁN DESCANSOS EN LA ÚLTIMA HORA",
                "¡¡¡SOLO SE AUTORIZAN 5 MINUTOS PARA BIO ENTRE LAS 23:00 Y LAS 23:30 Y NINGÚN DESCANSO DESPUÉS DE LAS 23:30!!!",
                "LOS DESCANSOS DEBEN TOMARSE EN EL TIEMPO NOTADO Y DEBEN SER CONFIRMADOS POR RTA O LÍDERES DE EQUIPO"
            ]
        },
        {
            "name": "USA SPANISH SECOND SHIFT",
            "breaks": [
                {"name": "DESCANSO", "start": "19:30", "end": "20:00", "max_users": 5},
                {"name": "DESCANSO", "start": "20:00", "end": "20:30", "max_users": 5},
                {"name": "DESCANSO", "start": "20:30", "end": "21:00", "max_users": 5},
                {"name": "DESCANSO", "start": "21:00", "end": "21:30", "max_users": 5}
            ],
            "rules": [
                "Incumplimiento de las reglas de descanso = Incidente",
                "LOS DESCANSOS DEBEN TOMARSE EN EL TIEMPO NOTADO Y DEBEN SER CONFIRMADOS POR RTA O LÍDERES DE EQUIPO"
            ]
        }
    ]
    
    for template in default_templates:
        cursor.execute("SELECT * FROM templates WHERE template_name = ?", (template["name"],))
        if not cursor.fetchone():
            import json
            cursor.execute(
                "INSERT INTO templates (template_name, breaks_json, rules_json, created_by, timestamp) VALUES (?, ?, ?, ?, ?)",
                (
                    template["name"],
                    json.dumps(template["breaks"]),
                    json.dumps(template["rules"]),
                    "system",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
    
    conn.commit()
    conn.close()

# Database helper functions
def get_available_break_slots(date, shift_type=None):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    
    if shift_type:
        cursor.execute("""
        SELECT 
            b.id, 
            b.break_name, 
            b.start_time, 
            b.end_time, 
            b.max_users,
            COUNT(bb.id) as current_users,
            b.created_by,
            b.timestamp
        FROM breaks b
        LEFT JOIN break_bookings bb ON b.id = bb.break_id AND bb.booking_date = ?
        WHERE b.shift_type = ?
        GROUP BY b.id
        ORDER BY b.start_time
        """, (date, shift_type))
    else:
        cursor.execute("""
        SELECT 
            b.id, 
            b.break_name, 
            b.start_time, 
            b.end_time, 
            b.max_users,
            COUNT(bb.id) as current_users,
            b.created_by,
            b.timestamp
        FROM breaks b
        LEFT JOIN break_bookings bb ON b.id = bb.break_id AND bb.booking_date = ?
        GROUP BY b.id
        ORDER BY b.start_time
        """, (date,))
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_user_bookings(username, date):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        bb.id,
        bb.break_id,
        bb.user_id,
        bb.username,
        bb.booking_date,
        bb.timestamp,
        b.break_name,
        b.start_time,
        b.end_time
    FROM break_bookings bb
    JOIN breaks b ON bb.break_id = b.id
    WHERE bb.username = ? AND bb.booking_date = ?
    ORDER BY b.start_time
    """, (username, date))
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_bookings(date, shift_type=None):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    
    if shift_type:
        cursor.execute("""
        SELECT 
            bb.id,
            bb.break_id,
            bb.user_id,
            bb.username,
            bb.booking_date,
            bb.timestamp,
            b.break_name,
            b.start_time,
            b.end_time,
            u.role
        FROM break_bookings bb
        JOIN breaks b ON bb.break_id = b.id
        JOIN users u ON bb.user_id = u.id
        WHERE bb.booking_date = ? AND b.shift_type = ?
        ORDER BY b.start_time
        """, (date, shift_type))
    else:
        cursor.execute("""
        SELECT 
            bb.id,
            bb.break_id,
            bb.user_id,
            bb.username,
            bb.booking_date,
            bb.timestamp,
            b.break_name,
            b.start_time,
            b.end_time,
            u.role
        FROM break_bookings bb
        JOIN breaks b ON bb.break_id = b.id
        JOIN users u ON bb.user_id = u.id
        WHERE bb.booking_date = ?
        ORDER BY b.start_time
        """, (date,))
    
    results = cursor.fetchall()
    conn.close()
    return results

def book_break_slot(break_id, user_id, username, date):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    
    # Check if user already has a booking for this time slot
    cursor.execute("""
    SELECT bb.id 
    FROM break_bookings bb
    JOIN breaks b ON bb.break_id = b.id
    WHERE bb.user_id = ? AND bb.booking_date = ? AND bb.break_id = ?
    """, (user_id, date, break_id))
    
    if cursor.fetchone():
        st.error("You already have a booking for this time slot!")
        return
    
    cursor.execute("""
    INSERT INTO break_bookings (break_id, user_id, username, booking_date, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """, (break_id, user_id, username, date, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()
    st.success("Break booked successfully!")

def clear_all_break_bookings(shift_type=None):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    
    if shift_type:
        # Get break IDs for this shift type
        cursor.execute("SELECT id FROM breaks WHERE shift_type = ?", (shift_type,))
        break_ids = [row[0] for row in cursor.fetchall()]
        
        if break_ids:
            # Delete bookings for these break IDs
            cursor.execute("DELETE FROM break_bookings WHERE break_id IN ({})".format(
                ','.join(['?']*len(break_ids))), break_ids)
    else:
        cursor.execute("DELETE FROM break_bookings")
    
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user[0],
            "username": user[1],
            "role": user[3],
            "team": user[4]
        }
    return None

def register_user(username, password, role, team):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role, team) VALUES (?, ?, ?, ?)",
            (username, password, role, team)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def add_break_slot(name, start, end, max_users, shift_type):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO breaks (break_name, start_time, end_time, max_users, created_by, timestamp, shift_type)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, start, end, max_users, st.session_state.username, 
          datetime.now().strftime("%Y-%m-%d %H:%M:%S"), shift_type))
    
    conn.commit()
    conn.close()

def delete_break_slot(break_id):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    
    # First delete any bookings for this break
    cursor.execute("DELETE FROM break_bookings WHERE break_id = ?", (break_id,))
    
    # Then delete the break itself
    cursor.execute("DELETE FROM breaks WHERE id = ?", (break_id,))
    
    conn.commit()
    conn.close()

def get_all_breaks(shift_type=None):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    
    if shift_type:
        cursor.execute("SELECT * FROM breaks WHERE shift_type = ? ORDER BY start_time", (shift_type,))
    else:
        cursor.execute("SELECT * FROM breaks ORDER BY start_time")
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_templates():
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM templates ORDER BY template_name")
    results = cursor.fetchall()
    conn.close()
    return results

def get_template_by_name(name):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM templates WHERE template_name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result

def save_template(name, breaks, rules):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    
    import json
    try:
        cursor.execute(
            "INSERT INTO templates (template_name, breaks_json, rules_json, created_by, timestamp) VALUES (?, ?, ?, ?, ?)",
            (name, json.dumps(breaks), json.dumps(rules), st.session_state.username, 
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_template(name):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM templates WHERE template_name = ?", (name,))
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Custom CSS for better layout
def load_css():
    st.markdown("""
    <style>
        .main {
            max-width: 1200px;
            padding: 2rem;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .break-card {
            background-color: #e9f7ef;
            border-left: 5px solid #2ecc71;
        }
        .booking-card {
            background-color: #f5e8ff;
            border-left: 5px solid #9b59b6;
        }
        .admin-card {
            background-color: #e3f2fd;
            border-left: 5px solid #3498db;
        }
        .btn-primary {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
        }
        .btn-danger {
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
        }
        .btn-success {
            background-color: #2ecc71;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
        }
        .availability-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 50px;
            font-weight: bold;
            font-size: 0.8rem;
        }
        .available {
            background-color: #2ecc71;
            color: white;
        }
        .full {
            background-color: #e74c3c;
            color: white;
        }
        .shift-selector {
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# Authentication
def login_section():
    load_css()
    st.markdown("""
    <div class="header">
        <h1>⏱️ Break Scheduling System</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Agent/Admin Login")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login", type="primary"):
                    user = login_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.username = user["username"]
                        st.session_state.role = user["role"]
                        st.session_state.team = user["team"]
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        
        with tab2:
            if st.session_state.get("role") == "admin":
                with st.form("register_form"):
                    st.subheader("Register New User")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_username = st.text_input("Username")
                        new_role = st.selectbox("Role", ["agent", "admin", "team_lead"])
                    with col2:
                        new_password = st.text_input("Password", type="password")
                        new_team = st.text_input("Team")
                    
                    if st.form_submit_button("Register User", type="primary"):
                        if register_user(new_username, new_password, new_role, new_team):
                            st.success("User registered successfully!")
                        else:
                            st.error("Username already exists")
            else:
                st.info("ℹ️ Only admins can register new users. Please login as admin.")
    else:
        st.sidebar.markdown(f"""
        <div class="card">
            <h3>👤 User Info</h3>
            <p><strong>Username:</strong> {st.session_state.username}</p>
            <p><strong>Role:</strong> {st.session_state.role.capitalize()}</p>
            <p><strong>Team:</strong> {st.session_state.team}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("🚪 Logout", type="primary"):
            st.session_state.authenticated = False
            st.session_state.clear()
            st.rerun()
        breaks_section()

# Break scheduling section
def breaks_section():
    load_css()
    
    today = datetime.now().strftime("%Y-%m-%d")
    selected_date = st.date_input("📅 Select date", datetime.now())
    formatted_date = selected_date.strftime("%Y-%m-%d")
    
    # Shift type selector (visible to all users)
    shift_type = st.selectbox(
        "Select Shift Type",
        ["All", "USA ENGLISH FIRST SHIFT", "USA ENGLISH SECOND SHIFT", 
         "USA SPANISH FIRST SHIFT", "USA SPANISH SECOND SHIFT"],
        key="shift_selector"
    )
    
    selected_shift = None if shift_type == "All" else shift_type

    # Admin section for managing templates
    if st.session_state.role == "admin":
        st.markdown("""
        <div class="header">
            <h2>🛠️ Admin Dashboard</h2>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Break Templates", "➕ Manage Breaks", "📊 View Bookings", "⚙️ Template Management"])
        
        with tab1:
            st.markdown("""
            <div class="card admin-card">
                <h3>Break Template Management</h3>
            </div>
            """, unsafe_allow_html=True)
            
            templates = get_all_templates()
            selected_template = st.selectbox(
                "Select Template", 
                [t[1] for t in templates],
                key="template_selector"
            )
            
            if selected_template:
                template = get_template_by_name(selected_template)
                if template:
                    import json
                    breaks = json.loads(template[2])
                    rules = json.loads(template[3])
                    
                    # Display rules
                    st.markdown("""
                    <div class="card">
                        <h4>📜 Break Rules</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for rule in rules:
                        st.markdown(f"""
                        <div class="card">
                            <p>• {rule}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Display breaks in template
                    st.markdown("""
                    <div class="card">
                        <h4>🕒 Break Schedule Template</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for i, break_slot in enumerate(breaks):
                        col1, col2, col3, col4 = st.columns([3,2,2,2])
                        with col1:
                            st.text_input("Break Name", value=break_slot["name"], key=f"tname_{i}", disabled=True)
                        with col2:
                            st.text_input("Start", value=break_slot["start"], key=f"tstart_{i}", disabled=True)
                        with col3:
                            st.text_input("End", value=break_slot["end"], key=f"tend_{i}", disabled=True)
                        with col4:
                            st.number_input("Max", value=break_slot["max_users"], key=f"tmax_{i}", disabled=True)
                    
                    apply_col1, apply_col2 = st.columns(2)
                    with apply_col1:
                        if st.button("💾 Apply This Template", type="primary"):
                            # Clear existing breaks for this shift type
                            conn = sqlite3.connect("data/break_schedule.db")
                            try:
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM breaks WHERE shift_type = ?", (selected_template,))
                                
                                # Add new breaks from template
                                for break_slot in breaks:
                                    cursor.execute("""
                                        INSERT INTO breaks (break_name, start_time, end_time, max_users, 
                                                          created_by, timestamp, shift_type) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        break_slot["name"],
                                        break_slot["start"],
                                        break_slot["end"],
                                        break_slot["max_users"],
                                        st.session_state.username,
                                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        selected_template
                                    ))
                                
                                conn.commit()
                                st.success(f"Template '{selected_template}' applied successfully!")
                            finally:
                                conn.close()
                    
                    with apply_col2:
                        if st.button("🗑️ Delete Template", type="secondary"):
                            delete_template(selected_template)
                            st.rerun()
        
        with tab2:
            st.markdown("""
            <div class="card admin-card">
                <h3>Manual Break Management</h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("add_break_form"):
                st.subheader("Add New Break Slot")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    break_name = st.text_input("Break Name", "TEABREAK")
                with col2:
                    start_time = st.text_input("Start Time (HH:MM)", "16:00")
                with col3:
                    end_time = st.text_input("End Time (HH:MM)", "16:15")
                with col4:
                    max_users = st.number_input("Max Users", min_value=1, value=5)
                with col5:
                    shift_type = st.selectbox(
                        "Shift Type",
                        ["USA ENGLISH FIRST SHIFT", "USA ENGLISH SECOND SHIFT", 
                         "USA SPANISH FIRST SHIFT", "USA SPANISH SECOND SHIFT"],
                        key="add_break_shift"
                    )
                
                if st.form_submit_button("➕ Add Break Slot", type="primary"):
                    add_break_slot(break_name, start_time, end_time, max_users, shift_type)
                    st.rerun()
            
            st.markdown("""
            <div class="card">
                <h4>Current Break Slots</h4>
            </div>
            """, unsafe_allow_html=True)
            
            current_breaks = get_all_breaks(selected_shift)
            
            if current_breaks:
                for b in current_breaks:
                    b_id, name, start, end, max_u, created_by, ts, shift = b
                    
                    col1, col2, col3, col4, col5, col6 = st.columns([3,2,2,2,3,1])
                    with col1:
                        st.text_input("Name", value=name, key=f"name_{b_id}")
                    with col2:
                        st.text_input("Start", value=start, key=f"start_{b_id}")
                    with col3:
                        st.text_input("End", value=end, key=f"end_{b_id}")
                    with col4:
                        st.number_input("Max Users", min_value=1, value=max_u, key=f"max_{b_id}")
                    with col5:
                        st.text_input("Shift Type", value=shift, key=f"shift_{b_id}", disabled=True)
                    with col6:
                        if st.button("🗑️", key=f"delete_{b_id}"):
                            delete_break_slot(b_id)
                            st.rerun()
            else:
                st.info("No break slots currently defined")
        
        with tab3:
            st.markdown("""
            <div class="card admin-card">
                <h3>All Bookings for Selected Date</h3>
            </div>
            """, unsafe_allow_html=True)
            
            bookings = get_all_bookings(formatted_date, selected_shift)
            if bookings:
                for b in bookings:
                    b_id, break_id, user_id, username, date, ts, break_name, start, end, role = b
                    
                    st.markdown(f"""
                    <div class="card booking-card">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <strong>{username}</strong> ({role})<br>
                                {break_name} ({start} - {end})<br>
                                <small>Shift: {selected_shift if selected_shift else 'All'}</small>
                            </div>
                            <div>
                                <button class="btn-danger" onclick="document.getElementById('cancel_{b_id}').click()">Cancel</button>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Cancel", key=f"cancel_{b_id}", on_click=lambda b_id=b_id: cancel_booking(b_id), visible=False):
                        pass
            else:
                st.info("No bookings for selected date")
            
            if st.button("🧹 Clear All Bookings", type="primary"):
                clear_all_break_bookings(selected_shift)
                st.rerun()
        
        with tab4:
            st.markdown("""
            <div class="card admin-card">
                <h3>Template Management</h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("➕ Create New Template"):
                with st.form("new_template_form"):
                    template_name = st.text_input("Template Name")
                    
                    # Break slots editor
                    st.subheader("Break Slots")
                    break_slots = st.session_state.get("new_template_breaks", [])
                    
                    cols = st.columns([3,2,2,2,1])
                    with cols[0]:
                        new_name = st.text_input("Break Name", key="new_break_name")
                    with cols[1]:
                        new_start = st.text_input("Start Time", key="new_break_start")
                    with cols[2]:
                        new_end = st.text_input("End Time", key="new_break_end")
                    with cols[3]:
                        new_max = st.number_input("Max Users", min_value=1, value=5, key="new_break_max")
                    with cols[4]:
                        if st.button("➕", key="add_break_button"):
                            if new_name and new_start and new_end:
                                break_slots.append({
                                    "name": new_name,
                                    "start": new_start,
                                    "end": new_end,
                                    "max_users": new_max
                                })
                                st.session_state.new_template_breaks = break_slots
                                st.rerun()
                    
                    # Display current break slots
                    for i, slot in enumerate(break_slots):
                        cols = st.columns([3,2,2,2,1])
                        with cols[0]:
                            st.text_input("Name", value=slot["name"], key=f"slot_name_{i}", disabled=True)
                        with cols[1]:
                            st.text_input("Start", value=slot["start"], key=f"slot_start_{i}", disabled=True)
                        with cols[2]:
                            st.text_input("End", value=slot["end"], key=f"slot_end_{i}", disabled=True)
                        with cols[3]:
                            st.number_input("Max", value=slot["max_users"], key=f"slot_max_{i}", disabled=True)
                        with cols[4]:
                            if st.button("🗑️", key=f"remove_slot_{i}"):
                                break_slots.pop(i)
                                st.session_state.new_template_breaks = break_slots
                                st.rerun()
                    
                    # Rules editor
                    st.subheader("Rules")
                    rules = st.session_state.get("new_template_rules", [])
                    
                    new_rule = st.text_input("Add New Rule")
                    if st.button("Add Rule", key="add_rule_button") and new_rule:
                        rules.append(new_rule)
                        st.session_state.new_template_rules = rules
                        st.rerun()
                    
                    for i, rule in enumerate(rules):
                        cols = st.columns([5,1])
                        with cols[0]:
                            st.text_input("Rule", value=rule, key=f"rule_{i}", disabled=True)
                        with cols[1]:
                            if st.button("🗑️", key=f"remove_rule_{i}"):
                                rules.pop(i)
                                st.session_state.new_template_rules = rules
                                st.rerun()
                    
                    if st.form_submit_button("💾 Save Template", type="primary"):
                        if template_name and break_slots and rules:
                            if save_template(template_name, break_slots, rules):
                                st.success("Template saved successfully!")
                                del st.session_state.new_template_breaks
                                del st.session_state.new_template_rules
                                st.rerun()
                            else:
                                st.error("Template with this name already exists")
                        else:
                            st.error("Please provide template name, at least one break slot, and at least one rule")
    
    else:
        # Agent view
        st.markdown(f"""
        <div class="header">
            <h2>👋 Welcome, {st.session_state.username}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🕒 Available Breaks", "📋 My Bookings"])
        
        with tab1:
            st.markdown("""
            <div class="card">
                <h3>Available Break Slots</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Get the template rules for the selected shift
            if selected_shift:
                template = get_template_by_name(selected_shift)
                if template:
                    import json
                    rules = json.loads(template[3])
                    
                    # Display rules
                    st.markdown("""
                    <div class="card">
                        <h4>📜 Break Rules</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for rule in rules:
                        st.markdown(f"""
                        <div class="card">
                            <p>• {rule}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            available_breaks = get_available_break_slots(formatted_date, selected_shift)
            
            if available_breaks:
                for b in available_breaks:
                    b_id, name, start, end, max_u, curr_u, created_by, ts = b
                    
                    conn = sqlite3.connect("data/break_schedule.db")
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM break_bookings 
                        WHERE break_id = ? AND booking_date = ?
                    """, (b_id, formatted_date))
                    booked_count = cursor.fetchone()[0]
                    conn.close()
                    
                    remaining = max_u - booked_count
                    availability_class = "available" if remaining > 0 else "full"
                    availability_text = f"{remaining}/{max_u} slots"
                    
                    st.markdown(f"""
                    <div class="card break-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4>{name}</h4>
                                <p>{start} - {end}</p>
                            </div>
                            <div style="text-align: right;">
                                <span class="availability-badge {availability_class}">{availability_text}</span><br>
                                <button class="btn-success" {"disabled" if remaining <= 0 else ""}
                                    onclick="document.getElementById('book_{b_id}').click()">
                                    Book Now
                                </button>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Book", key=f"book_{b_id}", on_click=lambda b_id=b_id: book_break(b_id, formatted_date), visible=False):
                        pass
            else:
                st.info("No break slots available for booking")
        
        with tab2:
            st.markdown("""
            <div class="card">
                <h3>My Bookings</h3>
            </div>
            """, unsafe_allow_html=True)
            
            user_bookings = get_user_bookings(st.session_state.username, formatted_date)
            
            if user_bookings:
                for b in user_bookings:
                    b_id, break_id, user_id, username, date, ts, break_name, start, end = b
                    
                    # Get shift type for this booking
                    conn = sqlite3.connect("data/break_schedule.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT shift_type FROM breaks WHERE id = ?", (break_id,))
                    shift_type = cursor.fetchone()[0]
                    conn.close()
                    
                    st.markdown(f"""
                    <div class="card booking-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4>{break_name}</h4>
                                <p>{start} - {end}</p>
                                <small>Shift: {shift_type}</small>
                            </div>
                            <div>
                                <button class="btn-danger" onclick="document.getElementById('cancel_{b_id}').click()">Cancel</button>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Cancel", key=f"cancel_{b_id}", on_click=lambda b_id=b_id: cancel_booking(b_id), visible=False):
                        pass
            else:
                st.info("You have no bookings for selected date")

def book_break(break_id, date):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (st.session_state.username,))
    user_id = cursor.fetchone()[0]
    conn.close()
    
    book_break_slot(break_id, user_id, st.session_state.username, date)
    st.rerun()

def cancel_booking(booking_id):
    conn = sqlite3.connect("data/break_schedule.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM break_bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    st.rerun()

# Main app
def main():
    st.set_page_config(
        page_title="Break Scheduling System",
        page_icon="⏱️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        login_section()
    else:
        breaks_section()

if __name__ == "__main__":
    main()
