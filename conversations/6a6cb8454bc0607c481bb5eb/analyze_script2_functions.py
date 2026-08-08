with open("page2_script.js", "r") as f:
    code = f.read()

# Let's print the entire JS code nicely formatted or search for functions
import re
print("JS Functions found:")
funcs = re.findall(r'function\s+\w+\s*\([^)]*\)', code)
for fn in funcs:
    print(" ", fn)

