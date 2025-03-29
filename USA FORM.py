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
    
    # 1. Check for 5-digit sequences within the last 6 digits
    # Only consider if they are in the first or last 5 digits of the 6-digit segment
    for i in [0, 1]:  # Only check first and second positions in 6-digit segment
        segment = last_six[i:i+5]
        
        # Ascending sequence (e.g., 12345)
        if segment in "0123456789":
            patterns_found.append(f"5-digit ascending sequence ({segment})")
        
        # Descending sequence (e.g., 98765)
        if segment in "9876543210":
            patterns_found.append(f"5-digit descending sequence ({segment})")
        
        # Repeated digits (e.g., 66666)
        if len(set(segment)) == 1:
            patterns_found.append(f"5 repeated digits ({segment})")
        
        # Mirrored patterns (e.g., 12321)
        if segment == segment[::-1]:
            patterns_found.append(f"Mirrored 5-digit pattern ({segment})")
    
    # 2. Check for 3-digit sequences
    # Only consider if they are significant patterns (not just any triplet)
    # Repeated triplets (e.g., 123123)
    if len(last_six) == 6:
        first_three = last_six[:3]
        second_three = last_six[3:]
        if first_three == second_three:
            patterns_found.append(f"Repeated 3-digit pattern ({first_three}-{second_three})")
        
        # Check for mirrored triplets (e.g., 123321)
        if last_six == last_six[::-1]:
            patterns_found.append(f"Perfect mirrored pattern ({last_six})")
    
    # 3. Check for 4-digit sequences
    for i in range(3):  # Check all possible 4-digit segments in last 6 digits
        segment = last_six[i:i+4]
        
        # All same digit (e.g., 4444)
        if len(set(segment)) == 1:
            patterns_found.append(f"4 repeated digits ({segment})")
        
        # XYXY pattern (e.g., 1212)
        if segment[:2] == segment[2:4] and segment[0] != segment[1]:
            patterns_found.append(f"XYXY pattern ({segment})")
    
    # 4. Check for special 6-digit patterns
    # All same digit (e.g., 666666)
    if len(set(last_six)) == 1:
        patterns_found.append(f"6 repeated digits ({last_six})")
    
    # Alternating pattern (e.g., 121212)
    if all(last_six[i] == last_six[i%2] for i in range(6)):
        patterns_found.append(f"Perfect alternating pattern ({last_six})")
    
    # 5. Check for double triplets (e.g., 111222, 333444)
    if len(last_six) == 6:
        first_triplet = last_six[:3]
        second_triplet = last_six[3:]
        if len(set(first_triplet)) == 1 and len(set(second_triplet)) == 1 and first_triplet[0] != second_triplet[0]:
            patterns_found.append(f"Double triplets ({first_triplet}-{second_triplet})")
    
    # 6. Check for sequential triplets (e.g., 123123)
    if len(last_six) == 6:
        first_triplet = last_six[:3]
        second_triplet = last_six[3:]
        if (first_triplet in "0123456789" or first_triplet in "9876543210") and first_triplet == second_triplet:
            patterns_found.append(f"Sequential repeated triplets ({first_triplet}-{second_triplet})")
    
    # 7. Check for 3+3 mirrored (e.g., 123321)
    if len(last_six) == 6:
        if last_six[:3] == last_six[3:][::-1]:
            patterns_found.append(f"Mirrored triplets ({last_six[:3]}-{last_six[3:]})")
    
    # Return result based on patterns found
    if patterns_found:
        # Filter out weak patterns that shouldn't qualify as fancy
        strong_patterns = [p for p in patterns_found if 
                          not ("3 repeated digits" in p) and  # Exclude simple triplets
                          not ("XYXY pattern" in p and len(p.split()[2]) < 4)]  # Exclude short XYXY
        
        if strong_patterns:
            return True, ", ".join(strong_patterns)
    
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
    - 5+ digit sequences (ascending/descending/repeated)
    - Repeated 3-digit blocks (e.g., 123123)
    - Perfect mirrors (e.g., 123321)
    - 4+ repeated digits (e.g., 4444, 55555)
    - Double triplets (e.g., 111222)
    - Perfect alternating patterns (e.g., 121212)
    
    #### Weak Patterns (Don't Qualify):
    - Simple triplets (e.g., 555)
    - Short XY patterns (e.g., 1212 in a longer sequence)
    - Isolated repeating digits
    
    #### Examples of Fancy Numbers:
    - 123456 (ascending)
    - 654321 (descending)
    - 111222 (double triplet)
    - 123123 (repeated block)
    - 123321 (mirrored)
    - 121212 (alternating)
    """)

# Optional: Debug testing for specific numbers
debug_mode = False
if debug_mode:
    test_numbers = [
        "16109055580",  # Should NOT be fancy (has 555 but not significant enough)
        "12408692892",  # Should NOT be fancy
        "12345678901",  # Last 6 = 678901 (ascending)
        "15853123123",  # Last 6 = 123123 (repeating block)
        "14085555555",  # Last 6 = 555555 (all same digit)
        "17025252525"   # Last 6 = 525252 (alternating)
    ]
    
    st.markdown("### Debug Testing")
    for number in test_numbers:
        is_fancy, pattern = is_fancy_number(number)
        st.write(f"Number: {number} - Fancy: {is_fancy} - Pattern: {pattern}")
