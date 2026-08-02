import re

with open("/opt/verdis/app/dist/web/dashboard.html", "r") as f:
    content = f.read()

scripts = re.findall(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
main_script = scripts[1]
lines = main_script.split("\n")

# Track brace depth and show significant depth changes
depth = 0
prev_depth = 0

for i, line in enumerate(lines):
    # Remove strings and comments
    cleaned = re.sub(r"'[^']*'", "", line)
    cleaned = re.sub(r'"[^"]*"', "", cleaned)
    cleaned = re.sub(r'`[^`]*`', "", cleaned)
    cleaned = re.sub(r'//.*$', '', cleaned)
    
    opens = cleaned.count("{")
    closes = cleaned.count("}")
    depth += opens - closes
    
    # Show lines where depth changes significantly or around known areas
    if depth != prev_depth and (depth <= 1 or prev_depth <= 1):
        print(f"Line {i+1}: depth {prev_depth}->{depth} - {line[:100]}")
    
    prev_depth = depth
