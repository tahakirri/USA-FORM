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
    /* [Previous CSS styles remain exactly the same] */
</style>
""", unsafe_allow_html=True)

# Fancy Number Checker App
st.header("🔢 Fancy Number Checker")

def is_fancy_number(phone_number):
    clean_number = re.sub(r'[^\d]', '', phone_number)
    
    # Validate length
    if len(clean_number) == 11 and clean_number.startswith('1'):
        clean_number = clean_number[1:]  # Remove country code
    elif len(clean_number) != 10:
        return False, "Invalid length (must be 10 digits or 11 digits starting with 1)"

    # 1. Check exceptional cases from image
    exceptional_cases = [
        '7900000123', '7900007555', 
        '7898789555', '7999004455'
    ]
    for case in exceptional_cases:
        if case in clean_number:
            return True, "Exceptional case match"

    # 2. Check 6-digit sequences from image
    six_digit_patterns = [
        '121456', '987654', '666666', '100001'
    ]
    for pattern in six_digit_patterns:
        if pattern in clean_number:
            return True, f"6-digit sequence ({pattern})"

    # 3. Check 3-digit pairs from image
    three_digit_pairs = [
        ('441', '555'), ('121', '126'), 
        ('786', '786'), ('457', '456')
    ]
    for i in range(len(clean_number)-5):
        chunk = clean_number[i:i+6]
        for pair in three_digit_pairs:
            if chunk[:3] == pair[0] and chunk[3:] == pair[1]:
                return True, f"3-digit pair ({pair[0]} {pair[1]})"

    # 4. Check 2-digit sequences from image
    two_digit_groups = [
        ('11', '12', '13'), ('20', '20', '20'),
        ('01', '01', '01'), ('32', '42', '52')
    ]
    for i in range(len(clean_number)-5):
        chunk = clean_number[i:i+6]
        for group in two_digit_groups:
            if (chunk[:2] == group[0] and 
                chunk[2:4] == group[1] and 
                chunk[4:6] == group[2]):
                return True, f"2-digit sequence ({' '.join(group)})"

    # 5. Check for 5+ repeating digits
    if re.search(r'(\d)\1{4,}', clean_number):
        return True, "5+ repeating digits"

    # 6. Check for repeating last 6 digits (ABCABC pattern)
    if len(clean_number) >= 6:
        last_six = clean_number[-6:]
        if last_six[:3] == last_six[3:]:
            return True, f"Repeating 3-digit ending ({last_six[:3]} {last_six[3:]})"

    # 7. Check for mirror pattern
    if len(clean_number) == 10:
        first_half = clean_number[:5]
        second_half = clean_number[5:]
        if first_half == second_half[::-1]:
            return True, "Mirror pattern"

    return False, "No fancy pattern detected"

# User Interface
phone_input = st.text_input("📱 Enter Phone Number (10 or 11 digits)", 
                          placeholder="e.g., 16788999999 or 13172611666")

if st.button("🔍 Check if Fancy") and phone_input:
    is_fancy, pattern = is_fancy_number(phone_input)
    clean_number = re.sub(r'[^\d]', '', phone_input)
    
    # Format display
    formatted_num = (f"{clean_number[:3]}-{clean_number[3:6]}-{clean_number[6:]}" 
                    if len(clean_number) == 10 else 
                    f"{clean_number[0]}-{clean_number[1:4]}-{clean_number[4:7]}-{clean_number[7:]}")
    
    if is_fancy:
        st.markdown(f"""
        <div class="fancy-result">
            <h3><span class="fancy-number">✨ {formatted_num} ✨</span></h3>
            <p>This is a <strong>FANCY</strong> phone number!</p>
            <p><strong>Pattern:</strong> {pattern}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="normal-result">
            <h3><span class="normal-number">{formatted_num}</span></h3>
            <p>This is a normal phone number</p>
            <p><strong>Analysis:</strong> {pattern}</p>
        </div>
        """, unsafe_allow_html=True)
        
