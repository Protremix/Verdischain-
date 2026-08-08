import subprocess, re

# Read the remote file
result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/explorer/index.html"],
    capture_output=True, text=True
)
content = result.stdout

# Fix the validatorName handling - convert byte arrays to strings
old_code = """      try { const n = await rpc('dpos_validatorName', [addr]); if (n) name = n; } catch(e) {}"""
new_code = """      try { const n = await rpc('dpos_validatorName', [addr]); if (n) { name = Array.isArray(n) ? String.fromCharCode.apply(null, n) : n; } } catch(e) {}"""

if old_code in content:
    content = content.replace(old_code, new_code)
    print("Fixed validatorName byte array conversion")
else:
    print("WARNING: old_code not found, trying alternative")
    # Try finding it with different whitespace
    if "dpos_validatorName" in content:
        # Find the line and replace it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "dpos_validatorName" in line and "Array.isArray" not in line:
                lines[i] = "      try { const n = await rpc('dpos_validatorName', [addr]); if (n) { name = Array.isArray(n) ? String.fromCharCode.apply(null, n) : n; } } catch(e) {}"
                print(f"Fixed line {i+1}")
                break
        content = '\n'.join(lines)

# Also fix the green score display - the green emoji might be causing encoding issues
old_green = "&#127807;"
new_green = ""
content = content.replace(old_green, new_green)

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /var/www/verdiscan/explorer/index.html"],
    input=content,
    capture_output=True,
    text=True
)
print("Fix applied. Exit:", proc.returncode)
