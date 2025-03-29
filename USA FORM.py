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

def is_fancy_number(phone_number):
    clean_number = re.sub(r'[^\d]', '', phone_number)
    
    # Length validation
    if len(clean_number) == 11 and clean_number.startswith('1'):
        clean_number = clean_number[1:]  # Remove country code
    elif len(clean_number) != 10:
        return False, "Invalid length"

    # 1. Check for triplets (666, 888, 999)
    if re.search(r'(\d)\1{2}', clean_number):
        triplet = re.search(r'(\d)\1{2}', clean_number).group()
        return True, f"Triplet pattern ({triplet})"

    # 2. Check 6-digit sequences from image
    six_digit_patterns = [
        '121456', '987654', '666666', '100001',
        '116666', '363636', '808888'  # Added patterns from user examples
    ]
    for pattern in six_digit_patterns:
        if pattern in clean_number:
            return True, f"6-digit sequence ({pattern})"

    # 3. Check 3-digit pairs from image
    three_digit_pairs = [
        ('441', '555'), ('121', '126'), 
        ('786', '786'), ('457', '456'),
        ('116', '666'), ('636', '363')  # Added pairs from user examples
    ]
    for i in range(len(clean_number)-5):
        chunk = clean_number[i:i+6]
        for pair in three_digit_pairs:
            if chunk[:3] == pair[0] and chunk[3:] == pair[1]:
                return True, f"3-digit pair ({pair[0]} {pair[1]})"

    # 4. Special number patterns
    special_patterns = {
        r'\d*666\d*': "Special 666 pattern",
        r'\d*888\d*': "Special 888 pattern",
        r'\d{3}9999\d*': "Quadruple 9 pattern",
        r'\d*0000\d*': "Quadruple 0 pattern"
    }
    for pattern, desc in special_patterns.items():
        if re.search(pattern, clean_number):
            return True, desc

    # 5. Repeating digit sequences
    if re.search(r'(\d)\1{4,}', clean_number):
        return True, "5+ repeating digits"

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
