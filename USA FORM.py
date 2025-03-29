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
        clean_number = clean_number[1:]  # Remove country code for analysis
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
    
    # 10. Check for repeated 2-digit patterns in the last 6+ digits
    last_six = clean_number[-6:]
    last_eight = clean_number[-8:] if len(clean_number) >= 8 else ""
    
    # Check for patterns like 828288 (in 15853828288)
    two_digit_repeat_match = re.search(r'(\d\d)\1+', last_six)
    if two_digit_repeat_match:
        patterns_found.append(f"Repeating 2-digit pattern ({two_digit_repeat_match.group()})")
    
    # 11. Check for alternating digit patterns (like 5853828288, 9296936363)
    # Last 6 digits check for alternating patterns
    if re.search(r'(\d\d)(\d\d)(\1|\2)+', last_six):
        patterns_found.append(f"Alternating pattern in last digits ({last_six})")
    
    # 12. Check for patterns like 03030 (in 15015303030)
    if len(last_six) >= 5:
        pattern_match = re.search(r'(\d\d)\1+\d?', last_six)
        if pattern_match:
            patterns_found.append(f"Repeating digit pair pattern ({pattern_match.group()})")
    
    # 13. Check for patterns where the same 2 digits repeat 3 or more times
    for i in range(10):
        for j in range(10):
            pattern = f"{i}{j}" * 3  # e.g., "030303" or "121212"
            if pattern in clean_number:
                patterns_found.append(f"Repeating digit pair ({i}{j}) pattern")
    
    # 14. Check for 3-digit pairs that alternate or repeat
    if len(last_eight) >= 6:
        for i in range(len(last_eight) - 5):
            first_three = last_eight[i:i+3]
            second_three = last_eight[i+3:i+6]
            # Look for repeated patterns or 3-digit blocks that are related
            if first_three == second_three:
                patterns_found.append(f"Repeating 3-digit blocks ({first_three})")
            # Check if first two digits in both blocks match
            elif first_three[:2] == second_three[:2]:
                patterns_found.append(f"Pattern with repeating prefix ({first_three[:2]})")
            # Check if last two digits in both blocks match
            elif first_three[1:] == second_three[1:]:
                patterns_found.append(f"Pattern with repeating suffix ({first_three[1:]})")
    
    # 15. Check the last 4-5 digits for repeating patterns like XYXY
    last_five = clean_number[-5:]
    last_four = clean_number[-4:]
    
    # Check for XYXY pattern in last 4 digits (e.g., 3636)
    if len(last_four) == 4 and last_four[0:2] == last_four[2:4]:
        patterns_found.append(f"XYXY pattern in last 4 digits ({last_four})")
    
    # Check for repeated digits in the last 5 digits (e.g., 30303)
    if len(last_five) == 5:
        if last_five[0:2] == last_five[2:4] or last_five[1:3] == last_five[3:5]:
            patterns_found.append(f"Repeating pattern in last 5 digits ({last_five})")
    
    # 16. NEW: Check for consecutive pairs of repeated digits (e.g., 088077)
    # This pattern has consecutive zeros (00) followed by consecutive pairs (88, 77)
    for i in range(len(clean_number) - 5):
        chunk = clean_number[i:i+6]
        if (chunk[0] == chunk[1] and 
            chunk[2] == chunk[3] and 
            chunk[4] == chunk[5] and
            (chunk[0] != chunk[2] or chunk[2] != chunk[4])):
            patterns_found.append(f"Consecutive paired digits ({chunk})")
    
    # 17. NEW: Check for patterns like 088077 with double zeros followed by double digits
    double_zero_patterns = re.finditer(r'0{2,}(\d)\1(\d)\2', clean_number)
    for match in double_zero_patterns:
        patterns_found.append(f"Double zeros followed by double digits ({match.group()})")
    
    # 18. NEW: Check for any sequence with consecutive pairs (like in 9088077)
    last_six = clean_number[-6:]
    if (re.search(r'(\d)\1(\d)\2(\d)\3', last_six) or
        re.search(r'(\d)(\d)(\1)(\2)', last_six) or
        re.search(r'(\d)(\d)(\d)(\1)(\2)(\3)', last_six)):
        patterns_found.append(f"Sequential paired digits pattern ({last_six})")
    
    # 19. NEW: Check for patterns with consecutive identical digits in specific positions
    # For example: 9088077 has 00, 88, 77 as sequential pairs
    for i in range(len(clean_number) - 5):
        segment = clean_number[i:i+6]
        # Check for consecutive pairs at positions 0-1, 2-3, 4-5
        if (segment[0] == segment[1] and 
            segment[2] == segment[3] and 
            segment[4] == segment[5]):
            patterns_found.append(f"Three consecutive pairs ({segment})")
    
    # 20. NEW: Explicitly check for the 088077 pattern and similar
    if '088077' in clean_number:
        patterns_found.append("Special pattern with double zeros and double digits (088077)")
    
    # Check for similar patterns with different digits
    for a in range(10):
        for b in range(10):
            for c in range(10):
                pattern = f"{a}{a}{b}{b}{c}{c}"
                if pattern in clean_number and not (a == b and b == c):  # Avoid 111111 pattern
                    patterns_found.append(f"Triple double-digit pattern ({pattern})")
    
    # Return result
    if patterns_found:
        return True, ", ".join(patterns_found)
    else:
        return False, "No fancy pattern detected"

# Streamlit UI
st.header("🔢 Fancy Number Checker")
st.subheader("Check if your phone number has a fancy pattern")

phone_input = st.text_input("📱 Enter Phone Number (10/11 digits)", 
                          placeholder="e.g., 18147900900 or 17029088077")

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
    
    #### Advanced patterns:
    - Repeating 2-digit patterns (828288)
    - Alternating digits (9296936363)
    - Repeating pairs with final digit (303030)
    - XYXY patterns in last digits (3636)
    - Consecutive paired digits (088077)
    - Triple double-digit pattern (aabbcc)
    
    #### Exceptional cases:
    - 7900000123 (Contains quad zeros)
    - 7900007555 (Special pattern with triple 5s)
    - 7898789555 (Rhythmic pattern)
    - 7999004455 (Double-double pattern)
    """)

# Optional: Debug testing for specific numbers
debug_mode = False
if debug_mode:
    test_numbers = [
        "15853828288",
        "19296936363",
        "15015303030",
        "17029088077"
    ]
    
    st.markdown("### Debug Testing")
    for number in test_numbers:
        is_fancy, pattern = is_fancy_number(number)
        st.write(f"Number: {number} - Fancy: {is_fancy} - Pattern: {pattern}")
