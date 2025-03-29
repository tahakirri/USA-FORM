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
        **Fancy phone numbers** are numbers that have special patterns that make them more memorable or desirable. 
        Common patterns include:
        
        - **Repeating digits**: 555-5555, 888-8888
        - **Sequential digits**: 123-4567, 987-6543
        - **Palindrome numbers**: 123-4321, 345-6543
        - **Same first and last digits**: 347-555-6666
        - **Multiple repeating patterns**: 501-530-3030
        - **All same digit except one**: 707-500-0001
        - **Special number patterns**: 1317-261-1666 (contains 666)
        
        These numbers are often considered premium and may be sold at higher prices.
        """)
    
    # Input field for phone number
    phone_input = st.text_input("📱 Enter Phone Number (10 or 11 digits)", 
                               placeholder="e.g., 3475556666 or 13172611666",
                               key="phone_input")
    
    # Check button
    check_button = st.button("🔍 Check if Fancy")
    
    # Function to check if a number is fancy
    def is_fancy_number(phone_number):
        # Remove all non-digit characters
        clean_number = re.sub(r'[^\d]', '', phone_number)
        
        # Check if the number is 10 or 11 digits (standard US numbers)
        if len(clean_number) not in [10, 11]:
            return False, "Invalid length (must be 10 or 11 digits)"
        
        # Check for various fancy patterns
        patterns = [
            (r'^(\d)\1{2,}\1{3,}$', "Repeating digits (e.g., 555-5555)"),  # All same digit
            (r'^(\d)\1{2,}(\d)\2{2,}$', "Multiple repeating patterns (e.g., 555-6666)"),
            (r'^(\d)\1{5,}', "Long repeating sequence (6+ same digits)"),
            (r'(\d)\1{3,}', "Four or more of the same digit in a row"),
            (r'123|234|345|456|567|678|789|987|876|765|654|543|432|321', "Sequential digits"),
            (r'(\d{3})\1', "Repeating 3-digit pattern"),
            (r'^(\d)(\d)(\d)\3\2\1$', "Palindrome (e.g., 123-321)"),
            (r'^(\d)\1(\d)\2(\d)\3$', "Alternating pairs (e.g., 11-22-33)"),
            (r'666|777|888|999|000|111|222|333|444|555', "Special triple digits"),
            (r'^(\d)\1{2}(\d)\2{2}(\d)\3{2}$', "Triple patterns (e.g., 111-222-333)"),
            (r'^(\d)\1?(\d)\2?(\d)\3?$', "Increasing or decreasing pattern"),
            (r'^(\d{3})\1\1$', "Repeating 3-digit block (e.g., 123-123-123)"),
            (r'^(\d)\1{1,}(\d)\2{1,}(\d)\3{1,}$', "Multiple repeating digits"),
            (r'^(\d{2})\1{2,}', "Repeating 2-digit pattern multiple times"),
            (r'^(\d)\1(\d)\1(\d)\1$', "Alternating with same digit (e.g., 1-2-1-3-1)"),
            (r'^\d*(\d)\1{2,}\d*$', "Three or more of same digit anywhere"),
            (r'^1?(\d{3})\1$', "First 3 digits repeat after area code"),
            (r'^1?(\d)\1{2}(\d)\2{2}(\d)\3{2}$', "Triple patterns with area code"),
            (r'^1?(\d{3})(\d)\2{3}$', "Last 4 digits same except first"),
            (r'^1?(\d)\1?(\d)\2?(\d)\3?(\d)\4?$', "Increasing/decreasing with possible skips")
        ]
        
        matched_patterns = []
        for pattern, description in patterns:
            if re.search(pattern, clean_number):
                matched_patterns.append(description)
        
        if matched_patterns:
            return True, matched_patterns
        else:
            return False, ["No fancy patterns detected"]
    
    if check_button and phone_input:
        # Check if the input is a valid phone number
        clean_number = re.sub(r'[^\d]', '', phone_input)
        
        if len(clean_number) not in [10, 11]:
            st.error("❌ Invalid phone number length. Please enter a 10-digit US number or 11-digit number starting with 1.")
        else:
            is_fancy, patterns = is_fancy_number(phone_input)
            
            # Format the phone number for display
            if len(clean_number) == 10:
                formatted_number = f"{clean_number[:3]}-{clean_number[3:6]}-{clean_number[6:]}"
            else:  # 11 digits
                formatted_number = f"{clean_number[:1]}-{clean_number[1:4]}-{clean_number[4:7]}-{clean_number[7:]}"
            
            if is_fancy:
                st.markdown(f"""
                <div class="result-box fancy-result">
                    <h3><span class="fancy-number">✨ {formatted_number} ✨</span></h3>
                    <p>This is a <strong>FANCY</strong> phone number!</p>
                    <p><strong>Patterns detected:</strong></p>
                    <ul>
                        {"".join([f"<li>{pattern}</li>" for pattern in patterns])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Show some examples of similar fancy numbers
                st.markdown("### Similar Fancy Number Examples:")
                examples = [
                    "347-555-6666", "501-530-3030", "707-500-0001", 
                    "131-726-11666", "167-889-99999", "146-979-90000",
                    "192-939-29933", "161-744-77575", "131-628-59999",
                    "133-228-66688", "158-538-28288", "192-969-36363",
                    "140-777-77370", "133-226-17777", "195-999-90008"
                ]
                st.write(", ".join(examples[:5]))
                st.write(", ".join(examples[5:10]))
                st.write(", ".join(examples[10:]))
            else:
                st.markdown(f"""
                <div class="result-box normal-result">
                    <h3><span class="normal-number">{formatted_number}</span></h3>
                    <p>This is a <strong>normal</strong> phone number.</p>
                    <p><strong>Analysis:</strong> {patterns[0]}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Batch checking option
    st.markdown("---")
    st.subheader("📁 Batch Check Phone Numbers")
    
    uploaded_file = st.file_uploader("Upload a CSV or text file with phone numbers (one per line)", 
                                    type=["csv", "txt"])
    
    if uploaded_file:
        try:
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                # Assume first column contains phone numbers
                phone_numbers = df.iloc[:, 0].astype(str).tolist()
            else:  # txt file
                phone_numbers = [line.decode('utf-8').strip() for line in uploaded_file.readlines()]
            
            if phone_numbers:
                st.success(f"✅ Successfully loaded {len(phone_numbers)} phone numbers")
                
                # Analyze all numbers
                results = []
                for number in phone_numbers:
                    is_fancy, patterns = is_fancy_number(number)
                    results.append({
                        "Phone Number": number,
                        "Fancy": "Yes" if is_fancy else "No",
                        "Patterns": ", ".join(patterns) if is_fancy else "Normal"
                    })
                
                # Create a dataframe with results
                results_df = pd.DataFrame(results)
                
                # Display results
                st.dataframe(results_df, use_container_width=True)
                
                # Download button
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results",
                    data=csv,
                    file_name="fancy_number_results.csv",
                    mime="text/csv"
                )
                
                # Show summary statistics
                fancy_count = results_df[results_df["Fancy"] == "Yes"].shape[0]
                st.markdown(f"""
                **Summary:**
                - Total numbers checked: {len(results_df)}
                - Fancy numbers found: {fancy_count} ({fancy_count/len(results_df):.1%})
                - Normal numbers: {len(results_df) - fancy_count} ({(len(results_df) - fancy_count)/len(results_df):.1%})
                """)
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
