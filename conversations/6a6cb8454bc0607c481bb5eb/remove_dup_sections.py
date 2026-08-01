#!/usr/bin/env python3
"""Remove duplicate loadSectionData functions"""
import re

with open("/opt/verdis/app/dist/web/dashboard.html") as f:
    html = f.read()

# Remove loadSectionData function blocks
pattern = r"function loadSectionData\(sectionId\)\s*\{[^}]*\}\s*</script>"
matches = list(re.finditer(pattern, html))
print(f"Found {len(matches)} loadSectionData blocks")

for m in matches:
    print(f"  At index {m.start()}: {repr(m.group()[:80])}...")

# Remove them all
html = re.sub(pattern, "", html)
print(f"Removed {len(matches)} blocks")

with open("/opt/verdis/app/dist/web/dashboard.html", "w") as f:
    f.write(html)
print("Done")
