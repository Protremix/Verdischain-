import re
import sys

with open("/opt/verdis/app/dist/web/dashboard.html", "r") as f:
    content = f.read()

scripts = re.findall(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
main_script = scripts[1]
lines = main_script.split("\n")

# Track brace depth, ignoring strings and comments
depth = 0
min_depth = 999
min_depth_line = 0

for i, line in enumerate(lines):
    # Remove single-quoted strings
    cleaned = re.sub(r"'[^']*'", "", line)
    # Remove double-quoted strings
    cleaned = re.sub(r'"[^"]*"', "", cleaned)
    # Remove template literals (simple)
    cleaned = re.sub(r'`[^`]*`', "", cleaned)
    # Remove line comments
    cleaned = re.sub(r'//.*$', '', cleaned)
    
    opens = cleaned.count("{")
    closes = cleaned.count("}")
    depth += opens - closes
    
    if depth < min_depth:
        min_depth = depth
        min_depth_line = i + 1
    
    # Show the last 30 lines before the end
    if i >= len(lines) - 30:
        print(f"Line {i+1}: depth={depth} - {line[:80]}")

print(f"\nFinal depth: {depth}")
print(f"Minimum depth: {min_depth} at line {min_depth_line}")
