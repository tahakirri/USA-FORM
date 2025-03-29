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

# [Previous CSS and setup code remains the same until Fancy Number Checker section]

# Fancy Number Checker Tab
elif section == "🔢 Fancy Number Checker":
    st.header("🔢 Fancy Number Checker")
    
    # Explanation of fancy numbers with the table from the image
    with st.expander("ℹ️ What makes a phone number fancy?"):
        st.markdown("""
        **Fancy phone numbers** must clearly match one of these specific patterns:
        
        <table>
            <thead>
                <tr>
                    <th><b>6-digit sequence</b></th>
                    <th><b>3-digit sequence</b></th>
                    <th><b>2-digit sequence</b></th>
                    <th><b>Exceptional cases</b></th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>123456</td>
                    <td>444 555</td>
                    <td>11 12 13</td>
                    <td>7900000123</td>
                </tr>
                <tr>
                    <td>987654</td>
                    <td>121 122</td>
                    <td>20 20 20</td>
                    <td>7900007555</td>
                </tr>
                <tr>
                    <td>666666</td>
                    <td>786 786</td>
                    <td>01 01 01</td>
                    <td>7898789555</td>
                </tr>
                <tr>
                    <td>100001</td>
                    <td>457 456</td>
                    <td>32 42 52</td>
                    <td>7999004455</td>
                </tr>
            </tbody>
        </table>
        
        We also detect:
        - Long sequences (like 18576543210)
        - Mirror patterns
        - Repeating digit groups
        """, unsafe_allow_html=True)
    
    # Input field for phone number
    phone_input = st.text_input("📱 Enter Phone Number (10 or 11 digits)", 
                               placeholder="e.g., 18576543210 or 7900000123",
                               key="phone_input")
    
    # Check button
    check_button = st.button("🔍 Check if Fancy")
    
    # Enhanced fancy number detection
    def is_fancy_number(phone_number):
        # Remove all non-digit characters
        clean_number = re.sub(r'[^\d]', '', phone_number)
        
        # Validate length (10 digits or 11 digits starting with 1)
        if len(clean_number) == 11 and clean_number.startswith('1'):
            clean_number = clean_number[1:]  # Remove country code
        elif len(clean_number) != 10:
            return False, "Invalid length (must be 10 digits or 11 digits starting with 1)"
        
        # Check for 6-digit sequences (123456, 987654)
        six_digit_sequences = [
            '012345', '123456', '234567', '345678', '456789', '567890',
            '987654', '876543', '765432', '654321', '543210'
        ]
        for seq in six_digit_sequences:
            if seq in clean_number:
                return True, f"6-digit sequence ({seq})"
        
        # Check for 3-digit sequences (444555, 121122)
        for i in range(len(clean_number)-5):
            chunk = clean_number[i:i+6]
            # Check for repeating 3-digit groups (444 555)
            if chunk[:3] == chunk[3:] and len(set(chunk[:3])) == 1:
                return True, f"Repeating 3-digit groups ({chunk[:3]} {chunk[3:]})"
            # Check for incremental patterns (121 122)
            if chunk[:3] == chunk[3:6] and len(set(chunk[:3])) > 1:
                return True, f"Repeating complex 3-digit groups ({chunk[:3]} {chunk[3:]})"
        
        # Check for 2-digit sequences (11 12 13, 20 20 20)
        for i in range(len(clean_number)-3):
            chunk = clean_number[i:i+4]
            # Check for incremental patterns (11 12 13)
            if (int(chunk[2:]) - int(chunk[:2]) == 1 and 
                int(chunk[:2]) - int(clean_number[i-2:i] if i >=2 else '0') == 1):
                return True, f"Incremental 2-digit sequence ({chunk[:2]} {chunk[2:]})"
            # Check for repeating 2-digit groups (20 20 20)
            if chunk[:2] == chunk[2:4]:
                return True, f"Repeating 2-digit groups ({chunk[:2]} {chunk[2:]})"
        
        # Check for exceptional cases (7900000123, 7900007555)
        # 4+ zeros in middle
        if re.search(r'[1-9]0{4,}[1-9]', clean_number):
            return True, "Exceptional case (4+ zeros in middle)"
        # Repeated special endings (555, 455, etc.)
        if re.search(r'([1-9]{2,})(\1){2,}$', clean_number):
            return True, "Exceptional case (repeated special ending)"
        
        # Check for long sequences (like 18576543210 -> 76543210)
        long_seq = '9876543210'
        if long_seq in clean_number:
            return True, f"Long sequence ({long_seq})"
        long_seq_rev = '0123456789'
        if long_seq_rev in clean_number:
            return True, f"Long sequence ({long_seq_rev})"
        
        # Check for all same digit
        if len(set(clean_number)) == 1:
            return True, "All same digit"
        
        # Check for mirror patterns
        if len(clean_number) == 10:
            first_half = clean_number[:5]
            second_half = clean_number[5:]
            if first_half == second_half[::-1]:
                return True, "Mirror pattern"
        
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
                "185-765-43210", "790-000-0123", "790-000-7555",
                "789-878-9555", "799-900-4455", "123-456-7890",
                "987-654-3210", "111-111-1111", "555-555-5555"
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

