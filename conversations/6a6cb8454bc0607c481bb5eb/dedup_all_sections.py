#!/usr/bin/env python3
"""Remove all duplicate section divs — keep only the last occurrence of each"""

with open('/opt/verdis/app/dist/web/dashboard.html', 'r') as f:
    lines = f.readlines()

def find_section_end(lines, start_idx):
    depth = 0
    for i in range(start_idx, len(lines)):
        depth += lines[i].count('<div')
        depth -= lines[i].count('</div>')
        if depth <= 0:
            return i + 1
    return len(lines)

sections_to_dedup = ['section-aiagents', 'section-nameservice', 'section-fraud', 'section-aa', 'section-tokenomics']

for section_name in sections_to_dedup:
    indices = [i for i, l in enumerate(lines) if f'id="{section_name}"' in l or f'id="{section_name}" class' in l]
    print(f"{section_name}: found at lines {[i+1 for i in indices]}")
    
    if len(indices) > 1:
        # Keep the last one, remove all others (process from bottom to top of the ones to remove)
        for idx in reversed(indices[:-1]):
            end = find_section_end(lines, idx)
            removed = lines[idx:end]
            print(f"  Removing lines {idx+1}-{end} ({end-idx} lines)")
            del lines[idx:end]

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.writelines(lines)

# Final verification
for s in sections_to_dedup + ['section-governance']:
    count = sum(1 for l in lines if s in l and 'section' in l)
    print(f"  {s}: {count} occurrence(s)")
print("Dedup complete!")
