#!/usr/bin/env python3
"""
Replace all standalone 'VRS' with 'VRDX' across the entire Verdis codebase.
VRS is NOT a substring of VRDX (V-R-S vs V-R-D-X), so a simple replace is safe.
But we need to be careful not to replace VRS inside other words/identifiers.
"""

import os
import re
import json

BASE = "/opt/verdis/app/dist"
STATE_FILE = "/opt/verdis/blobs/verdis-state.json"

# Pattern: match 'VRS' as a standalone token (not part of a longer word)
# Use word boundary, but also handle cases like 'VRS' in strings, comments, etc.
# Since VRS is 3 chars and always uppercase, we can safely replace 'VRS' with 'VRDX'
# as long as we don't touch 'VRDX' itself (which doesn't contain 'VRS' anyway)
pattern = re.compile(r'\bVRS\b')

def replace_vrs(text):
    """Replace standalone VRS with VRDX, preserving VRDX instances."""
    # VRDX doesn't contain VRS, so simple replacement is safe
    return pattern.sub('VRDX', text)

# Files to patch
web_dir = os.path.join(BASE, "web")
api_dir = os.path.join(BASE, "api")
core_dir = os.path.join(BASE, "core")

total_replacements = 0
files_modified = []

# 1. Patch all web HTML files
for fname in os.listdir(web_dir):
    if not fname.endswith('.html'):
        continue
    fpath = os.path.join(web_dir, fname)
    with open(fpath, 'r', errors='replace') as f:
        content = f.read()
    
    count = len(pattern.findall(content))
    if count > 0:
        new_content = replace_vrs(content)
        with open(fpath, 'w') as f:
            f.write(new_content)
        files_modified.append(f"web/{fname}: {count} replacements")
        total_replacements += count

# 2. Patch API JS files
for fname in os.listdir(api_dir):
    if not fname.endswith('.js'):
        continue
    fpath = os.path.join(api_dir, fname)
    with open(fpath, 'r', errors='replace') as f:
        content = f.read()
    
    count = len(pattern.findall(content))
    if count > 0:
        new_content = replace_vrs(content)
        with open(fpath, 'w') as f:
            f.write(new_content)
        files_modified.append(f"api/{fname}: {count} replacements")
        total_replacements += count

# 3. Patch core JS files
for fname in os.listdir(core_dir):
    if not fname.endswith('.js'):
        continue
    fpath = os.path.join(core_dir, fname)
    with open(fpath, 'r', errors='replace') as f:
        content = f.read()
    
    count = len(pattern.findall(content))
    if count > 0:
        new_content = replace_vrs(content)
        with open(fpath, 'w') as f:
            f.write(new_content)
        files_modified.append(f"core/{fname}: {count} replacements")
        total_replacements += count

# 4. Patch the state file — update DEX pool token names
with open(STATE_FILE, 'r') as f:
    state = json.load(f)

state_replacements = 0
state_str = json.dumps(state)
state_count = len(pattern.findall(state_str))
if state_count > 0:
    # Do replacement on the JSON string and parse back
    new_state_str = pattern.sub('VRDX', state_str)
    new_state = json.loads(new_state_str)
    with open(STATE_FILE, 'w') as f:
        json.dump(new_state, f)
    files_modified.append(f"state file: {state_count} replacements")
    total_replacements += state_count

# 5. Also check for VRS in the market tracker / other sub-directories
for root, dirs, files in os.walk(BASE):
    # Skip already processed dirs
    if '/web' in root or '/api' in root or '/core' in root:
        continue
    for fname in files:
        if not fname.endswith('.js'):
            continue
        fpath = os.path.join(root, fname)
        with open(fpath, 'r', errors='replace') as f:
            content = f.read()
        count = len(pattern.findall(content))
        if count > 0:
            new_content = replace_vrs(content)
            with open(fpath, 'w') as f:
                f.write(new_content)
            rel_path = fpath.replace(BASE + '/', '')
            files_modified.append(f"{rel_path}: {count} replacements")
            total_replacements += count

print(f"\nTotal replacements: {total_replacements}")
print(f"Files modified: {len(files_modified)}")
for f in files_modified:
    print(f"  ✅ {f}")
