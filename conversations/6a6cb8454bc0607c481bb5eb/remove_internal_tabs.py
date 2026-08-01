#!/usr/bin/env python3
"""Remove internal/developer-only tabs from the user-facing dashboard"""

with open('/opt/verdis/app/dist/web/dashboard.html') as f:
    html = f.read()

import re

# Tabs to remove and their section IDs
REMOVE_TABS = ['monitoring', 'aiagents', 'fraud', 'parallel', 'zk', 'aa']

changes = 0

# 1. Remove nav-tab buttons
for tab in REMOVE_TABS:
    pattern = f'<div class="nav-tab" data-tab="{tab}">.*?</div>'
    match = re.search(pattern, html)
    if match:
        html = html.replace(match.group(), '', 1)
        print(f"  Removed tab button: {tab}")
        changes += 1
    else:
        print(f"  Tab button not found: {tab}")

# 2. Remove section divs (from <div id="section-XXX" to the closing </div> that ends the section)
# We need to find the section blocks carefully
for tab in REMOVE_TABS:
    # Find the section start
    section_start = html.find(f'id="section-{tab}"')
    if section_start == -1:
        print(f"  Section not found: {tab}")
        continue
    
    # Find the opening div tag that contains this id
    div_start = html.rfind('<div', 0, section_start)
    
    # Find the matching closing div by counting depth
    depth = 0
    pos = div_start
    while pos < len(html):
        if html[pos:pos+5] == '<div ' or html[pos:pos+4] == '<div>':
            depth += 1
        elif html[pos:pos+6] == '</div>':
            depth -= 1
            if depth == 0:
                # Found the closing div
                end_pos = pos + 6
                # Also remove any trailing whitespace/newline
                while end_pos < len(html) and html[end_pos] in '\n\r ':
                    end_pos += 1
                removed = html[div_start:end_pos]
                html = html[:div_start] + html[end_pos:]
                print(f"  Removed section: {tab} ({len(removed)} chars)")
                changes += 1
                break
        pos += 1

# 3. Remove loadTabData references for removed tabs
for tab in REMOVE_TABS:
    # Pattern: if(t==='xxx'){...return;} or if(t==='xxx')loadXXX();
    patterns = [
        rf"if\(t==='{tab}'\)\{{[^}}]*\}}[^;]*;",
        rf"if\(t==='zk'\)\{{loadZKStats\(\);return;\}}",
        rf"if\(t==='parallel'\)\{{loadParallelStats\(\);return;\}}",
        rf"if \(t === '{tab}'\) load\w+\(\);",
    ]
    for pat in patterns:
        matches = re.findall(pat, html)
        for m in matches:
            html = html.replace(m, '', 1)
            print(f"  Removed loadTabData ref: {tab}")
            changes += 1

# 4. Clean up the loadTabData switch cases for removed tabs
for tab in REMOVE_TABS:
    # Remove case 'xxx':loadXXX();break;
    pat = rf"case'{tab}':load\w+\(\);break;"
    matches = re.findall(pat, html)
    for m in matches:
        html = html.replace(m, '', 1)
        print(f"  Removed switch case: {tab}")
        changes += 1

print(f"\nTotal changes: {changes}")

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.write(html)
print("Dashboard cleaned!")
