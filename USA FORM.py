import streamlit as st
import re

# Custom CSS for dark mode and enhanced styling
st.set_page_config(
    page_title="Lycamobile Fancy Number Checker", 
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

def is_lycamobile_fancy_number(phone_number):
    clean_number = re.sub(r'[^\d]', '', phone_number)
    
    # Length validation
    if len(clean_number) == 11 and clean_number.startswith('1'):
        clean_number = clean_number[1:]  # Remove country code for analysis
    elif len(clean_number) != 10:
        return False, "Invalid length (must be 10 or 11 digits)"
    
    # Focus only on the last 6 digits for Lycamobile classification
    last_six = clean_number[-6:]
    
    # Store all patterns found
    patterns_found = []
    
    # 1. Check for 6-digit sequences (must match exactly)
    # Ascending sequence (e.g., 123456, 234567)
    if all(int(last_six[i]) == int(last_six[i-1]) + 1 for i in range(1, 6)):
        patterns_found.append("6-digit ascending sequence")
    
    # Descending sequence (e.g., 987654, 876543)
    if all(int(last_six[i]) == int(last_six[i-1]) - 1 for i in range(1, 6)):
        patterns_found.append("6-digit descending sequence")
    
    # All identical digits (e.g., 666666, 999999)
    if len(set(last_six)) == 1:
        patterns_found.append("6-digit repeated digits")
    
    # Special patterns (e.g., 100001)
    special_patterns = {
        '100001': "Special pattern (100001)",
        '123123': "Repeating block (123123)",
        '345543': "Mirror sequence (345543)",
        '122221': "Palindromic structure (122221)",
        '808808': "Mirrored block (808808)"
    }
    for pattern, desc in special_patterns.items():
        if pattern in last_six:
            patterns_found.append(desc)
    
    # 2. Check for 3-digit sequences (must be two consecutive 3-digit patterns)
    if len(last_six) >= 6:
        first_three = last_six[:3]
        second_three = last_six[3:]
        
        # Same triplet repeated (e.g., 444444)
        if first_three == second_three and len(set(first_three)) == 1:
            patterns_found.append("Repeated identical triplet")
        
        # Related triplets (e.g., 444555, 121122)
        if (len(set(first_three)) == 1 and 
            len(set(second_three)) == 1 and 
            first_three != second_three):
            patterns_found.append(f"Paired triplets ({first_three}-{second_three})")
        
        # Sequential triplets (e.g., 123456 would be 123-456)
        if (all(int(first_three[i]) == int(first_three[i-1]) + 1 for i in range(1, 3)) and 
            all(int(second_three[i]) == int(second_three[i-1]) + 1 for i in range(1, 3)) and 
            int(second_three[0]) == int(first_three[-1]) + 1):
            patterns_found.append("Sequential triplets forming 6-digit sequence")
    
    # 3. Check for 2-digit sequences (three consecutive 2-digit patterns)
    if len(last_six) >= 6:
        # Extract three 2-digit pairs
        pairs = [last_six[i:i+2] for i in range(0, 6, 2)]
        
        # All pairs identical (e.g., 121212)
        if len(set(pairs)) == 1:
            patterns_found.append("Repeated 2-digit sequence")
        
        # Ascending pairs (e.g., 111213)
        if all(int(pairs[i]) == int(pairs[i-1]) + 1 for i in range(1, 3)):
            patterns_found.append("Ascending 2-digit sequence")
        
        # Related pairs (e.g., 202020, 010101)
        if pairs[0] == pairs[1] == pairs[2]:
            patterns_found.append("Identical 2-digit sequence")
        
        # Pattern pairs (e.g., 324252)
        if (all(pairs[i][0] == pairs[0][0] for i in range(1, 3)) and 
            all(int(pairs[i][1]) == int(pairs[i-1][1]) + 1 for i in range(1, 3))):
            patterns_found.append("Patterned 2-digit sequence")
    
    # 4. Check for mirror sequences and palindromic structures
    # Full mirror (e.g., 345543)
    if last_six == last_six[::-1]:
        patterns_found.append("Perfect mirror/palindrome")
    
    # Partial mirror (e.g., 808808)
    if len(last_six) == 6 and last_six[:3] == last_six[3:][::-1]:
        patterns_found.append("Mirrored 3-digit block")
    
    # 5. Check for repeating block patterns (e.g., 345345, 123123)
    if len(last_six) == 6 and last_six[:3] == last_six[3:]:
        patterns_found.append("Repeating 3-digit block")
    
    # 6. Check for exceptional cases that might need verification
    exceptional_cases = {
        '088077': "Double-double pattern (088077)",
        '090909': "Alternating pattern with zero (090909)",
        '070707': "Alternating pattern with zero (070707)"
    }
    for pattern, desc in exceptional_cases.items():
        if pattern in last_six:
            patterns_found.append(desc)
    
    # Return result based on patterns found
    if patterns_found:
        return True, ", ".join(patterns_found)
    else:
        return False, "No Lycamobile fancy pattern detected in last 6 digits"

# Streamlit UI
st.header("🔢 Lycamobile Fancy Number Checker")
st.subheader("Check if your phone number qualifies as a Fancy/Golden number")

phone_input = st.text_input("📱 Enter Phone Number (10/11 digits)", 
                          placeholder="e.g., 18147900900 or 17029088077")

col1, col2 = st.columns([1, 2])
with col1:
    if st.button("🔍 Check Number"):
        if not phone_input:
            st.warning("Please enter a phone number")
        else:
            is_fancy, pattern = is_lycamobile_fancy_number(phone_input)
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
                    <p>LYCAMOBILE FANCY/GOLDEN NUMBER DETECTED!</p>
                    <p><strong>Pattern in last 6 digits:</strong> {pattern}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-box normal-result">
                    <h3><span class="normal-number">{formatted_num}</span></h3>
                    <p>Not a Lycamobile Fancy/Golden number</p>
                    <p><strong>Reason:</strong> {pattern}</p>
                </div>
                """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    ### Lycamobile Fancy/Golden Number Patterns
    
    #### 6-digit sequence patterns:
    - **123456** (Ascending sequence)
    - **987654** (Descending sequence)
    - **666666** (Repeated digits)
    - **100001** (Special pattern)
    - **345543** (Mirror sequence)
    - **122221** (Palindromic structure)
    - **808808** (Mirrored block)
    
    #### 3-digit sequence patterns:
    - **444555** (Paired triplets)
    - **121122** (Related triplets)
    - **786786** (Repeated triplet)
    - **457456** (Sequential triplets)
    
    #### 2-digit sequence patterns:
    - **111213** (Ascending pairs)
    - **202020** (Repeated pairs)
    - **010101** (Repeated pairs)
    - **324252** (Patterned pairs)
    
    #### Mirror and palindromic patterns:
    - **345543** (Perfect mirror)
    - **122221** (Palindrome)
    - **808808** (Mirrored block)
    
    #### Repeating block patterns:
    - **123123** (Repeating 3-digit block)
    - **456456** (Repeating 3-digit block)
    
    #### Exceptional cases:
    - **088077** (Double-double pattern)
    - **090909** (Alternating pattern)
    - **070707** (Alternating pattern)
    
    *Note: Only the last 6 digits are analyzed for fancy number classification.*
    """)

# Optional: Debug testing for specific numbers
debug_mode = False
if debug_mode:
    test_numbers = [
        "1234567890",  # Ascending sequence
        "9876543210",  # Descending sequence
        "5555555555",  # Repeated digits
        "18080880888", # Mirrored block
        "17029088077", # Double-double pattern
        "12408692892", # Should NOT be fancy
        "15853828288",
        "19296936363"
    ]
    
    st.markdown("### Debug Testing")
    for number in test_numbers:
        is_fancy, pattern = is_lycamobile_fancy_number(number)
        st.write(f"Number: {number} - Fancy: {is_fancy} - Pattern: {pattern}")
