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
    
    # Validate length and format
    if len(clean_number) == 11 and clean_number.startswith('1'):
        clean_number = clean_number[1:]  # Remove US country code
    elif len(clean_number) != 10:
        return False, "Invalid number length"
    
    last_six = clean_number[-6:]  # Focus on last 6 digits
    patterns_found = []

    # 1. Check for 4+ consecutive identical digits
    for i in range(len(last_six) - 3):
        if last_six[i] == last_six[i+1] == last_six[i+2] == last_six[i+3]:
            # Track full sequence length
            j = i + 4
            while j < len(last_six) and last_six[j] == last_six[i]:
                j += 1
            seq_length = j - i
            patterns_found.append(f"{seq_length} consecutive {last_six[i]}s")

    # 2. Check special 6-digit patterns
    # All identical digits
    if len(set(last_six)) == 1:
        patterns_found.append("6 identical digits")
    
    # Perfect mirror
    if last_six == last_six[::-1]:
        patterns_found.append("perfect mirror")
    
    # 3. Check 5-digit sequences
    for i in [0, 1]:
        segment = last_six[i:i+5]
        # Ascending
        if segment in "0123456789":
            patterns_found.append("5-digit ascending")
        # Descending
        if segment in "9876543210":
            patterns_found.append("5-digit descending")

    # 4. Check 3-digit patterns
    # Repeated triplets (e.g., 123123)
    if len(last_six) == 6 and last_six[:3] == last_six[3:]:
        patterns_found.append("repeated triplets")
    
    # Double triplets (e.g., 111222)
    if len(set(last_six[:3])) == 1 and len(set(last_six[3:])) == 1:
        patterns_found.append("double triplets")

    # 5. Filter significant patterns
    significant_patterns = []
    for pattern in patterns_found:
        if any(keyword in pattern for keyword in [
            "4 consecutive", "5-digit", "6 identical",
            "perfect mirror", "repeated triplets", "double triplets"
        ]):
            significant_patterns.append(pattern)

    return bool(significant_patterns), " | ".join(significant_patterns) if significant_patterns else "No fancy pattern"

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

            # Highlight last six digits
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
    - 4+ consecutive identical digits (e.g., 116666, 5555)
    - 5-digit sequences (ascending/descending)
    - Perfect mirrored numbers (e.g., 123321)
    - Repeated 3-digit blocks (e.g., 123123)
    - Double triplets (e.g., 111222)
    - 6 identical digits
    
    #### Weak Patterns (Don't Qualify):
    - Isolated triplets (e.g., 555 in 555123)
    - Short sequences without 4+ repetition
    - Simple repeating pairs (e.g., 1212)
    
    #### Examples:
    - ✅ 116666 (4+ repeats)
    - ✅ 123456 (ascending)
    - ✅ 111222 (double triplet)
    - ❌ 555123 (isolated triplet)
    - ❌ 121212 (only pairs)
    """)

# Debug testing
if st.checkbox("Show debug examples"):
    test_numbers = [
        ("13172611666", True),   # Last 6: 116666 (4+ repeats)
        ("16109055580", False),  # Last 6: 555580 (only 4 repeats)
        ("1234567890", True),    # Last 6: 456789 (ascending)
        ("18005555555", True),   # Last 6: 555555 (6 repeats)
        ("17021212121", False)   # Last 6: 121212 (only pairs)
    ]
    
    st.markdown("### Validation Tests")
    for number, expected in test_numbers:
        is_fancy, pattern = is_fancy_number(number)
        status = "PASS ✅" if is_fancy == expected else "FAIL ❌"
        st.write(f"{status} {number}: {pattern}")
