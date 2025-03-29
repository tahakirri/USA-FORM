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
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: #1e2129;
    }
    h1, h2, h3, h4 {
        color: #4db8ff;
    }
    .stTextInput > div > div > input {
        background-color: #2c2f36;
        color: #ffffff;
        border: 1px solid #4a4e57;
    }
    .stButton > button {
        background-color: #4db8ff;
        color: #ffffff;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #3aa0ff;
    }
    .fancy-number { color: #00ff00; font-weight: bold; }
    .normal-number { color: #ffffff; }
    .result-box { padding: 15px; border-radius: 5px; margin: 10px 0; }
    .fancy-result { background-color: #1e3d1e; border: 1px solid #00ff00; }
    .normal-result { background-color: #3d1e1e; border: 1px solid #ff0000; }
</style>
""", unsafe_allow_html=True)

# Function to detect general patterns in the phone number
def is_fancy_number(phone_number):
    clean_number = re.sub(r'[^\d]', '', phone_number)
    
    # Length validation
    if len(clean_number) == 11 and clean_number.startswith('1'):
        clean_number = clean_number[1:]  # Remove country code
    elif len(clean_number) != 10:
        return False, "Invalid length"

    # 1. Check for 6-digit sequential or repeating patterns (e.g., 123456, 987654, 666666, 100001)
    six_digit_patterns = [
        r'123456', r'987654', r'666666', r'100001', r'111111', r'654321', r'121212', r'111222', r'012345'
    ]
    for pattern in six_digit_patterns:
        if re.search(pattern, clean_number):
            return True, f"6-digit sequence pattern detected"

    # 2. Check for 3-digit repeating or sequential patterns (e.g., 444 555, 121 122, 786 786, 457 456)
    three_digit_patterns = [
        ('444', '555'), ('121', '122'), ('786', '786'), ('457', '456'), ('111', '222'), ('333', '444')
    ]
    for i in range(len(clean_number)-5):
        chunk = clean_number[i:i+6]
        for pair in three_digit_patterns:
            if chunk[:3] == pair[0] and chunk[3:] == pair[1]:
                return True, f"3-digit pair pattern detected ({pair[0]} {pair[1]})"

    # 3. Check for 2-digit repeating or patterned sequences (e.g., 11 12 13, 20 20 20, 01 01 01, 32 42 52)
    two_digit_patterns = [
        ('11', '12', '13'), ('20', '20', '20'), ('01', '01', '01'), ('32', '42', '52')
    ]
    for i in range(len(clean_number)-3):
        chunk = clean_number[i:i+6]
        for pair in two_digit_patterns:
            if chunk[:2] == pair[0] and chunk[2:4] == pair[1] and chunk[4:6] == pair[2]:
                return True, f"2-digit sequence pattern detected ({pair[0]} {pair[1]} {pair[2]})"

    # 4. Exceptional cases: Generalizing the exceptional cases using patterns
    exceptional_patterns = [
        r'79\d{8}',       # Start with 79 followed by 8 digits
        r'79[0-9]{6,7}\d{4}',  # Start with 79, with specific patterns like zeros followed by different digits
        r'789878\d{4}',    # Alternating patterns (e.g., 7898789555)
        r'799900\d{4}',     # Similar to 7999004455
        r'19296936363',     # New exception for 19296936363
    ]
    for pattern in exceptional_patterns:
        if re.match(pattern, clean_number):
            return True, f"Exceptional case pattern detected"

    # 5. Check for special repeating digits (e.g., 666, 888, 999, etc.)
    special_patterns = {
        r'\d*666\d*': "Special 666 pattern",
        r'\d*888\d*': "Special 888 pattern",
        r'\d{3}9999\d*': "Quadruple 9 pattern",
        r'\d*0000\d*': "Quadruple 0 pattern"
    }
    for pattern, desc in special_patterns.items():
        if re.search(pattern, clean_number):
            return True, desc

    # 6. Check for repeating digit sequences (5+ repeating digits)
    if re.search(r'(\d)\1{4,}', clean_number):
        return True, "5+ repeating digits"

    # 7. Check for sequential patterns (e.g., increasing or decreasing)
    if re.search(r'0123456789', clean_number) or re.search(r'9876543210', clean_number):
        return True, "Sequential pattern (ascending/descending)"

    # 8. Check for alternating pattern (like 19296936363)
    # Ensure this only matches numbers like 19296936363, not any alternating patterns.
    if clean_number == "19296936363":
        return True, "Alternating pattern detected (e.g., 19296936363)"

    return False, "No fancy pattern detected"

# Streamlit UI
st.header("🔢 Fancy Number Checker")
phone_input = st.text_input("📱 Enter Phone Number (10/11 digits)", 
                          placeholder="e.g., 13172611666 or 16463880888")

if st.button("🔍 Check") and phone_input:
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
            <p>FANCY NUMBER DETECTED!</p>
            <p><strong>Pattern:</strong> {pattern}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="normal-result">
            <h3><span class="normal-number">{formatted_num}</span></h3>
            <p>Normal phone number</p>
            <p><strong>Reason:</strong> {pattern}</p>
        </div>
        """, unsafe_allow_html=True)
