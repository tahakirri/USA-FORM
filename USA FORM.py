import streamlit as st
from datetime import datetime, time
import pandas as pd
import json
import os
from streamlit.components.v1 import html

# Custom CSS to match the original styling
def inject_custom_css():
    st.markdown("""
    <style>
        .stApp {
            background-color: white;
        }
        .stMarkdown h1 {
            color: black;
            font-size: 24px;
            font-weight: bold;
        }
        .stMarkdown h2 {
            color: black;
            font-size: 20px;
            font-weight: bold;
            border-bottom: 1px solid black;
        }
        .stDataFrame {
            width: 100%;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .warning {
            color: red;
            font-weight: bold;
        }
        .break-option {
            padding: 5px;
            margin: 2px;
            border-radius: 3px;
            cursor: pointer;
        }
        .break-option:hover {
            background-color: #f0f0f0;
        }
        .selected-break {
            background-color: #4CAF50;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'templates' not in st.session_state:
        st.session_state.templates = {}
    if 'current_template' not in st.session_state:
        st.session_state.current_template = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'agent_bookings' not in st.session_state:
        st.session_state.agent_bookings = {}
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = datetime.now().strftime('%Y-%m-%d')
    
    # Load templates from file if exists
    if os.path.exists('templates.json'):
        with open('templates.json', 'r') as f:
            st.session_state.templates = json.load(f)

# Save templates to file
def save_templates():
    with open('templates.json', 'w') as f:
        json.dump(st.session_state.templates, f)

# Login page
def login_page():
    st.title("Break Scheduling System")
    st.markdown("---")
    
    role = st.radio("Select your role:", ["Admin", "Agent"])
    password = st.text_input("Password:", type="password")
    
    if st.button("Login"):
        if role == "Admin" and password == "admin123":
            st.session_state.user_role = "admin"
            st.session_state.logged_in = True
            st.success("Logged in as Admin")
            st.rerun()
        elif role == "Agent" and password == "agent123":
            st.session_state.user_role = "agent"
            st.session_state.logged_in = True
            st.success("Logged in as Agent")
            st.rerun()
        else:
            st.error("Invalid credentials")

# [Rest of your code remains exactly the same...]

# Main app
def main():
    inject_custom_css()
    init_session_state()
    
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.user_role == "admin":
            admin_dashboard()
        else:
            agent_dashboard()
        
        # Logout button
        if st.button("Logout", key="logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.rerun()

if __name__ == "__main__":
    main()
