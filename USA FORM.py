import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io
from PIL import Image
import re

# Ensure a directory exists for storing uploaded images
UPLOAD_DIRECTORY = 'uploaded_images'
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
LATEST_IMAGE_PATH = os.path.join(UPLOAD_DIRECTORY, 'latest_hold_image.jpg')

# Custom CSS for dark mode and enhanced styling
st.set_page_config(
    page_title="USA Collab", 
    page_icon="✉️", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Define custom CSS for dark mode and enhanced styling
st.markdown("""
<style>
    /* Dark Mode Theme */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Custom Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #1e2129;
    }
    
    /* Header Styling */
    h1, h2, h3, h4 {
        color: #4db8ff;
    }
    
    /* Input and Select Box Styling */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div > select {
        background-color: #2c2f36;
        color: #ffffff;
        border: 1px solid #4a4e57;
    }
    
    /* Data Editor Styling */
    .dataframe {
        background-color: #1e2129;
        color: #ffffff;
    }
    
    /* Button Styling */
    .stButton > button {
        background-color: #4db8ff;
        color: #ffffff;
        border: none;
        transition: background-color 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #3aa0ff;
    }
    
    /* Fancy Number Styling */
    .fancy-number {
        color: #00ff00;
        font-weight: bold;
    }
    
    .normal-number {
        color: #ffffff;
    }
    
    .result-box {
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .fancy-result {
        background-color: #1e3d1e;
        border: 1px solid #00ff00;
    }
    
    .normal-result {
        background-color: #3d1e1e;
        border: 1px solid #ff0000;
    }
    
    .pattern-example {
        font-family: monospace;
        background-color: #2c2f36;
        padding: 2px 5px;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# Define separate CSV files for each section
REQUEST_FILE = 'request_data.csv'
MISTAKE_FILE = 'mistake_data.csv'

# Ensure files exist
for file in [REQUEST_FILE, MISTAKE_FILE]:
    if not os.path.exists(file):
        pd.DataFrame().to_csv(file, index=False)

# Load request data with Completed column
try:
    request_data = pd.read_csv(REQUEST_FILE)
    if "Completed" not in request_data.columns:
        request_data["Completed"] = False
except pd.errors.EmptyDataError:
    request_data = pd.DataFrame(columns=["Completed", "Agent Name", "TYPE", "ID", "COMMENT", "Timestamp"])

# Load mistake data
try:
    mistake_data = pd.read_csv(MISTAKE_FILE)
except pd.errors.EmptyDataError:
    mistake_data = pd.DataFrame(columns=["Team Leader Name", "Agent Name", "Ticket ID", "Error", "Timestamp"])

# Sidebar for navigation with icons
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    section = st.radio("Choose Section", [
        "📋 Request", 
        "🖼️ HOLD", 
        "❌ Ticket Mistakes",
        "🔢 Fancy Number Checker"
    ])

# Request Tab
if section == "📋 Request":
    st.header("📋 Request Section")

    col1, col2 = st.columns([3, 2])
    
    with col1:
        agent_name_input = st.text_input("👤 Agent Name", key="agent_name")
        type_input = st.selectbox("🔍 Type", ["Email", "Phone Number", "Ticket ID"], key="type")
        id_input = st.text_input("🆔 ID", key="id")
    
    with col2:
        comment_input = st.text_area("💬 Comment", height=150, key="comment")  
    
    # Side-by-side buttons
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        submit_button = st.button("✅ Submit Data")
    
    with btn_col2:
        refresh_button = st.button("🔄 Refresh Data")
    
    with btn_col3:
        clear_button = st.button("🗑️ Clear Data")
    
    # Clear data confirmation
    if clear_button:
        # Create a password input for confirmation
        clear_password = st.text_input("🔐 Enter password to clear data:", type="password", key="clear_password")
        
        if clear_password:
            if clear_password == "wipe":
                # Clear only request data
                request_data = pd.DataFrame(columns=["Completed", "Agent Name", "TYPE", "ID", "COMMENT", "Timestamp"])
                request_data.to_csv(REQUEST_FILE, index=False)
                st.success("✅ Request data has been cleared successfully!")
            else:
                st.error("❌ Incorrect password. Data was not cleared.")
    
    if submit_button:
        if not agent_name_input or not id_input or not comment_input:
            st.error("❗ Please fill out all fields.")
        else:
            new_data = {
                "Completed": False,
                "Agent Name": agent_name_input,
                "TYPE": type_input,
                "ID": id_input,
                "COMMENT": comment_input,
                "Timestamp": datetime.now().strftime("%H:%M:%S")
            }
            new_row = pd.DataFrame([new_data])
            request_data = pd.concat([request_data, new_row], ignore_index=True)
            request_data.to_csv(REQUEST_FILE, index=False)
            st.success("✅ Data Submitted!")

    if not request_data.empty:
        st.write("### 📋 Submitted Requests:")
        
        columns_order = ["Completed", "Agent Name", "TYPE", "ID", "COMMENT", "Timestamp"]
        
        display_data = request_data[columns_order].copy()
        
        edited_df = st.data_editor(
            display_data, 
            column_config={
                "Completed": st.column_config.CheckboxColumn(
                    "✅ Completed",
                    help="Mark request as completed",
                    default=False
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        request_data.loc[:, columns_order] = edited_df
        request_data.to_csv(REQUEST_FILE, index=False)

# HOLD Tab
if section == "🖼️ HOLD":
    st.header("🖼️ HOLD Section")
    uploaded_image = st.file_uploader("📤 Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_image:
        try:
            # Open the image
            image = Image.open(uploaded_image)
            
            # Convert image to RGB mode if it's not already
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(LATEST_IMAGE_PATH), exist_ok=True)
            
            # Save the image with explicit write permissions
            image.save(LATEST_IMAGE_PATH, quality=85)
            
            # Display the uploaded image
            st.image(image, caption="📸 Uploaded Image", use_container_width=True)
            st.success("✅ Image uploaded successfully!")
        
        except Exception as e:
            st.error(f"❌ Error uploading image: {str(e)}")

    if st.button("🔍 CHECK HOLD"):
        # Check if the latest image exists
        if os.path.exists(LATEST_IMAGE_PATH):
            try:
                # Open and display the latest image
                latest_image = Image.open(LATEST_IMAGE_PATH)
                st.image(latest_image, caption="📸 Latest Uploaded Image", use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error displaying image: {str(e)}")
        else:
            st.write("❌ No image uploaded.")

# Ticket Mistakes Tab
if section == "❌ Ticket Mistakes":
    st.header("❌ Ticket Mistakes Section")

    col1, col2 = st.columns([3, 2])  
    
    with col1:
        team_leader_input = st.text_input("👥 Team Leader Name", key="team_leader")
        agent_name_mistake_input = st.text_input("👤 Agent Name", key="agent_name_mistake")
        ticket_id_input = st.text_input("🆔 Ticket ID", key="ticket_id")
    
    with col2:
        error_input = st.text_area("⚠️ Error", height=150, key="error")
    
    # Side-by-side buttons for Ticket Mistakes
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        submit_mistake_button = st.button("✅ Submit Mistake")
    
    with btn_col2:
        refresh_mistake_button = st.button("🔄 Refresh Mistakes")
    
    if submit_mistake_button:
        if not team_leader_input or not agent_name_mistake_input or not ticket_id_input or not error_input:
            st.error("❗ Please fill out all fields.")
        else:
            new_mistake = {
                "Team Leader Name": team_leader_input,
                "Agent Name": agent_name_mistake_input,
                "Ticket ID": ticket_id_input,
                "Error": error_input,
                "Timestamp": datetime.now().strftime("%H:%M:%S")
            }
            new_row = pd.DataFrame([new_mistake])
            mistake_data = pd.concat([mistake_data, new_row], ignore_index=True)
            mistake_data.to_csv(MISTAKE_FILE, index=False)
            st.success("✅ Mistake Submitted!")

    if refresh_mistake_button or not mistake_data.empty:
        st.write("❌ Mistakes Table:")
        st.dataframe(mistake_data, use_container_width=True)

# Fancy Number Checker Tab
elif section == "🔢 Fancy Number Checker":
    st.header("🔢 Fancy Number Checker")
    
    # Explanation of fancy numbers
    with st.expander("ℹ️ What makes a phone number fancy?"):
        st.markdown("""
        **Fancy phone numbers** must clearly match one of these specific patterns:
        
        - **4+ repeating digits**: <span class="pattern-example">555-5555</span>
        - **Perfect sequences**: <span class="pattern-example">123-4567</span> or <span class="pattern-example">987-6543</span>
        - **Palindromes**: <span class="pattern-example">123-4321</span>
        - **Mirror patterns**: <span class="pattern-example">17029-088-077</span>
        - **All same digit**: <span class="pattern-example">888-8888</span>
        
        Numbers with minor patterns or random repetitions won't be considered fancy.
        """, unsafe_allow_html=True)
    
    # Input field for phone number
    phone_input = st.text_input("📱 Enter Phone Number (10 or 11 digits)", 
                               placeholder="e.g., 3475556666 or 13172611666",
                               key="phone_input")
    
    # Check button
    check_button = st.button("🔍 Check if Fancy")
    
    # Precise fancy number detection
    def is_fancy_number(phone_number):
        # Remove all non-digit characters
        clean_number = re.sub(r'[^\d]', '', phone_number)
        
        # Validate length (10 digits or 11 digits starting with 1)
        if len(clean_number) == 11 and clean_number.startswith('1'):
            clean_number = clean_number[1:]  # Remove country code
        elif len(clean_number) != 10:
            return False, "Invalid length (must be 10 digits or 11 digits starting with 1)"
        
        # Check for 4+ repeating digits (e.g., 5555555)
        if re.search(r'(\d)\1{3,}', clean_number):
            return True, "4+ repeating digits"
        
        # Check for perfect sequences (e.g., 1234567890 or 9876543210)
        if clean_number in '1234567890' or clean_number in '9876543210':
            return True, "Perfect sequence"
        
        # Check for palindromes (reads same forwards and backwards)
        if clean_number == clean_number[::-1]:
            return True, "Palindrome"
        
        # Check for mirror patterns in last 6 digits (e.g., 088 077)
        last_six = clean_number[4:]
        if len(last_six) == 6 and last_six[:3] == last_six[3:]:
            return True, "Mirror pattern in last 6 digits"
        
        # Check for all same digit
        if len(set(clean_number)) == 1:
            return True, "All same digit"
        
        return False, "No fancy pattern detected"
    
    if check_button and phone_input:
        is_fancy, pattern = is_fancy_number(phone_input)
        clean_number = re.sub(r'[^\d]', '', phone_input)
        
        # Format the number for display
        if len(clean_number) == 10:
            formatted_number = f"{clean_number[:3]}-{clean_number[3:6]}-{clean_number[6:]}"
        elif len(clean_number) == 11:
            formatted_number = f"{clean_number[0]}-{clean_number[1:4]}-{clean_number[4:7]}-{clean_number[7:]}"
        else:
            formatted_number = clean_number
            
        if is_fancy:
            st.markdown(f"""
            <div class="result-box fancy-result">
                <h3><span class="fancy-number">✨ {formatted_number} ✨</span></h3>
                <p>This is a <strong>FANCY</strong> phone number!</p>
                <p><strong>Pattern:</strong> {pattern}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show examples of similar fancy numbers
            st.markdown("### Similar Fancy Number Examples:")
            examples = [
                "555-555-5555", "123-456-7890", "987-654-3210",
                "111-111-1111", "170-290-88077", "088-088-0888",
                "123-321-1234", "456-654-4567", "999-999-9999"
            ]
            st.write(", ".join(examples[:5]))
            st.write(", ".join(examples[5:]))
        else:
            st.markdown(f"""
            <div class="result-box normal-result">
                <h3><span class="normal-number">{formatted_number}</span></h3>
                <p>This is a <strong>normal</strong> phone number.</p>
                <p><strong>Analysis:</strong> {pattern}</p>
            </div>
            """, unsafe_allow_html=True)
