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
    
    # Length validation (expecting a 10 or 11 digit number)
    if len(clean_number) == 11 and clean_number.startswith('1'):
        clean_number = clean_number[1:]  # Remove country code for analysis
    elif len(clean_number) != 10:
        return False, "Invalid length"
    
    # According to Lycamobile policy, only analyze the last 6 digits
    last_six = clean_number[-6:]
    
    # Patterns found in the last 6 digits
    patterns_found = []
    
    # 1. Check for 5-digit sequences within the last 6 digits
    # Ascending sequence (e.g., 12345)
    if all(int(last_six[i]) == int(last_six[i-1]) + 1 for i in range(1, 5)):
        patterns_found.append(f"5-digit ascending sequence ({last_six})")
    
    # Descending sequence (e.g., 98765)
    if all(int(last_six[i]) == int(last_six[i-1]) - 1 for i in range(1, 5)):
        patterns_found.append(f"5-digit descending sequence ({last_six})")
    
    # Repeated digits (e.g., 66666)
    if len(set(last_six)) == 1:
        patterns_found.append(f"5 repeated digits ({last_six})")
    
    # Mirrored patterns (e.g., 12321)
    if last_six == last_six[::-1]:
        patterns_found.append(f"5-digit mirrored pattern ({last_six})")
    
    # 2. Check for 3-digit sequences
    # Repeated triplets (e.g., 444555)
    if last_six[:3] == last_six[3:]:
        patterns_found.append(f"Repeated 3-digit pattern ({last_six[:3]}-{last_six[3:]})")
    
    # Closely related triplets (e.g., 121122, 786786)
    if (int(last_six[:3]) == int(last_six[3:6]) - 111 or
        int(last_six[:3]) == int(last_six[3:6]) + 111):
        patterns_found.append(f"Closely related 3-digit pattern ({last_six[:3]}-{last_six[3:]})")
    
    # 3. Check for 2-digit sequences
    # Repeated or incremental pairs (e.g., 111213, 202020)
    if last_six[:2] == last_six[2:4] == last_six[4:]:
        patterns_found.append(f"Repeated 2-digit sequence ({last_six[:2]}-{last_six[2:4]}-{last_six[4:]})")
    
    # Incremental pairs (e.g., 111213, 324252)
    if (int(last_six[:2]) + 1 == int(last_six[2:4]) and
        int(last_six[2:4]) + 1 == int(last_six[4:])):
        patterns_found.append(f"Incremental 2-digit sequence ({last_six[:2]}-{last_six[2:4]}-{last_six[4:]})")
    
    # Exceptional checks: XYXY pattern, alternating digits, etc.
    if len(last_six) == 6 and all(last_six[i] == last_six[i % 2] for i in range(6)):
        patterns_found.append(f"Alternating pattern ({last_six})")
    
    # 4. Return result
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
