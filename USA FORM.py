import streamlit as st
import re

# Custom CSS for dark mode and enhanced styling
st.set_page_config(
    page_title="Fancy Number Checker", 
    page_icon="🔢", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* [Previous CSS styles remain exactly the same] */
</style>
""", unsafe_allow_html=True)

# Fancy Number Checker App
st.header("🔢 Fancy Number Checker")

def is_fancy_number(phone_number):
    clean_number = re.sub(r'[^\d]', '', phone_number)
    
    # Validate length
    if len(clean_number) == 11 and clean_number.startswith('1'):
        clean_number = clean_number[1:]  # Remove country code
    elif len(clean_number) != 10:
        return False, "Invalid length (must be 10 digits or 11 digits starting with 1)"

    # 1. Check for repeating triplets (like 900900 in 18147900900)
    if re.search(r'(\d{3})\1', clean_number):
        triplet = re.search(r'(\d{3})\1', clean_number).group(1)
        return True, f"Repeating triplets ({triplet} {triplet})"

    # 2. Check 6-digit sequences from the image
    six_digit_patterns = [
        '123456', '987654', '666666', '100001'
    ]
    for pattern in six_digit_patterns:
        if pattern in clean_number:
            return True, f"6-digit sequence ({pattern})"

    # 3. Check 3-digit sequences from the image
    three_digit_groups = [
        ('444', '555'), ('121', '122'), 
        ('786', '786'), ('457', '456')
    ]
    for i in range(len(clean_number)-5):
        chunk = clean_number[i:i+6]
        for group in three_digit_groups:
            if chunk[:3] == group[0] and chunk[3:] == group[1]:
                return True, f"3-digit sequence ({group[0]} {group[1]})"

    # [Rest of the pattern checks remain the same...]

    return False, "No fancy pattern detected"

# User Interface
phone_input = st.text_input("📱 Enter Phone Number (10 or 11 digits)", 
                          placeholder="e.g., 18147900900 or 16463880888")

if st.button("🔍 Check if Fancy") and phone_input:
    is_fancy, pattern = is_fancy_number(phone_input)
    clean_number = re.sub(r'[^\d]', '', phone_input)
    
    # Format display
    formatted_num = (f"{clean_number[:3]}-{clean_number[3:6]}-{clean_number[6:]}" 
                    if len(clean_number) == 10 else 
                    f"{clean_number[0]}-{clean_number[1:4]}-{clean_number[4:7]}-{clean_number[7:]}")
    
    if is_fancy:
        st.markdown(f"""
        <div class="fancy-result">
            <h3><span class="fancy-number">✨ {formatted_num} ✨</span></h3>
            <p>This is a <strong>FANCY</strong> phone number!</p>
            <p><strong>Pattern:</strong> {pattern}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="normal-result">
            <h3><span class="normal-number">{formatted_num}</span></h3>
            <p>This is a normal phone number</p>
            <p><strong>Analysis:</strong> {pattern}</p>
        </div>
        """, unsafe_allow_html=True)
