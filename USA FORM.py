import streamlit as st
from datetime import datetime, time, timedelta
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
        .full-break {
            background-color: #FF5252;
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
    if 'timezone_offset' not in st.session_state:
        st.session_state.timezone_offset = 0  # GMT by default
    if 'break_limits' not in st.session_state:
        st.session_state.break_limits = {}
    
    # Load data from files if exists
    if os.path.exists('templates.json'):
        with open('templates.json', 'r') as f:
            st.session_state.templates = json.load(f)
    if os.path.exists('break_limits.json'):
        with open('break_limits.json', 'r') as f:
            st.session_state.break_limits = json.load(f)
    if os.path.exists('all_bookings.json'):
        with open('all_bookings.json', 'r') as f:
            st.session_state.agent_bookings = json.load(f)

# Save data to files
def save_data():
    with open('templates.json', 'w') as f:
        json.dump(st.session_state.templates, f)
    with open('break_limits.json', 'w') as f:
        json.dump(st.session_state.break_limits, f)
    with open('all_bookings.json', 'w') as f:
        json.dump(st.session_state.agent_bookings, f)

# Adjust time based on timezone offset
def adjust_time(time_str, offset):
    try:
        if not time_str.strip():
            return ""
        time_obj = datetime.strptime(time_str.strip(), "%H:%M")
        adjusted_time = (time_obj + timedelta(hours=offset)).time()
        return adjusted_time.strftime("%H:%M")
    except:
        return time_str

# Adjust all times in a template based on timezone offset
def adjust_template_times(template, offset):
    adjusted_template = {
        "lunch_breaks": [adjust_time(t, offset) for t in template["lunch_breaks"]],
        "tea_breaks": {
            "early": [adjust_time(t, offset) for t in template["tea_breaks"]["early"]],
            "late": [adjust_time(t, offset) for t in template["tea_breaks"]["late"]]
        }
    }
    return adjusted_template

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

# Admin functions
def admin_dashboard():
    st.title("Admin Dashboard")
    st.markdown("---")
    
    # Timezone adjustment
    st.header("Timezone Adjustment")
    timezone = st.selectbox(
        "Select Timezone:", 
        ["GMT", "GMT+1", "GMT+2", "GMT-1", "GMT-2"],
        index=0
    )
    
    # Map timezone to offset
    timezone_offsets = {"GMT": 0, "GMT+1": 1, "GMT+2": 2, "GMT-1": -1, "GMT-2": -2}
    new_offset = timezone_offsets[timezone]
    
    if new_offset != st.session_state.timezone_offset:
        st.session_state.timezone_offset = new_offset
        st.success(f"Timezone set to {timezone}. All break times adjusted.")
        st.rerun()
    
    # Template management
    st.header("Template Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        template_name = st.text_input("Template Name:")
    
    with col2:
        if st.button("Create New Template"):
            if template_name:
                if template_name not in st.session_state.templates:
                    st.session_state.templates[template_name] = {
                        "lunch_breaks": ["19:30", "20:00", "20:30", "21:00", "21:30"],
                        "tea_breaks": {
                            "early": ["16:00", "16:15", "16:30", "16:45", "17:00", "17:15", "17:30"],
                            "late": ["21:45", "22:00", "22:15", "22:30"]
                        }
                    }
                    st.session_state.current_template = template_name
                    save_data()
                    st.success(f"Template '{template_name}' created!")
                else:
                    st.error("Template with this name already exists")
            else:
                st.error("Please enter a template name")
    
    # Template selection - THIS IS THE CORRECTED SECTION
    if st.session_state.templates:
        selected_template = st.selectbox(
            "Select Template to Edit:",
            list(st.session_state.templates.keys()),
            index=0 if not st.session_state.current_template else list(st.session_state.templates.keys()).index(st.session_state.current_template)
        )
        
        st.session_state.current_template = selected_template
        
        if st.button("Delete Template"):
            del st.session_state.templates[selected_template]
            st.session_state.current_template = None
            save_data()
            st.success(f"Template '{selected_template}' deleted!")
            st.rerun()

        
        # Edit template
        if st.session_state.current_template:
            template = st.session_state.templates[st.session_state.current_template]
            
            st.subheader("Edit Lunch Breaks")
            lunch_breaks = st.text_area(
                "Lunch Breaks (one per line):",
                "\n".join(template["lunch_breaks"]),
                height=150
            )
            
            st.subheader("Edit Tea Breaks")
            st.write("Early Tea Breaks:")
            early_tea_breaks = st.text_area(
                "Early Tea Breaks (one per line):",
                "\n".join(template["tea_breaks"]["early"]),
                height=150,
                key="early_tea"
            )
            
            st.write("Late Tea Breaks:")
            late_tea_breaks = st.text_area(
                "Late Tea Breaks (one per line):",
                "\n".join(template["tea_breaks"]["late"]),
                height=150,
                key="late_tea"
            )
            
            if st.button("Save Changes"):
                template["lunch_breaks"] = [t.strip() for t in lunch_breaks.split("\n") if t.strip()]
                template["tea_breaks"]["early"] = [t.strip() for t in early_tea_breaks.split("\n") if t.strip()]
                template["tea_breaks"]["late"] = [t.strip() for t in late_tea_breaks.split("\n") if t.strip()]
                save_data()
                st.success("Template updated successfully!")
    
    # Break limits management
    st.header("Break Limits Management")
    if st.session_state.current_template:
        template = st.session_state.templates[st.session_state.current_template]
        
        # Initialize limits if not exists
        if st.session_state.current_template not in st.session_state.break_limits:
            st.session_state.break_limits[st.session_state.current_template] = {
                "lunch": {time: 5 for time in template["lunch_breaks"]},
                "early_tea": {time: 3 for time in template["tea_breaks"]["early"]},
                "late_tea": {time: 3 for time in template["tea_breaks"]["late"]}
            }
        
        st.subheader("Lunch Break Limits")
        lunch_cols = st.columns(len(template["lunch_breaks"]))
        for i, time_slot in enumerate(template["lunch_breaks"]):
            with lunch_cols[i]:
                st.session_state.break_limits[st.session_state.current_template]["lunch"][time_slot] = st.number_input(
                    f"Max at {time_slot}",
                    min_value=1,
                    value=st.session_state.break_limits[st.session_state.current_template]["lunch"].get(time_slot, 5),
                    key=f"lunch_limit_{time_slot}"
                )
        
        st.subheader("Early Tea Break Limits")
        early_tea_cols = st.columns(len(template["tea_breaks"]["early"]))
        for i, time_slot in enumerate(template["tea_breaks"]["early"]):
            with early_tea_cols[i]:
                st.session_state.break_limits[st.session_state.current_template]["early_tea"][time_slot] = st.number_input(
                    f"Max at {time_slot}",
                    min_value=1,
                    value=st.session_state.break_limits[st.session_state.current_template]["early_tea"].get(time_slot, 3),
                    key=f"early_tea_limit_{time_slot}"
                )
        
        st.subheader("Late Tea Break Limits")
        late_tea_cols = st.columns(len(template["tea_breaks"]["late"]))
        for i, time_slot in enumerate(template["tea_breaks"]["late"]):
            with late_tea_cols[i]:
                st.session_state.break_limits[st.session_state.current_template]["late_tea"][time_slot] = st.number_input(
                    f"Max at {time_slot}",
                    min_value=1,
                    value=st.session_state.break_limits[st.session_state.current_template]["late_tea"].get(time_slot, 3),
                    key=f"late_tea_limit_{time_slot}"
                )
        
        if st.button("Save Break Limits"):
            save_data()
            st.success("Break limits saved successfully!")
    
    # View all bookings
    st.header("All Bookings")
    if st.session_state.agent_bookings:
        # Convert to DataFrame for better display
        bookings_list = []
        for date, agents in st.session_state.agent_bookings.items():
            for agent_id, breaks in agents.items():
                bookings_list.append({
                    "Date": date,
                    "Agent ID": agent_id,
                    "Lunch Break": breaks.get("lunch", "-"),
                    "Early Tea": breaks.get("early_tea", "-"),
                    "Late Tea": breaks.get("late_tea", "-")
                })
        
        bookings_df = pd.DataFrame(bookings_list)
        st.dataframe(bookings_df)
        
        # Export option
        if st.button("Export Bookings to CSV"):
            csv = bookings_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="break_bookings.csv",
                mime="text/csv"
            )
    else:
        st.write("No bookings yet.")

# Agent functions
def agent_dashboard():
    st.title("Agent Dashboard")
    st.markdown("---")
    
    # Agent ID input
    agent_id = st.text_input("Enter your Agent ID:")
    if not agent_id:
        st.warning("Please enter your Agent ID to continue")
        return
    
    # Date selection
    schedule_date = st.date_input("Select Date:", datetime.now())
    st.session_state.selected_date = schedule_date.strftime('%Y-%m-%d')
    
    # Template selection (only if multiple templates exist)
    if len(st.session_state.templates) > 1:
        selected_template = st.selectbox(
            "Select Schedule Template:",
            list(st.session_state.templates.keys())
        )
        template = adjust_template_times(st.session_state.templates[selected_template], st.session_state.timezone_offset)
    elif st.session_state.templates:
        template = adjust_template_times(list(st.session_state.templates.values())[0], st.session_state.timezone_offset)
    else:
        st.error("No schedules available. Please ask your admin to create one.")
        return
    
    # Display schedule and booking options
    display_schedule(template)
    
    # Booking section
    st.markdown("---")
    st.header("Book Your Breaks")
    
    # Check if template has limits defined
    template_name = st.session_state.current_template if st.session_state.current_template else list(st.session_state.templates.keys())[0]
    break_limits = st.session_state.break_limits.get(template_name, {})
    
    # Lunch break booking
    st.subheader("Lunch Break")
    if template["lunch_breaks"]:
        lunch_cols = st.columns(len(template["lunch_breaks"]))
        selected_lunch = None
        
        for i, time_slot in enumerate(template["lunch_breaks"]):
            with lunch_cols[i]:
                # Check if time slot is full
                current_bookings = count_bookings(st.session_state.selected_date, "lunch", time_slot)
                max_limit = break_limits.get("lunch", {}).get(time_slot, 5)
                
                if current_bookings >= max_limit:
                    st.button(f"{time_slot} (FULL)", key=f"lunch_{time_slot}", disabled=True, help="This slot is full")
                else:
                    if st.button(time_slot, key=f"lunch_{time_slot}"):
                        selected_lunch = time_slot
        
        if selected_lunch:
            if st.session_state.selected_date not in st.session_state.agent_bookings:
                st.session_state.agent_bookings[st.session_state.selected_date] = {}
            
            if agent_id not in st.session_state.agent_bookings[st.session_state.selected_date]:
                st.session_state.agent_bookings[st.session_state.selected_date][agent_id] = {}
            
            st.session_state.agent_bookings[st.session_state.selected_date][agent_id]["lunch"] = selected_lunch
            save_data()
            st.success(f"Lunch break booked for {selected_lunch}")
    else:
        st.write("No lunch breaks available in this schedule.")
    
    # Tea break booking
    st.subheader("Tea Breaks")
    st.write("Early Tea Breaks:")
    early_tea_cols = st.columns(len(template["tea_breaks"]["early"]))
    selected_early_tea = None
    
    for i, time_slot in enumerate(template["tea_breaks"]["early"]):
        with early_tea_cols[i]:
            # Check if time slot is full
            current_bookings = count_bookings(st.session_state.selected_date, "early_tea", time_slot)
            max_limit = break_limits.get("early_tea", {}).get(time_slot, 3)
            
            if current_bookings >= max_limit:
                st.button(f"{time_slot} (FULL)", key=f"early_tea_{time_slot}", disabled=True, help="This slot is full")
            else:
                if st.button(time_slot, key=f"early_tea_{time_slot}"):
                    selected_early_tea = time_slot
    
    if selected_early_tea:
        if st.session_state.selected_date not in st.session_state.agent_bookings:
            st.session_state.agent_bookings[st.session_state.selected_date] = {}
        
        if agent_id not in st.session_state.agent_bookings[st.session_state.selected_date]:
            st.session_state.agent_bookings[st.session_state.selected_date][agent_id] = {}
        
        st.session_state.agent_bookings[st.session_state.selected_date][agent_id]["early_tea"] = selected_early_tea
        save_data()
        st.success(f"Early tea break booked for {selected_early_tea}")
    
    st.write("Late Tea Breaks:")
    late_tea_cols = st.columns(len(template["tea_breaks"]["late"]))
    selected_late_tea = None
    
    for i, time_slot in enumerate(template["tea_breaks"]["late"]):
        with late_tea_cols[i]:
            # Check if time slot is full
            current_bookings = count_bookings(st.session_state.selected_date, "late_tea", time_slot)
            max_limit = break_limits.get("late_tea", {}).get(time_slot, 3)
            
            if current_bookings >= max_limit:
                st.button(f"{time_slot} (FULL)", key=f"late_tea_{time_slot}", disabled=True, help="This slot is full")
            else:
                if st.button(time_slot, key=f"late_tea_{time_slot}"):
                    selected_late_tea = time_slot
    
    if selected_late_tea:
        if st.session_state.selected_date not in st.session_state.agent_bookings:
            st.session_state.agent_bookings[st.session_state.selected_date] = {}
        
        if agent_id not in st.session_state.agent_bookings[st.session_state.selected_date]:
            st.session_state.agent_bookings[st.session_state.selected_date][agent_id] = {}
        
        st.session_state.agent_bookings[st.session_state.selected_date][agent_id]["late_tea"] = selected_late_tea
        save_data()
        st.success(f"Late tea break booked for {selected_late_tea}")
    
    # Display current bookings
    if st.session_state.selected_date in st.session_state.agent_bookings and agent_id in st.session_state.agent_bookings[st.session_state.selected_date]:
        st.markdown("---")
        st.header("Your Bookings")
        bookings = st.session_state.agent_bookings[st.session_state.selected_date][agent_id]
        
        if "lunch" in bookings:
            st.write(f"**Lunch Break:** {bookings['lunch']}")
        if "early_tea" in bookings:
            st.write(f"**Early Tea Break:** {bookings['early_tea']}")
        if "late_tea" in bookings:
            st.write(f"**Late Tea Break:** {bookings['late_tea']}")
        
        if st.button("Cancel All Bookings"):
            del st.session_state.agent_bookings[st.session_state.selected_date][agent_id]
            save_data()
            st.success("All bookings canceled for this date")
            st.rerun()

# Count bookings for a specific break time
def count_bookings(date, break_type, time_slot):
    count = 0
    if date in st.session_state.agent_bookings:
        for agent_id, breaks in st.session_state.agent_bookings[date].items():
            if break_type == "lunch" and "lunch" in breaks and breaks["lunch"] == time_slot:
                count += 1
            elif break_type == "early_tea" and "early_tea" in breaks and breaks["early_tea"] == time_slot:
                count += 1
            elif break_type == "late_tea" and "late_tea" in breaks and breaks["late_tea"] == time_slot:
                count += 1
    return count

# Display schedule (used by both admin and agent)
def display_schedule(template):
    st.header("LM US ENG 3:00 PM shift")
    
    # Lunch breaks table
    st.markdown("### LUNCH BREAKS")
    lunch_df = pd.DataFrame({
        "DATE": [st.session_state.selected_date],
        **{time: [""] for time in template["lunch_breaks"]}
    })
    st.table(lunch_df)
    
    st.markdown("**KINDLY RESPECT THE RULES BELOW**")
    st.markdown("**Non Respect Of Break Rules = Incident**")
    st.markdown("---")
    
    # Tea breaks table
    st.markdown("### TEA BREAK")
    
    # Create two columns for tea breaks
    max_rows = max(len(template["tea_breaks"]["early"]), len(template["tea_breaks"]["late"]))
    tea_data = {
        "TEA BREAK": template["tea_breaks"]["early"] + [""] * (max_rows - len(template["tea_breaks"]["early"])),
        "TEA BREAK": template["tea_breaks"]["late"] + [""] * (max_rows - len(template["tea_breaks"]["late"]))
    }
    tea_df = pd.DataFrame(tea_data)
    st.table(tea_df)
    
    # Rules section
    st.markdown("""
    **NO BREAK IN THE LAST HOUR WILL BE AUTHORIZED**  
    **PS: ONLY 5 MINUTES BIO IS AUTHORIZED IN THE LAST HOUR BETWEEN 23:00 TILL 23:30 AND NO BREAK AFTER 23:30 !!!**  
    **BREAKS SHOULD BE TAKEN AT THE NOTED TIME AND NEED TO BE CONFIRMED FROM RTA OR TEAM LEADERS**
    """)

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
