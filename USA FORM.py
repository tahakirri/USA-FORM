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
    
    last_six = clean_number[-6:]
    
    # Store all patterns found
    patterns_found = []
    
    # 1. Check for sequences of 4+ identical digits (main fix for 116666 case)
    for i in range(len(last_six) - 3):
        if last_six[i] == last_six[i+1] == last_six[i+2] == last_six[i+3]:
            # Check how long this sequence continues
            j = i + 4
            while j < len(last_six) and last_six[j] == last_six[i]:
                j += 1
            seq_length = j - i
            patterns_found.append(f"{seq_length} repeated {last_six[i]}s ({last_six[i:j]})")
    
    # 2. Check for 5-digit sequences within the last 6 digits
    for i in [0, 1]:  # Only check first and second positions in 6-digit segment
        segment = last_six[i:i+5]
        
        # Ascending sequence (e.g., 12345)
        if segment in "0123456789":
            patterns_found.append(f"5-digit ascending sequence ({segment})")
        
        # Descending sequence (e.g., 98765)
        if segment in "9876543210":
            patterns_found.append(f"5-digit descending sequence ({segment})")
        
        # Mirrored patterns (e.g., 12321)
        if segment == segment[::-1]:
            patterns_found.append(f"Mirrored 5-digit pattern ({segment})")
    
    # 3. Check for special 6-digit patterns
    # All same digit (e.g., 666666)
    if len(set(last_six)) == 1:
        patterns_found.append(f"6 repeated digits ({last_six})")
    
    # Alternating pattern (e.g., 121212)
    if all(last_six[i] == last_six[i%2] for i in range(6)):
        patterns_found.append(f"Perfect alternating pattern ({last_six})")
    
    # 4. Check for repeated/mirrored 3-digit blocks
    if len(last_six) == 6:
        first_three = last_six[:3]
        second_three = last_six[3:]
        
        # Repeated triplets (e.g., 123123)
        if first_three == second_three:
            patterns_found.append(f"Repeated 3-digit pattern ({first_three}-{second_three})")
        
        # Mirrored triplets (e.g., 123321)
        if last_six == last_six[::-1]:
            patterns_found.append(f"Perfect mirrored pattern ({last_six})")
        
        # Double triplets (e.g., 111222)
        if len(set(first_three)) == 1 and len(set(second_three)) == 1 and first_three != second_three:
            patterns_found.append(f"Double triplets ({first_three}-{second_three})")
    
    # 5. Check for special 4-digit patterns
    for i in range(3):  # Check all possible 4-digit segments in last 6 digits
        segment = last_six[i:i+4]
        
        # XYXY pattern (e.g., 1212)
        if segment[:2] == segment[2:4] and segment[0] != segment[1]:
            patterns_found.append(f"XYXY pattern ({segment})")
    
    # Return result based on patterns found
    if patterns_found:
        # Filter to only show the most significant patterns
        significant_patterns = []
        for pattern in patterns_found:
            # Always include 4+ repeated digits, 5+ sequences, and special 6-digit patterns
            if ("repeated" in pattern and int(pattern.split()[0]) >= 4) or \
               ("5-digit" in pattern) or \
               ("6 repeated" in pattern) or \
               ("Perfect" in pattern) or \
               ("Double triplets" in pattern) or \
               ("Repeated 3-digit" in pattern):
                significant_patterns.append(pattern)
        
        if significant_patterns:
            return True, ", ".join(significant_patterns)
    
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
    
    #### Strong Patterns (Qualify as Fancy):
    - 4+ identical digits in sequence (e.g., 116666, 5555)
    - 5+ digit sequences (ascending/descending)
    - Perfect mirrored numbers (e.g., 123321)
    - Repeated 3-digit blocks (e.g., 123123)
    - Double triplets (e.g., 111222)
    - Perfect alternating patterns (e.g., 121212)
    
    #### Weak Patterns (Don't Qualify):
    - Simple triplets alone (e.g., 555)
    - Short XY patterns (e.g., 1212 in a longer sequence)
    - Isolated repeating digits
    
    #### Examples of Fancy Numbers:
    - 116666 (quad 6s)
    - 123456 (ascending)
    - 654321 (descending)
    - 111222 (double triplet)
    - 123123 (repeated block)
    - 123321 (mirrored)
    - 121212 (alternating)
    """)

# Debug testing
if st.checkbox("Show debug examples"):
    test_numbers = [
        "13172611666",  # Last 6: 116666 (quad 6s) - FANCY
        "16109055580",  # Last 6: 55580 (only triplet 5s) - NOT FANCY
        "1234567890",   # Last 6: 456789 (ascending) - FANCY
        "18005555555",  # Last 6: 555555 (all 5s) - FANCY
        "17021212121"   # Last 6: 121212 (alternating) - FANCY
    ]
    
    st.markdown("### Debug Test Results")
    for number in test_numbers:
        is_fancy, pattern = is_fancy_number(number)
        result = "FANCY" if is_fancy else "NOT FANCY"
        st.write(f"Number: {number} - Last 6: {number[-6:]} - {result} - Pattern: {pattern}")
