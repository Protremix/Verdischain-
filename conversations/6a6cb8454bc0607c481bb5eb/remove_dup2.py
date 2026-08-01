#!/usr/bin/env python3
"""Remove duplicate loadSectionData functions (multi-line with nested braces)"""

with open("/opt/verdis/app/dist/web/dashboard.html") as f:
    lines = f.readlines()

result = []
i = 0
removed = 0
while i < len(lines):
    line = lines[i]
    if "function loadSectionData" in line:
        # Skip this entire function block - count braces
        depth = 0
        j = i
        while j < len(lines):
            depth += lines[j].count("{") - lines[j].count("}")
            if depth <= 0 and j > i:
                j += 1  # past closing brace
                break
            j += 1
        # Also skip trailing </script> if present
        while j < len(lines) and lines[j].strip() in ("</script>", ""):
            j += 1
        removed += (j - i)
        i = j
    else:
        result.append(lines[i])
        i += 1

with open("/opt/verdis/app/dist/web/dashboard.html", "w") as f:
    f.writelines(result)
print(f"Removed {removed} lines ({2 if removed > 0 else 0} duplicate loadSectionData functions)")
