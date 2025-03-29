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
    
    # Store all patterns found
    patterns_found = []
    
    # 1. Check for 6-digit repeating pattern (e.g., 900900)
    if len(clean_number) >= 6:
        for i in range(len(clean_number) - 5):
            if clean_number[i:i+3] == clean_number[i+3:i+6]:
                patterns_found.append(f"Repeating 3-digit pattern ({clean_number[i:i+3]}-{clean_number[i+3:i+6]})")
    
    # 2. Check for triplets (e.g., 111, 222, 333)
    triplet_matches = re.finditer(r'(\d)\1{2}', clean_number)
    for match in triplet_matches:
        patterns_found.append(f"Triplet pattern ({match.group()})")
    
    # 3. Check for 6-digit sequences from examples
    six_digit_patterns = {
        '123456': "Ascending sequence (123456)",
        '987654': "Descending sequence (987654)",
        '666666': "Repeated digit sequence (666666)",
        '100001': "Special pattern (100001)"
    }
    for pattern, desc in six_digit_patterns.items():
        if pattern in clean_number:
            patterns_found.append(desc)
    
    # 4. Check for 3-digit pairs from examples
    three_digit_pairs = [
        ('444', '555'), ('121', '122'), 
        ('786', '786'), ('457', '456')
    ]
    for i in range(len(clean_number) - 5):
        chunk = clean_number[i:i+6]
        for pair in three_digit_pairs:
            if chunk[:3] == pair[0] and chunk[3:] == pair[1]:
                patterns_found.append(f"3-digit pair pattern ({pair[0]}-{pair[1]})")
    
    # 5. Check for 2-digit sequences from examples
    two_digit_patterns = [
        ('11', '12', '13'), ('20', '20', '20'),
        ('32', '42', '52'), ('01', '01', '01')
    ]
    for pattern in two_digit_patterns:
        if len(pattern) == 3:  # For 3 consecutive 2-digit groups
            for i in range(len(clean_number) - 5):
                chunk = clean_number[i:i+6]
                if chunk[:2] == pattern[0] and chunk[2:4] == pattern[1] and chunk[4:6] == pattern[2]:
                    patterns_found.append(f"2-digit sequence ({pattern[0]}-{pattern[1]}-{pattern[2]})")
    
    # 6. Check for exceptional cases
    exceptional_cases = {
        '7900000123': "Special pattern with quad zeros (7900000123)",
        '7900007555': "Special pattern with triple 5s (7900007555)",
        '7898789555': "Special rhythmic pattern (7898789555)",
        '7999004455': "Double-double pattern (7999004455)"
    }
    for pattern, desc in exceptional_cases.items():
        if pattern in clean_number:
            patterns_found.append(desc)
    
    # 7. Check for quad patterns (4 identical digits in a row)
    quad_matches = re.finditer(r'(\d)\1{3}', clean_number)
    for match in quad_matches:
        patterns_found.append(f"Quad pattern ({match.group()})")
    
    # 8. Check for double-doubles (e.g., 1122, 5566)
    double_double_matches = re.finditer(r'(\d)\1(\d)\2', clean_number)
    for match in double_double_matches:
        patterns_found.append(f"Double-double pattern ({match.group()})")
    
    # 9. Check for ascending/descending sequences of at least 4 digits
    for i in range(len(clean_number) - 3):
        chunk = clean_number[i:i+4]
        # Check ascending (e.g., 1234, 5678)
        if all(int(chunk[j]) == int(chunk[j-1]) + 1 for j in range(1, 4)):
            patterns_found.append(f"Ascending sequence ({chunk})")
        # Check descending (e.g., 9876, 5432)
        if all(int(chunk[j]) == int(chunk[j-1]) - 1 for j in range(1, 4)):
            patterns_found.append(f"Descending sequence ({chunk})")
    
    # Return result
    if patterns_found:
        return True, ", ".join(patterns_found)
    else:
        return False, "No fancy pattern detected"

# Streamlit UI
st.header("🔢 Fancy Number Checker")
st.subheader("Check if your phone number has a fancy pattern")

phone_input = st.text_input("📱 Enter Phone Number (10/11 digits)", 
                          placeholder="e.g., 18147900900 or 16463880888")

col1, col2 = st.columns([1, 2])
with col1:
    if st.button("🔍 Check Number"):
        if not phone_input:
            st.warning("Please enter a phone number")
        else:
            is_fancy, pattern = is_fancy_number(phone_input)
            clean_number = re.sub(r'[^\d]', '', phone_input)
            
            # Format display
            if len(clean_number) == 10:
                formatted_num = f"{clean_number[:3]}-{clean_number[3:6]}-{clean_number[6:]}"
            elif len(clean_number) == 11 and clean_number.startswith('1'):
                formatted_num = f"1-{clean_number[1:4]}-{clean_number[4:7]}-{clean_number[7:]}"
            else:
                formatted_num = clean_number

            if is_fancy:
                st.markdown(f"""
                <div class="result-box fancy-result">
                    <h3><span class="fancy-number">✨ {formatted_num} ✨</span></h3>
                    <p>FANCY NUMBER DETECTED!</p>
                    <p><strong>Pattern:</strong> {pattern}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-box normal-result">
                    <h3><span class="normal-number">{formatted_num}</span></h3>
                    <p>Normal phone number</p>
                    <p><strong>Reason:</strong> {pattern}</p>
                </div>
                """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    ### Fancy Number Patterns
    
    #### 6-digit sequence fancy numbers:
    - 123456 (Ascending sequence)
    - 987654 (Descending sequence)
    - 666666 (Repeated digits)
    - 100001 (Special pattern)
    
    #### 3-digit sequence fancy numbers:
    - 444-555 (Paired sequences)
    - 121-122 (Paired sequences)
    - 786-786 (Repeated sequence)
    - 457-456 (Paired sequences)
    
    #### 2-digit sequence fancy numbers:
    - 11-12-13 (Sequential pairs)
    - 20-20-20 (Repeated pairs)
    - 32-42-52 (Pattern pairs)
    - 01-01-01 (Repeated pairs)
    
    #### Exceptional cases:
    - 7900000123 (Contains quad zeros)
    - 7900007555 (Special pattern with triple 5s)
    - 7898789555 (Rhythmic pattern)
    - 7999004455 (Double-double pattern)
    """)
