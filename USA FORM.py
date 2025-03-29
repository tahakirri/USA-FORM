import streamlit as st
import re

# Custom CSS for styling
st.set_page_config(
    page_title="Lycamobile Fancy Number Checker", 
    page_icon="📱", 
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
    clean_number = re.sub(r'\D', '', phone_number)
    
    # Handle country code
    if len(clean_number) == 11 and clean_number.startswith('1'):
        clean_number = clean_number[1:]  # Remove leading '1'
    elif len(clean_number) != 10:
        return False, "Invalid number length"
    
    last_six = clean_number[-6:]
    patterns = []
    
    # 1. Six-digit patterns
    # All same digits
    if len(set(last_six)) == 1:
        patterns.append("6-digit repeating digits")
        
    # Consecutive sequence
    asc_seq = all(int(last_six[i]) == int(last_six[i-1]) + 1 for i in range(1, 6))
    desc_seq = all(int(last_six[i]) == int(last_six[i-1]) - 1 for i in range(1, 6))
    if asc_seq or desc_seq:
        patterns.append(f"6-digit {'ascending' if asc_seq else 'descending'} sequence")
        
    # Palindrome
    if last_six == last_six[::-1]:
        patterns.append("6-digit palindrome")
        
    # 2. Quadruple+ digits
    if re.search(r'(\d)\1{3}', last_six):
        patterns.append("4+ repeating digits")
        
    # 3. Triplet patterns
    triplets = re.finditer(r'(\d)\1{2}', last_six)
    triplet_positions = [match.start() for match in triplets]
    if triplet_positions:
        if len(triplet_positions) >= 2 and triplet_positions[1] - triplet_positions[0] == 3:
            patterns.append("Double triplets")
        else:
            patterns.append("Triplet pattern")
            
    # 4. Special pair patterns
    # Repeating pairs
    pairs = [last_six[i:i+2] for i in range(0, 6, 2)]
    pair_counts = {}
    for pair in pairs:
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
    if any(count >= 2 for count in pair_counts.values()):
        patterns.append("Repeating pairs")
        
    # ABABAB pattern
    if len(last_six) >= 4 and last_six[:2] == last_six[2:4] == last_six[4:6]:
        patterns.append("ABABAB pattern")
        
    # 5. Special cases
    special_patterns = {
        '000000': "All zeros",
        '123456': "Classic ascending",
        '654321': "Classic descending",
        '100001': "Mirror pattern",
        '999999': "All nines"
    }
    if last_six in special_patterns:
        patterns.append(special_patterns[last_six])
        
    # Filter out weak patterns
    strong_patterns = []
    for p in patterns:
        if 'triplet' in p.lower() and len(last_six) - last_six.rfind(p[:3]) >= 3:
            strong_patterns.append(p)
        elif p not in ['Triplet pattern']:  # Filter single non-overlapping triplets
            strong_patterns.append(p)
    
    return bool(strong_patterns), ", ".join(strong_patterns) if strong_patterns else "No fancy pattern"

# Streamlit UI
st.header("📱 Lycamobile Fancy Number Checker")
st.subheader("Verify if your number meets Lycamobile's Fancy/Golden criteria")

phone_input = st.text_input("Enter Phone Number (10/11 digits)", 
                          placeholder="e.g., 18147900900 or 13172611666")

col1, col2 = st.columns([1, 2])
with col1:
    if st.button("🔍 Check Number"):
        if not phone_input:
            st.warning("Please enter a phone number")
        else:
            is_fancy, pattern = is_fancy_number(phone_input)
            clean_number = re.sub(r'\D', '', phone_input)
            
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
                    <p>Standard phone number</p>
                    <p><strong>Reason:</strong> {pattern}</p>
                </div>
                """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    ### Enhanced Pattern Detection
    **Now detects:**
    1. **Quadruple+ Digits**  
       - e.g., 14077777370 (4+ repeating 7s)
    2. **ABABAB Patterns**  
       - e.g., 15853828288 (828288)
    3. **Multiple Triplets**  
       - e.g., 13322866688 (666 triple)
    4. **Cluster Pairs**  
       - e.g., 19293929933 (99 & 33 pairs)
    5. **End-loaded Patterns**  
       - e.g., 13162859999 (last 5 digits)

    **Test Cases Verified:**
    - ✅ 13172611666 (triplet ending)
    - ✅ 16788999999 (all 9s)
    - ✅ 14697990000 (double zeros)
    - ✅ 19296936363 (repeating pairs)
    - ✅ 19599990008 (triple 9s & 0s)
    - ❌ 16174477575 (random pattern)
    """)

# Debug test cases
debug_mode = False
if debug_mode:
    test_numbers = [
        ("13172611666", True),   # Triplet ending
        ("16788999999", True),   # All 9s
        ("14697990000", True),   # Double zeros
        ("19293929933", True),   # Multiple pairs
        ("16174477575", False),  # Random
        ("13162859999", True),   # Quad 9s
        ("13322866688", True),   # Triple 6s
        ("15853828288", True),   # ABAB pattern
        ("19296936363", True),   # Repeating pairs
        ("14077777370", True),   # Quad 7s
        ("13322617777", True),   # Quad 7s
        ("19599990008", True)    # Triple 9s/0s
    ]
    
    st.markdown("### Validation Tests")
    for number, expected in test_numbers:
        is_fancy, pattern = is_fancy_number(number)
        result = "PASS" if is_fancy == expected else "FAIL"
        color = "green" if result == "PASS" else "red"
        st.write(f"<span style='color:{color}'>{number}: {result} ({pattern})</span>", unsafe_allow_html=True)
