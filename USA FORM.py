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

def is_sequential(digits, step=1):
    """Check if digits form a sequential pattern with given step"""
    return all(int(digits[i]) == int(digits[i-1]) + step for i in range(1, len(digits)))

def is_fancy_number(phone_number):
    clean_number = re.sub(r'\D', '', phone_number)
    
    # Get last 6 digits according to Lycamobile policy
    if len(clean_number) >= 6:
        last_six = clean_number[-6:]
        last_three = clean_number[-3:]
    else:
        return False, "Number too short (need at least 6 digits)"
    
    patterns = []
    
    # 1. 6-digit patterns (from both text policy and image table)
    # All same digits (666666)
    if len(set(last_six)) == 1:
        patterns.append("6 identical digits")
        
    # Consecutive ascending (123456)
    if is_sequential(last_six, 1):
        patterns.append("6-digit ascending sequence")
        
    # Consecutive descending (654321)
    if is_sequential(last_six, -1):
        patterns.append("6-digit descending sequence")
        
    # Palindrome (100001)
    if last_six == last_six[::-1]:
        patterns.append("6-digit palindrome")
    
    # 2. 3-digit patterns (from image table)
    # Double triplets (444555)
    first_triple = last_six[:3]
    second_triple = last_six[3:]
    
    # Same triplets (444555)
    if len(set(first_triple)) == 1 and len(set(second_triple)) == 1:
        patterns.append("Double triplets (444555)")
    
    # Similar triplets (121122)
    if first_triple[0] == first_triple[1] and second_triple[0] == second_triple[1]:
        patterns.append("Similar triplets (121122)")
    
    # Repeating triplets (786786)
    if first_triple == second_triple:
        patterns.append("Repeating triplets (786786)")
    
    # Nearly sequential (457456)
    if abs(int(first_triple) - int(second_triple)) == 1:
        patterns.append("Nearly sequential triplets (457456)")
    
    # 3. 2-digit patterns (from image table)
    # Incremental pairs (111213)
    pairs = [last_six[i:i+2] for i in range(0, 5)]
    if all(int(pairs[i]) == int(pairs[i-1]) + 1 for i in range(1, len(pairs))):
        patterns.append("Incremental pairs (111213)")
    
    # Repeating pairs (202020)
    if all(p == pairs[0] for p in pairs[::2]) and all(p == pairs[1] for p in pairs[1::2]):
        patterns.append("Repeating pairs (202020)")
    
    # Alternating pairs (010101)
    if pairs[0] == pairs[2] == pairs[4] and pairs[1] == pairs[3]:
        patterns.append("Alternating pairs (010101)")
    
    # Stepping pairs (324252)
    if all(int(pairs[i][1]) == int(pairs[i-1][1]) + 2 for i in range(1, len(pairs))):
        patterns.append("Stepping pairs (324252)")
    
    # 4. Special cases (from image table)
    # These would normally require additional verification
    special_cases = {
        '000000': "All zeros",
        '123456': "Classic ascending",
        '654321': "Classic descending",
        '111111': "All ones",
        '999999': "All nines",
        '100001': "Mirror pattern",
        '121212': "Perfect alternation",
        '112233': "Paired sequence"
    }
    if last_six in special_cases:
        patterns.append(special_cases[last_six])
    
    # 5. Exceptional cases (from image table)
    # These would normally require manual verification
    if last_three in ['123', '555', '777', '999']:
        patterns.append("Potential exceptional case (needs verification)")
    
    # Filter to only include patterns that meet Lycamobile's strict policy
    approved_patterns = [
        "6 identical digits",
        "6-digit ascending sequence",
        "6-digit descending sequence",
        "6-digit palindrome",
        "Double triplets (444555)",
        "Similar triplets (121122)",
        "Repeating triplets (786786)",
        "Nearly sequential triplets (457456)",
        "Incremental pairs (111213)",
        "Repeating pairs (202020)",
        "Alternating pairs (010101)",
        "Stepping pairs (324252)",
        "Potential exceptional case (needs verification)"
    ]
    
    valid_patterns = [p for p in patterns if any(ap in p for ap in approved_patterns)]
    
    return bool(valid_patterns), ", ".join(valid_patterns) if valid_patterns else "No qualifying fancy pattern"

# Streamlit UI
st.header("📱 Lycamobile Fancy Number Checker")
st.subheader("Official Policy: Analyzes last 6 digits only for qualifying patterns")

phone_input = st.text_input("Enter Phone Number", 
                          placeholder="e.g., 1555123456 or 44207123456")

col1, col2 = st.columns([1, 2])
with col1:
    if st.button("🔍 Check Number"):
        if not phone_input:
            st.warning("Please enter a phone number")
        else:
            is_fancy, pattern = is_fancy_number(phone_input)
            clean_number = re.sub(r'\D', '', phone_input)
            
            # Extract last 6 digits for display
            last_six = clean_number[-6:] if len(clean_number) >= 6 else clean_number
            formatted_num = f"{last_six[:3]}-{last_six[3:]}" if len(last_six) == 6 else last_six

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
    ### Lycamobile Fancy Number Policy
    **Qualifying Patterns (last 6 digits only):**
    
    #### 6-Digit Patterns
    - 123456 (ascending)
    - 987654 (descending)
    - 666666 (repeating)
    - 100001 (palindrome)
    
    #### 3-Digit Patterns  
    - 444 555 (double triplets)
    - 121 122 (similar triplets)
    - 786 786 (repeating triplets)
    - 457 456 (nearly sequential)
    
    #### 2-Digit Patterns
    - 11 12 13 (incremental)
    - 20 20 20 (repeating)
    - 01 01 01 (alternating)
    - 32 42 52 (stepping)
    
    #### Exceptional Cases
    - Ending with 123/555/777/999
    - Requires manual verification
    """)

# Test cases
debug_mode = st.checkbox("Show test cases", False)
if debug_mode:
    test_numbers = [
        ("123456", True),    # 6-digit ascending ✓
        ("987654", True),    # 6-digit descending ✓
        ("444555", True),    # Double triplets ✓
        ("121122", True),    # Similar triplets ✓
        ("786786", True),    # Repeating triplets ✓
        ("457456", True),    # Nearly sequential ✓
        ("111213", True),    # Incremental pairs ✓
        ("202020", True),    # Repeating pairs ✓
        ("010101", True),    # Alternating pairs ✓
        ("324252", True),    # Stepping pairs ✓
        ("7900000123", True), # Exceptional case ✓
        ("123458", False),   # No pattern ✗
        ("112233", True),    # Paired sequence ✓
        ("1555123123", True) # Ends with 123 (exceptional) ✓
    ]
    
    st.markdown("### Policy Validation Tests")
    for number, expected in test_numbers:
        is_fancy, pattern = is_fancy_number(number)
        result = "PASS" if is_fancy == expected else "FAIL"
        color = "green" if result == "PASS" else "red"
        st.write(f"<span style='color:{color}'>{number[-6:]}: {result} ({pattern})</span>", unsafe_allow_html=True)
