#!/usr/bin/env python3
"""Remove duplicate governance sections — keep only the newest one (line ~3462)"""

with open('/opt/verdis/app/dist/web/dashboard.html', 'r') as f:
    lines = f.readlines()

# Find all section-governance line indices (0-based)
gov_lines = [i for i, l in enumerate(lines) if 'section-governance' in l]
print(f"Found governance sections at lines: {[l+1 for l in gov_lines]}")

# We want to keep the LAST one (line 3462, index ~3461) which is our new injected one
# Remove the first two (old ones at lines 1288 and 2668)

# Remove section 2 (line 2668, index 2667) first, then section 1 (line 1288, index 1287)
# We need to find the end of each section — look for the closing </div> that matches

def find_section_end(lines, start_idx):
    """Find the matching closing </div> for the section opening at start_idx"""
    depth = 0
    for i in range(start_idx, len(lines)):
        depth += lines[i].count('<div')
        depth -= lines[i].count('</div>')
        if depth <= 0:
            return i + 1  # Include the closing tag
    return len(lines)

# Remove section at line 2668 (index 2667) first (process from bottom to top to keep indices valid)
for section_line in reversed(gov_lines[:-1]):  # Skip the last one (our new section)
    end = find_section_end(lines, section_line)
    removed = lines[section_line:end]
    print(f"Removing lines {section_line+1}-{end}: {removed[0].strip()[:60]}...{removed[-1].strip()[:60]}")
    del lines[section_line:end]

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.writelines(lines)

# Verify
gov_count = sum(1 for l in lines if 'section-governance' in l)
print(f"Remaining governance sections: {gov_count}")
