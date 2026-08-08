#!/usr/bin/env python3
"""Deep audit pass 2 - color consistency, meta tags, hardcoded values."""
import re, glob

issues = []

# Check for inconsistent color references
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    if "#00ff88" in content and rel not in ["/index.html", "/_not-found/", "/404/", "/token-sale/"]:
        count = content.count("#00ff88")
        issues.append(f"{rel}: OLD GREEN #00ff88 used {count}x (should be #caff33)")

# Check for missing meta descriptions
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    if 'name="description"' not in content and rel not in ["/404/", "/_not-found/", "/token-sale/"]:
        issues.append(f"{rel}: MISSING meta description")

# Check for missing OG tags
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    if 'og:title' not in content and rel not in ["/404/", "/_not-found/", "/token-sale/"]:
        issues.append(f"{rel}: MISSING og:title tag")

# Check for hardcoded block heights in static HTML
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    blocks = re.findall(r"Block\s*#(\d{2,})", content)
    for b in blocks:
        if int(b) > 1:
            issues.append(f"{rel}: HARDCODED block height: Block #{b}")

# Check for "coming soon" text
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    for phrase in ["coming soon", "under construction", "not yet available"]:
        if phrase in content.lower():
            idx = content.lower().index(phrase)
            ctx = content[max(0,idx-40):idx+len(phrase)+40].replace("\n"," ")
            issues.append(f"{rel}: COMING SOON: ...{ctx}...")

# Check for inconsistent token supply references
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    if "1 billion" in content.lower() and "100" not in content.lower():
        issues.append(f"{rel}: References 1 billion supply (should be 100B)")

# Check for inconsistent VRDX vs VRD ticker
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    # Look for VRD without X (but not in words like "Verdis" or "VRDX")
    vrd_refs = re.findall(r'\bVRD\b(?!X)', content)
    if vrd_refs:
        issues.append(f"{rel}: WRONG TICKER VRD (should be VRDX): {len(vrd_refs)} occurrences")

# Print
if issues:
    print(f"FOUND {len(set(issues))} ISSUES:")
    for issue in sorted(set(issues)):
        print(f"  - {issue}")
else:
    print("No additional issues found")
