import re

with open("/tmp/dash_orig.html", "r") as f:
    orig = f.read()

with open("/opt/verdis/app/dist/web/dashboard.html", "r") as f:
    curr = f.read()

# Find the sale JS section in the original by looking for saleStats
ss_idx = orig.find("let saleStats")
# Find the line start
line_start = orig.rfind("\n", 0, ss_idx) + 1

# Find the end (MONITORING after saleStats)
mon_idx = orig.find("// MONITORING", ss_idx)

sale_block = orig[line_start:mon_idx]

# Count braces using a proper tokenizer
def count_braces(code):
    depth = 0
    i = 0
    in_string = False
    string_char = None
    in_template = False
    in_line_comment = False
    in_block_comment = False
    
    while i < len(code):
        c = code[i]
        c_next = code[i+1] if i+1 < len(code) else ''
        
        if in_line_comment:
            if c == '\n':
                in_line_comment = False
            i += 1
            continue
        if in_block_comment:
            if c == '*' and c_next == '/':
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue
        if in_string:
            if c == '\\':
                i += 2
                continue
            if c == string_char:
                in_string = False
            i += 1
            continue
        if in_template:
            if c == '\\':
                i += 2
                continue
            if c == '`':
                in_template = False
            i += 1
            continue
        
        if c == '/' and c_next == '/':
            in_line_comment = True
            i += 2
            continue
        if c == '/' and c_next == '*':
            in_block_comment = True
            i += 2
            continue
        if c == "'" or c == '"':
            in_string = True
            string_char = c
            i += 1
            continue
        if c == '`':
            in_template = True
            i += 1
            continue
        
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        i += 1
    
    return depth

sale_depth = count_braces(sale_block)
print(f"Sale JS block brace depth: {sale_depth} (should be 0 if self-contained)")
print(f"Block starts at char {line_start}, ends at char {mon_idx}")
print(f"Block size: {len(sale_block)} chars, {sale_block.count(chr(10))} lines")

# Show first and last 3 lines
lines = sale_block.strip().split("\n")
print(f"\nFirst 3 lines:")
for l in lines[:3]:
    print(f"  {l[:120]}")
print(f"\nLast 3 lines:")
for l in lines[-3:]:
    print(f"  {l[:120]}")

# Now check the full original
orig_depth = count_braces(orig)
print(f"\nOriginal full HTML brace depth: {orig_depth}")

# Check just the script sections
# Find the last <script> before saleStats
script_start = orig.rfind("<script", 0, ss_idx)
# Find the </script> after MONITORING
script_end = orig.find("</script>", mon_idx)
main_script = orig[script_start:script_end]
main_depth = count_braces(main_script)
print(f"Main script block depth: {main_depth}")

# Check current version
curr_depth = count_braces(curr)
print(f"Current full HTML brace depth: {curr_depth}")
