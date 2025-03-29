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

def is_fancy_number(phone_number):
    clean_number = re.sub(r'[^\d]', '', phone_number)
    
    # Length validation
    if len(clean_number) == 11 and clean_number.startswith('1'):
        clean_number = clean_number[1:]  # Remove country code for analysis
    elif len(clean_number) != 10:
        return False, "Invalid length"
    
    # According to Lycamobile policy, only analyze the last 6 digits
    last_six = clean_number[-6:]
    
    # Store all patterns found
    patterns_found = []
    
    # 1. Check for 5-digit sequences within the last 6 digits
    # Ascending sequence (e.g., 12345)
    if any(last_six[i:i+5] in "0123456789" for i in range(2)):
        patterns_found.append(f"5-digit ascending sequence in last 6 digits ({last_six})")
    
    # Descending sequence (e.g., 98765)
    if any(last_six[i:i+5] in "9876543210" for i in range(2)):
        patterns_found.append(f"5-digit descending sequence in last 6 digits ({last_six})")
    
    # Repeated digits (e.g., 66666)
    five_repeat = re.search(r'(\d)\1{4}', last_six)
    if five_repeat:
        patterns_found.append(f"5 repeated digits ({five_repeat.group()})")
    
    # Mirrored patterns (e.g., 12321)
    for i in range(2):
        if i+5 <= len(last_six):
            segment = last_six[i:i+5]
            if segment == segment[::-1]:
                patterns_found.append(f"Mirrored 5-digit pattern ({segment})")
    
    # 2. Check for 3-digit sequences
    # Repeated triplets (e.g., 444555)
    if len(last_six) == 6:
        first_three = last_six[:3]
        second_three = last_six[3:]
        if first_three == second_three:
            patterns_found.append(f"Repeated 3-digit pattern ({first_three}-{second_three})")
        # Closely related patterns (e.g., 121122, 457456)
        elif (first_three[:2] == second_three[:2] or 
              first_three[1:] == second_three[1:] or
              first_three[:1] + first_three[2:] == second_three[:1] + second_three[2:]):
            patterns_found.append(f"Related 3-digit pattern ({first_three}-{second_three})")
    
    # 3. Check for 2-digit sequences
    # Repeated or incremental pairs (e.g., 111213, 202020, 010101, 324252)
    if len(last_six) == 6:
        pairs = [last_six[i:i+2] for i in range(0, 6, 2)]
        
        # Repeated pairs (202020, 010101)
        if pairs[0] == pairs[1] == pairs[2]:
            patterns_found.append(f"Repeated 2-digit sequence ({pairs[0]}-{pairs[1]}-{pairs[2]})")
        
        # Incremental pairs (e.g., 111213, 324252)
        try:
            if (int(pairs[1]) == int(pairs[0]) + 1 and int(pairs[2]) == int(pairs[1]) + 1) or \
               (pairs[0][0] == pairs[1][0] == pairs[2][0] and 
                int(pairs[0][1]) + 1 == int(pairs[1][1]) and 
                int(pairs[1][1]) + 1 == int(pairs[2][1])):
                patterns_found.append(f"Incremental 2-digit sequence ({pairs[0]}-{pairs[1]}-{pairs[2]})")
        except ValueError:
            pass  # Skip if conversion to int fails
    
    # 4. Check for mirror sequences and symmetrical patterns
    # Palindromic structure (e.g., 345543, 122221)
    if last_six == last_six[::-1]:
        patterns_found.append(f"Palindromic pattern ({last_six})")
    
    # Check for symmetrical patterns like 808808
    if len(last_six) == 6:
        if last_six[:3] == last_six[3:]:
            patterns_found.append(f"Symmetrical pattern ({last_six[:3]}-{last_six[3:]})")
    
    # 5. Repeating block patterns
    # Numbers that repeat a block of three or more digits (e.g., 345345, 123123)
    # Already covered in the 3-digit sequences check
    
    # 6. Check for triplets (e.g., 111, 222, 333)
    triplet_matches = re.finditer(r'(\d)\1{2}', last_six)
    for match in triplet_matches:
        patterns_found.append(f"Triplet pattern ({match.group()})")
    
    # 7. Check for quad patterns (4 identical digits in a row)
    quad_matches = re.finditer(r'(\d)\1{3}', last_six)
    for match in quad_matches:
        patterns_found.append(f"Quad digit pattern ({match.group()})")
    
    # 8. Check for double-doubles (e.g., 1122, 5566)
    double_double_matches = re.finditer(r'(\d)\1(\d)\2', last_six)
    for match in double_double_matches:
        patterns_found.append(f"Double-double pattern ({match.group()})")
    
    # 9. Check for XYXY pattern (e.g., 3636)
    for i in range(len(last_six) - 3):
        segment = last_six[i:i+4]
        if segment[:2] == segment[2:4] and segment[0] != segment[1]:
            patterns_found.append(f"XYXY pattern ({segment})")
    
    # 10. Check for alternating digits (e.g., 525252)
    if len(last_six) >= 6:
        if all(last_six[i] == last_six[i%2] for i in range(6)):
            patterns_found.append(f"Alternating digit pattern ({last_six})")
    
    # Return result based on patterns found
    if patterns_found:
        return True, ", ".join(patterns_found)
    else:
        return False, "No fancy pattern detected"

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
            is_fancy, pattern = is_fancy_number(phone_input)
            clean_number = re.sub(r'[^\d]', '', phone_input)
            
            # Format display
            if len(clean_number) == 10:
                formatted_num = f"{clean_number[:3]}-{clean_number[3:6]}-{clean_number[6:]}"
            elif len(clean_number) == 11 and clean_number.startswith('1'):
                formatted_num = f"1-{clean_number[1:4]}-{clean_number[4:7]}-{clean_number[7:]}"
            else:
                formatted_num = clean_number

            # Highlight the last 6 digits specifically
            if len(clean_number) >= 6:
                last_six = clean_number[-6:]
                if len(clean_number) == 10:
                    formatted_last_six = f"{last_six[:3]}-{last_six[3:]}"
                    formatted_prefix = f"{clean_number[:4]}-"
                elif len(clean_number) == 11:
                    formatted_last_six = f"{last_six[:3]}-{last_six[3:]}"
                    formatted_prefix = f"1-{clean_number[1:5]}-"
                else:
                    formatted_last_six = last_six
                    formatted_prefix = clean_number[:-6]
            else:
                formatted_last_six = clean_number
                formatted_prefix = ""
                
            if is_fancy:
                st.markdown(f"""
                <div class="result-box fancy-result">
                    <h3>{formatted_prefix}<span class="fancy-number">✨ {formatted_last_six} ✨</span></h3>
                    <p>FANCY/GOLDEN NUMBER DETECTED!</p>
                    <p><strong>Pattern:</strong> {pattern}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-box normal-result">
                    <h3><span class="normal-number">{formatted_num}</span></h3>
                    <p>Regular number</p>
                    <p><strong>Reason:</strong> {pattern}</p>
                </div>
                """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    ### Lycamobile Fancy/Golden Number Patterns
    
    According to Lycamobile's classification policy, only the **last six digits** are analyzed for determining if a number is fancy/golden.
    
    #### 5-digit Sequences:
    - Consecutive ascending (e.g., 12345)
    - Consecutive descending (e.g., 98765)
    - Repeated digits (e.g., 66666)
    - Mirrored patterns (e.g., 12321)
    
    #### 3-digit Sequences:
    - Repeated triplets (e.g., 444555)
    - Related triplets (e.g., 121122, 786786, 457456)
    
    #### 2-digit Sequences:
    - Repeated pairs (e.g., 202020, 010101)
    - Incremental pairs (e.g., 111213, 324252)
    
    #### Mirror and Symmetrical Patterns:
    - Palindromic structures (e.g., 345543, 122221)
    - Symmetrical patterns (e.g., 808808)
    
    #### Repeating Block Patterns:
    - Repeating blocks of digits (e.g., 345345, 123123)
    
    #### Other Recognized Patterns:
    - Triplets of same digit (e.g., 111, 222)
    - Quad digits (e.g., 9999)
    - Double-doubles (e.g., 1122, 5566)
    - Alternating digits (e.g., 525252)
    - XYXY patterns (e.g., 3636)
    """)
