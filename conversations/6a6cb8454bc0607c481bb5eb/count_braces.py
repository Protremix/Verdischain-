import re

with open("/tmp/dash_orig.html", "r") as f:
    orig = f.read()

# Extract the main script from the original
orig_scripts = re.findall(r"<script[^>]*>(.*?)</script>", orig, re.DOTALL)
orig_main = orig_scripts[1]

# Find the TOKEN SALE section
ts_start = orig_main.find("// TOKEN SALE")
mon_start = orig_main.find("// MONITORING")

if ts_start >= 0 and mon_start >= 0:
    sale_block = orig_main[ts_start:mon_start]
    
    # Count braces precisely, handling strings
    depth = 0
    in_string = False
    string_char = None
    in_template = False
    in_comment = False
    
    for char in sale_block:
        if in_comment:
            if char == '\n':
                in_comment = False
            continue
        if in_string:
            if char == string_char:
                in_string = False
            continue
        if in_template:
            if char == '`':
                in_template = False
            continue
        
        if char == '/' and sale_block[sale_block.index(char):sale_block.index(char)+2] == '//':
            in_comment = True
            continue
        if char == "'" or char == '"':
            in_string = True
            string_char = char
            continue
        if char == '`':
            in_template = True
            continue
        
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
    
    print(f"Sale JS block brace depth: {depth} (should be 0)")
    print(f"Block size: {len(sale_block)} chars")
    
    # Also check the entire original script
    depth = 0
    in_string = False
    string_char = None
    in_template = False
    in_comment = False
    
    for char in orig_main:
        if in_comment:
            if char == '\n':
                in_comment = False
            continue
        if in_string:
            if char == string_char:
                in_string = False
            continue
        if in_template:
            if char == '`':
                in_template = False
            continue
        
        if char == "'":
            in_string = True
            string_char = "'"
            continue
        if char == '"':
            in_string = True
            string_char = '"'
            continue
        if char == '`':
            in_template = True
            continue
        
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
    
    print(f"Original full script brace depth: {depth} (should be 0)")
else:
    print(f"TOKEN SALE: {ts_start}, MONITORING: {mon_start}")
