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
    last_three = clean_number[-3:]
    patterns = []
    
    # 6-digit patterns check
    if len(last_six) == 6:
        # All same digits
        if len(set(last_six)) == 1:
            patterns.append("6-digit repeating digits")
            
        # Consecutive sequence
        if all(int(last_six[i]) == int(last_six[i-1]) + 1 for i in range(1, 6)):
            patterns.append("6-digit ascending sequence")
        elif all(int(last_six[i]) == int(last_six[i-1]) - 1 for i in range(1, 6)):
            patterns.append("6-digit descending sequence")
            
        # Palindrome check
        if last_six == last_six[::-1]:
            patterns.append("6-digit palindrome")
    
    # 3-digit patterns check in last six digits
    if len(last_six) >= 6:
        first_three = last_six[:3]
        second_three = last_six[3:]
        
        # Double triplets
        if len(set(first_three)) == 1 and len(set(second_three)) == 1:
            patterns.append(f"Double triplets ({first_three}-{second_three})")
            
        # Related triplets (e.g., 121-122)
        if first_three[:-1] == second_three[:-1] and int(second_three[-1]) == int(first_three[-1]) + 1:
            patterns.append(f"Sequential triplets ({first_three}-{second_three})")
    
    # 2-digit patterns check
    pairs = [last_six[i:i+2] for i in range(0, len(last_six), 2)]
    if len(pairs) >= 3:
        # All pairs same
        if all(p == pairs[0] for p in pairs[:3]):
            patterns.append(f"Repeating pairs ({pairs[0]})")
            
        # Incremental pairs
        if all(int(pairs[i]) == int(pairs[i-1]) + 1 for i in range(1, 3)):
            patterns.append(f"Incremental pairs ({'→'.join(pairs[:3])})")
    
    # Last three digits check
    if len(last_three) == 3 and len(set(last_three)) == 1:
        patterns.append(f"Triplet ending ({last_three})")
    
    # Exceptional cases
    exceptional_patterns = {
        '000000': "Special zero pattern",
        '123456': "Classic ascending",
        '654321': "Classic descending",
        '100001': "Mirror pattern"
    }
    if last_six in exceptional_patterns:
        patterns.append(exceptional_patterns[last_six])
    
    if patterns:
        return True, ", ".join(patterns)
    else:
        return False, "No fancy pattern detected"

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
    ### Lycamobile Fancy Number Policy
    **Last 6-digit Analysis:**
    1. **6-digit Patterns**  
    - All identical digits (e.g., 666666)  
    - Consecutive sequences (123456 or 654321)  
    - Palindrome numbers (e.g., 123321)  
    - Special patterns (100001)
    
    2. **3-digit Patterns**  
    - Double triplets (444555)  
    - Sequential triplets (121122)  
    - Triplet ending (XXXXXX666)
    
    3. **2-digit Patterns**  
    - Repeating pairs (112233)  
    - Incremental pairs (111213)
    
    **Examples:**
    - ✅ Fancy Numbers:  
      13172611666 (triplet ending)  
      18147900900 (double triplets)  
      1702123456 (ascending sequence)
    
    - ❌ Normal Numbers:  
      16109055580 (no patterns)  
      12408692892 (random digits)  
      15015551234 (single triplet not in last three)
    """)

# Debug test cases
debug_mode = False
if debug_mode:
    test_numbers = [
        ("13172611666", True),  # Triplet ending
        ("16109055580", False), # No patterns
        ("18147900900", True),  # Double triplets
        ("1702123456", True),   # Ascending sequence
        ("15015551234", False)  # Triplet not in last three
    ]
    
    st.markdown("### Validation Tests")
    for number, expected in test_numbers:
        is_fancy, pattern = is_fancy_number(number)
        result = "PASS" if is_fancy == expected else "FAIL"
        color = "green" if result == "PASS" else "red"
        st.write(f"<span style='color:{color}'>{number}: {result} ({pattern})</span>", unsafe_allow_html=True)
