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

# Database helper functions
def get_available_break_slots(date):
    conn = sqlite3.connect("data/requests.db")
    cursor = conn.cursor()
    
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
    conn = sqlite3.connect("data/requests.db")
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

def get_all_bookings(date):
    conn = sqlite3.connect("data/requests.db")
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
    conn = sqlite3.connect("data/requests.db")
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

def clear_all_break_bookings():
    conn = sqlite3.connect("data/requests.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM break_bookings")
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect("data/requests.db")
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
    conn = sqlite3.connect("data/requests.db")
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

def add_break_slot(name, start, end, max_users):
    conn = sqlite3.connect("data/requests.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO breaks (break_name, start_time, end_time, max_users, created_by, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (name, start, end, max_users, st.session_state.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()

def delete_break_slot(break_id):
    conn = sqlite3.connect("data/requests.db")
    cursor = conn.cursor()
    
    # First delete any bookings for this break
    cursor.execute("DELETE FROM break_bookings WHERE break_id = ?", (break_id,))
    
    # Then delete the break itself
    cursor.execute("DELETE FROM breaks WHERE id = ?", (break_id,))
    
    conn.commit()
    conn.close()

def get_all_breaks():
    conn = sqlite3.connect("data/requests.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM breaks ORDER BY start_time")
    results = cursor.fetchall()
    conn.close()
    return results

# Initialize the database
init_db()

# Authentication
def login_section():
    st.title("Break Scheduling System")
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login"):
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
                    new_username = st.text_input("New Username")
                    new_password = st.text_input("New Password", type="password")
                    new_role = st.selectbox("Role", ["agent", "admin", "team_lead"])
                    new_team = st.text_input("Team")
                    
                    if st.form_submit_button("Register"):
                        if register_user(new_username, new_password, new_role, new_team):
                            st.success("User registered successfully!")
                        else:
                            st.error("Username already exists")
            else:
                st.info("Only admins can register new users. Please login as admin.")
    else:
        st.sidebar.write(f"Logged in as: {st.session_state.username} ({st.session_state.role})")
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.clear()
            st.rerun()
        breaks_section()

# Break scheduling section
def breaks_section():
    # Define shift templates
    SHIFT_TEMPLATES = {
        "USA ENGLISH FIRST SHIFT": {
            "breaks": [
                {"name": "TEABREAK", "start": "16:00", "end": "16:15", "max_users": 5},
                {"name": "TEABREAK", "start": "16:15", "end": "16:30", "max_users": 5},
                {"name": "TEABREAK", "start": "16:30", "end": "16:45", "max_users": 5},
                {"name": "TEABREAK", "start": "16:45", "end": "17:00", "max_users": 5},
                {"name": "TEABREAK", "start": "17:00", "end": "17:15", "max_users": 5},
                {"name": "TEABREAK", "start": "17:15", "end": "17:30", "max_users": 5},
                {"name": "TEABREAK", "start": "21:45", "end": "22:00", "max_users": 5},
                {"name": "TEABREAK", "start": "22:00", "end": "22:15", "max_users": 5},
                {"name": "TEABREAK", "start": "22:15", "end": "22:30", "max_users": 5},
            ],
            "rules": [
                "NO BREAK IN THE LAST HOUR WILL BE AUTHORIZED",
                "PS. ONLY 5 MINUTES BIO IS AUTHORIZED IN THE LAST HOUR BETWEEN 23:00 TILL 23:30 AND NO BREAK AFTER 23:30 !!!",
                "BREAKS SHOULD BE TAKEN AT THE NOTED TIME AND NEED TO BE CONFIRMED FROM RTA OR TEAM LEADERS"
            ]
        },
        "USA ENGLISH SECOND SHIFT": {
            "breaks": [
                {"name": "TEABREAK", "start": "19:30", "end": "20:00", "max_users": 5},
                {"name": "TEABREAK", "start": "20:00", "end": "20:30", "max_users": 5},
                {"name": "TEABREAK", "start": "20:30", "end": "21:00", "max_users": 5},
                {"name": "TEABREAK", "start": "21:00", "end": "21:30", "max_users": 5},
            ],
            "rules": [
                "Non Respect Of Break Rules = Incident",
                "BREAKS SHOULD BE TAKEN AT THE NOTED TIME AND NEED TO BE CONFIRMED FROM RTA OR TEAM LEADERS"
            ]
        },
        "USA SPANISH FIRST SHIFT": {
            "breaks": [
                {"name": "DESCANSO", "start": "16:00", "end": "16:15", "max_users": 5},
                {"name": "DESCANSO", "start": "16:15", "end": "16:30", "max_users": 5},
                {"name": "DESCANSO", "start": "16:30", "end": "16:45", "max_users": 5},
                {"name": "DESCANSO", "start": "16:45", "end": "17:00", "max_users": 5},
                {"name": "DESCANSO", "start": "17:00", "end": "17:15", "max_users": 5},
                {"name": "DESCANSO", "start": "17:15", "end": "17:30", "max_users": 5},
                {"name": "DESCANSO", "start": "21:45", "end": "22:00", "max_users": 5},
                {"name": "DESCANSO", "start": "22:00", "end": "22:15", "max_users": 5},
                {"name": "DESCANSO", "start": "22:15", "end": "22:30", "max_users": 5},
            ],
            "rules": [
                "NO SE AUTORIZARÁN DESCANSOS EN LA ÚLTIMA HORA",
                "¡¡¡SOLO SE AUTORIZAN 5 MINUTOS PARA BIO ENTRE LAS 23:00 Y LAS 23:30 Y NINGÚN DESCANSO DESPUÉS DE LAS 23:30!!!",
                "LOS DESCANSOS DEBEN TOMARSE EN EL TIEMPO NOTADO Y DEBEN SER CONFIRMADOS POR RTA O LÍDERES DE EQUIPO"
            ]
        },
        "USA SPANISH SECOND SHIFT": {
            "breaks": [
                {"name": "DESCANSO", "start": "19:30", "end": "20:00", "max_users": 5},
                {"name": "DESCANSO", "start": "20:00", "end": "20:30", "max_users": 5},
                {"name": "DESCANSO", "start": "20:30", "end": "21:00", "max_users": 5},
                {"name": "DESCANSO", "start": "21:00", "end": "21:30", "max_users": 5},
            ],
            "rules": [
                "Incumplimiento de las reglas de descanso = Incidente",
                "LOS DESCANSOS DEBEN TOMARSE EN EL TIEMPO NOTADO Y DEBEN SER CONFIRMADOS POR RTA O LÍDERES DE EQUIPO"
            ]
        }
    }

    today = datetime.now().strftime("%Y-%m-%d")
    selected_date = st.date_input("Select date", datetime.now())
    formatted_date = selected_date.strftime("%Y-%m-%d")

    # Admin section for managing templates
    if st.session_state.role == "admin":
        st.subheader("Admin: Break Schedule Management")
        
        # Template selection and management
        selected_template = st.selectbox("Select Template", list(SHIFT_TEMPLATES.keys()))
        
        # Display current template breaks
        st.markdown("### Current Template Breaks")
        template_breaks = SHIFT_TEMPLATES[selected_template]["breaks"]
        
        # Create a table-like display for the breaks
        st.markdown("""
        <style>
            .break-table {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 10px;
                margin-bottom: 20px;
            }
            .break-header {
                font-weight: bold;
                background-color: #2d3748;
                padding: 8px;
                border-radius: 5px;
            }
            .break-cell {
                padding: 8px;
                background-color: #1f2937;
                border-radius: 5px;
            }
            .rules-box {
                background-color: #1f2937;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 4px solid #3b82f6;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Display rules
        st.markdown("### Break Rules")
        with st.container():
            for rule in SHIFT_TEMPLATES[selected_template]["rules"]:
                st.markdown(f"""
                <div class="rules-box">
                    <p>{rule}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Display breaks in a grid
        st.markdown("### Break Schedule")
        st.markdown('<div class="break-table">', unsafe_allow_html=True)
        
        # Headers
        st.markdown('<div class="break-header">Time Slot</div>', unsafe_allow_html=True)
        st.markdown('<div class="break-header">Start</div>', unsafe_allow_html=True)
        st.markdown('<div class="break-header">End</div>', unsafe_allow_html=True)
        st.markdown('<div class="break-header">Max Users</div>', unsafe_allow_html=True)
        st.markdown('<div class="break-header">Action</div>', unsafe_allow_html=True)
        
        for i, break_slot in enumerate(template_breaks):
            st.markdown(f'<div class="break-cell">{break_slot["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="break-cell">{break_slot["start"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="break-cell">{break_slot["end"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="break-cell">{break_slot["max_users"]}</div>', unsafe_allow_html=True)
            
            if st.button("✏️ Edit", key=f"edit_template_{i}"):
                pass  # Would implement edit functionality here
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply template to current date
        if st.button("Apply Template to Selected Date"):
            # Clear existing breaks for this date
            conn = sqlite3.connect("data/requests.db")
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM breaks")
                
                # Add new breaks from template
                for break_slot in template_breaks:
                    cursor.execute("""
                        INSERT INTO breaks (break_name, start_time, end_time, max_users, created_by, timestamp) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        break_slot["name"],
                        break_slot["start"],
                        break_slot["end"],
                        break_slot["max_users"],
                        st.session_state.username,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                
                conn.commit()
                st.success("Template applied successfully!")
            finally:
                conn.close()
        
        st.markdown("---")
        
        # Manual break management
        st.subheader("Manual Break Management")
        
        with st.form("add_break_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                break_name = st.text_input("Break Name", "TEABREAK")
            with col2:
                start_time = st.text_input("Start Time (HH:MM)", "16:00")
            with col3:
                end_time = st.text_input("End Time (HH:MM)", "16:15")
            with col4:
                max_users = st.number_input("Max Users", min_value=1, value=5)
            
            if st.form_submit_button("Add Break Slot"):
                add_break_slot(break_name, start_time, end_time, max_users)
                st.rerun()
        
        st.markdown("### Current Break Slots")
        current_breaks = get_all_breaks()
        
        if current_breaks:
            for b in current_breaks:
                b_id, name, start, end, max_u, created_by, ts = b
                
                col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])
                with col1:
                    st.text_input("Name", value=name, key=f"name_{b_id}")
                with col2:
                    st.text_input("Start", value=start, key=f"start_{b_id}")
                with col3:
                    st.text_input("End", value=end, key=f"end_{b_id}")
                with col4:
                    st.number_input("Max Users", min_value=1, value=max_u, key=f"max_{b_id}")
                with col5:
                    if st.button("🗑️", key=f"delete_{b_id}"):
                        delete_break_slot(b_id)
                        st.rerun()
        else:
            st.info("No break slots currently defined")
        
        st.markdown("---")
        
        # Display all bookings for selected date
        st.subheader("All Bookings for Selected Date")
        bookings = get_all_bookings(formatted_date)
        if bookings:
            for b in bookings:
                b_id, break_id, user_id, username, date, ts, break_name, start, end, role = b
                st.write(f"{username} ({role}) - {break_name} ({start} - {end})")
        else:
            st.info("No bookings for selected date")
        
        if st.button("Clear All Bookings", key="clear_all_bookings"):
            clear_all_break_bookings()
            st.rerun()
    
    else:
        # Agent view
        st.subheader("Available Break Slots")
        
        # Display rules from the first template (assuming all have same rules)
        st.markdown("### Break Rules")
        with st.container():
            for rule in list(SHIFT_TEMPLATES.values())[0]["rules"]:
                st.markdown(f"""
                <div class="rules-box">
                    <p>{rule}</p>
                </div>
                """, unsafe_allow_html=True)
        
        available_breaks = get_available_break_slots(formatted_date)
        
        if available_breaks:
            st.markdown('<div class="break-table">', unsafe_allow_html=True)
            
            # Headers
            st.markdown('<div class="break-header">Break</div>', unsafe_allow_html=True)
            st.markdown('<div class="break-header">Time</div>', unsafe_allow_html=True)
            st.markdown('<div class="break-header">Available</div>', unsafe_allow_html=True)
            st.markdown('<div class="break-header">Action</div>', unsafe_allow_html=True)
            
            for b in available_breaks:
                b_id, name, start, end, max_u, curr_u, created_by, ts = b
                
                conn = sqlite3.connect("data/requests.db")
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM break_bookings 
                    WHERE break_id = ? AND booking_date = ?
                """, (b_id, formatted_date))
                booked_count = cursor.fetchone()[0]
                conn.close()
                
                remaining = max_u - booked_count
                
                # Break name cell
                st.markdown(f'<div class="break-cell">{name}</div>', unsafe_allow_html=True)
                
                # Time slot cell
                st.markdown(f'<div class="break-cell">{start} - {end}</div>', unsafe_allow_html=True)
                
                # Availability cell
                st.markdown(f'<div class="break-cell">{remaining}/{max_u}</div>', unsafe_allow_html=True)
                
                # Action cell
                if remaining > 0:
                    if st.button("Book", key=f"book_{b_id}"):
                        conn = sqlite3.connect("data/requests.db")
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM users WHERE username = ?", 
                                    (st.session_state.username,))
                        user_id = cursor.fetchone()[0]
                        conn.close()
                        
                        book_break_slot(b_id, user_id, st.session_state.username, formatted_date)
                        st.rerun()
                else:
                    st.markdown('<div class="break-cell">Full</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Your Bookings")
        user_bookings = get_user_bookings(st.session_state.username, formatted_date)
        
        if user_bookings:
            for b in user_bookings:
                b_id, break_id, user_id, username, date, ts, break_name, start, end = b
                st.write(f"{break_name} ({start} - {end})")
                
                # Add cancel button for each booking
                if st.button("Cancel Booking", key=f"cancel_{b_id}"):
                    conn = sqlite3.connect("data/requests.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM break_bookings WHERE id = ?", (b_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()
        else:
            st.info("You have no bookings for selected date")

# Main app
def main():
    st.set_page_config(
        page_title="Break Scheduling System",
        page_icon="⏱️",
        layout="wide"
    )
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        login_section()
    else:
        breaks_section()

if __name__ == "__main__":
    main()
