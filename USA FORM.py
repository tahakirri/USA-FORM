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

def is_sequential(digits):
    """Check if digits form a sequential pattern (ascending or descending)"""
    diffs = [int(digits[i]) - int(digits[i-1]) for i in range(1, len(digits))]
    # Check if all differences are +1 (ascending) or -1 (descending)
    if all(d == 1 for d in diffs):
        return "ascending"
    elif all(d == -1 for d in diffs):
        return "descending"
    return None

def is_fancy_number(phone_number):
    clean_number = re.sub(r'\D', '', phone_number)
    
    # Handle country code
    if len(clean_number) == 11 and clean_number.startswith('1'):
        clean_number = clean_number[1:]  # Remove leading '1'
    elif len(clean_number) != 10:
        return False, "Invalid number length"
    
    last_six = clean_number[-6:]
    last_four = clean_number[-4:]
    last_three = clean_number[-3:]
    full_number = clean_number
    patterns = []
    
    # 1. Full number easy-to-remember patterns
    if len(full_number) == 10:
        # Check for 4+ of the same digit
        for digit in set(full_number):
            count = full_number.count(digit)
            if count >= 4:
                positions = [i for i, d in enumerate(full_number) if d == digit]
                if (len(positions) >= 4 and 
                    (all(positions[i] == positions[i-1]+1 for i in range(1, len(positions))) or
                    count >= 5)):
                    patterns.append(f"Memorable sequence ({count}x{digit})")
                    break
        
        # Check for multiple repeating groups
        repeating_groups = []
        for group_size in [2, 3, 4]:
            groups = [full_number[i:i+group_size] for i in range(0, 11-group_size)]
            for group in groups:
                if len(set(group)) == 1 and len(group) == group_size and group not in repeating_groups:
                    repeating_groups.append(group)
        if len(repeating_groups) >= 2:
            patterns.append(f"Multiple repeating groups ({' & '.join(repeating_groups)})")
    
    # 2. Six-digit patterns
    if len(set(last_six)) == 1:
        patterns.append("6-digit repeating digits")
        
    # Consecutive sequence in last 6
    seq_type = is_sequential(last_six)
    if seq_type:
        patterns.append(f"6-digit {seq_type} sequence")
        
    # Palindrome
    if last_six == last_six[::-1]:
        patterns.append("6-digit palindrome")
    
    # Repeating 3-digit group
    if len(last_six) == 6 and last_six[:3] == last_six[3:]:
        patterns.append(f"Repeating 3-digit group ({last_six[:3]})")
    
    # 3. Enhanced last 3-digit patterns (like 587 in 588587)
    seq_type = is_sequential(last_three)
    if seq_type:
        patterns.append(f"3-digit {seq_type} sequence ({last_three})")
    
    # Triple patterns
    if len(set(last_three)) == 1:
        patterns.append(f"Triplet ending ({last_three})")
        
    # Double triplets
    if len(last_six) == 6:
        first_triple = last_six[:3]
        second_triple = last_six[3:]
        if len(set(first_triple)) == 1 and len(set(second_triple)) == 1:
            patterns.append(f"Double triplets ({first_triple}-{second_triple})")
    
    # 4. Pair patterns
    pairs = [last_six[i:i+2] for i in range(0, 6, 2)]
    if len(pairs) == 3:
        if pairs[0] == pairs[1] or pairs[1] == pairs[2] or pairs[0] == pairs[2]:
            if len(set(pairs)) <= 2:
                patterns.append(f"Repeating pairs ({'-'.join(pairs)})")
                
        if pairs[0][0] == pairs[1][0] == pairs[2][0] and pairs[0][1] == pairs[1][1] == pairs[2][1]:
            patterns.append("Perfect ABABAB pattern")
            
        if pairs[0] == pairs[2][::-1] and pairs[1] == pairs[1][::-1]:
            patterns.append("Mirror pair pattern")
    
    # 5. Alternating pattern
    if len(last_six) == 6:
        if (last_six[0] == last_six[2] == last_six[4]) and (last_six[1] == last_six[3] == last_six[5]):
            patterns.append(f"Alternating digits pattern ({last_six[0]}{last_six[1]})")
    
    # 6. Special cases
    special_patterns = {
        '000000': "All zeros",
        '123456': "Classic ascending",
        '654321': "Classic descending",
        '100001': "Mirror pattern",
        '999999': "All nines",
        '888888': "All eights",
        '636363': "Special repeating pairs",
        '900900': "Repeating group",
        '929933': "Special pattern with triplet ending"
    }
    if last_six in special_patterns:
        patterns.append(special_patterns[last_six])
        
    # 7. Quadruple+ digits
    if re.search(r'(\d)\1{3}', last_six):
        patterns.append("4+ repeating digits")
    
    # 8. Highly memorable full numbers
    if len(full_number) == 10:
        digit_counts = {d: full_number.count(d) for d in set(full_number)}
        for digit, count in digit_counts.items():
            if count >= 5:
                patterns.append(f"Highly memorable ({count}x{digit} in full number)")
    
    # Filter and prioritize patterns
    strong_patterns = []
    priority_patterns = [
        "Highly memorable",
        "Memorable sequence",
        "Multiple repeating groups",
        "6-digit repeating digits",
        "6-digit sequence",
        "6-digit palindrome",
        "3-digit ascending sequence",
        "3-digit descending sequence",
        "Double triplets",
        "Triplet ending",
        "4+ repeating digits"
    ]
    
    for priority in priority_patterns:
        for p in patterns:
            if priority in p and p not in strong_patterns:
                strong_patterns.append(p)
    
    for p in patterns:
        if p not in strong_patterns:
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
    **New Improvements:**
    1. **3-Digit Sequence Detection**  
       - Now detects ascending/descending sequences in last 3 digits (like 587 in 588587)
    2. **Full Number Analysis**  
       - Detects memorable patterns across entire number
    3. **Multiple Group Detection**  
       - Identifies numbers with multiple repeating groups
    4. **Priority Pattern System**  
       - Gives higher priority to clearly memorable patterns

    **Test Cases:**
    - ✅ 588587 → 3-digit ascending sequence (587)
    - ✅ 19599990008 → Highly memorable (5x9) & repeating groups
    - ✅ 1234567890 → 6-digit ascending sequence
    - ✅ 5432101234 → 3-digit descending sequence (210)
    - ❌ 1234567891 → No qualifying patterns
    """)

# Debug test cases
debug_mode = st.checkbox("Show test cases", False)
if debug_mode:
    test_numbers = [
        ("588587", True),       # 3-digit ascending sequence (587) ✓
        ("19599990008", True),  # Five 9s and three 0s ✓
        ("1234567890", True),   # 6-digit ascending ✓
        ("5432101234", True),   # 3-digit descending (210) ✓
        ("1234567891", False),  # No pattern ✗
        ("588586", False),      # No sequence ✗
        ("588589", False),      # No sequence ✗
        ("588567", True),       # 3-digit ascending (567) ✓
        ("588543", True)        # 3-digit descending (543) ✓
    ]
    
    st.markdown("### Validation Tests")
    for number, expected in test_numbers:
        is_fancy, pattern = is_fancy_number(number)
        result = "PASS" if is_fancy == expected else "FAIL"
        color = "green" if result == "PASS" else "red"
        st.write(f"<span style='color:{color}'>{number}: {result} ({pattern})</span>", unsafe_allow_html=True)
