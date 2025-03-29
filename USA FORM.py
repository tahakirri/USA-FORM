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
    
    # 1. Check for sequences of 3+ identical digits (but only consider 4+ as fancy)
    for i in range(len(last_six) - 2):
        if last_six[i] == last_six[i+1] == last_six[i+2]:
            # Check how long this sequence continues
            j = i + 3
            while j < len(last_six) and last_six[j] == last_six[i]:
                j += 1
            seq_length = j - i
            if seq_length >= 4:  # Only consider sequences of 4+ identical digits as fancy
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
               ("Repeated 3-digit" in pattern and len(set(pattern.split()[3][:3])) == 1):
                significant_patterns.append(pattern)
        
        if significant_patterns:
            return True, ", ".join(significant_patterns)
    
    return False, "No fancy pattern detected"
