#!/usr/bin/env python3
"""Deep audit - check for remaining stale pricing, fake data, and text issues."""
import re, glob

issues = []

# Check all pages for stale IDO pricing
stale_prices = [
    ("$0.005 / VRDX", "old seed price"),
    ("$0.010 / VRDX", "old private price (in IDO context)"),
    ("$0.025 / VRDX", "old presale price"),
    ("$0.05 / VRDX", "old public price"),
    ("$300M", "old hard cap"),
    ("$250M", "old hard cap"),
    ("$36M", "old private hard cap"),
    ("$100M", "old presale/public hard cap"),
    ("$120M", "old public hard cap"),
    ("$150M", "old presale hard cap"),
    ("$12M", "old seed hard cap"),
    ("3 IDO", "old 3 phases"),
    ("Phase 1.*Private", "Phase 1 should be Seed"),
]

# Check all pages for stale allocation values
stale_allocs = [
    ("2.4B VRDX", "old seed alloc (now 3B)"),
    ("3.6B VRDX", "old private alloc (now 3B)"),
    ("6.0B VRDX", "old presale alloc (now 4B)"),
    ("6B VRDX", "old presale alloc (now 4B)"),
    ("2.0B VRDX", "old public alloc (now 2B)"),
]

for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    
    # Skip /sale/ and /tokenomics/ for stale price checks (already fixed)
    # But still check other pages
    if rel not in ["/sale/", "/tokenomics/", "/token-sale/"]:
        for pattern, desc in stale_prices:
            if pattern in content:
                issues.append(f"{rel}: STALE PRICE: {desc} -> '{pattern}'")
    
    for pattern, desc in stale_allocs:
        if pattern in content and rel not in ["/sale/", "/tokenomics/"]:
            issues.append(f"{rel}: STALE ALLOC: {desc} -> '{pattern}'")

# Check for fake/hardcoded data on non-live pages
fake_data = [
    ("1,847", "fake faucet number"),
    ("21 validators", "hardcoded validator count"),
    ("18 services", "hardcoded service count"),
]

for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    for pattern, desc in fake_data:
        if pattern.lower() in content.lower():
            issues.append(f"{rel}: FAKE DATA: {desc} -> '{pattern}'")

# Check for "lorem ipsum", "TODO", "FIXME", "XXX", "HACK" in all pages
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    for word in ["lorem ipsum", "TODO", "FIXME", "XXX", "HACK", "PLACEHOLDER"]:
        if word in content:
            # Get context
            idx = content.index(word)
            ctx = content[max(0,idx-30):idx+len(word)+30].replace("\n"," ")
            issues.append(f"{rel}: {word}: ...{ctx}...")

# Check for "0.010" in sale/tokenomics pages (should be 0.001 now)
for filepath in ["/var/www/verdiscan/sale/index.html", "/var/www/verdiscan/tokenomics/index.html"]:
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    # Look for $0.010 that's NOT in the JS config as listingPrice
    if "$0.010" in content:
        # Check if it's in IDO Price context
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "$0.010" in line and "listingPrice" not in line and "Listing" not in line:
                issues.append(f"{rel} line {i+1}: Possible stale $0.010: {line.strip()[:80]}")

# Check for "0.005" that's not $0.0005
for filepath in ["/var/www/verdiscan/sale/index.html", "/var/www/verdiscan/tokenomics/index.html"]:
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    if "$0.005 " in content and "$0.0005" not in content:
        issues.append(f"{rel}: Has $0.005 but not $0.0005")

# Check for broken img tags
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    imgs = re.findall(r'<img[^>]+>', content)
    for img in imgs:
        src_match = re.search(r'src="([^"]+)"', img)
        if src_match:
            src = src_match.group(1)
            if not src.startswith("data:") and not src.startswith("http"):
                import os
                target = "/var/www/verdiscan" + src
                if not os.path.exists(target):
                    issues.append(f"{rel}: BROKEN IMG: {src}")

# Print results
if issues:
    print(f"FOUND {len(set(issues))} ISSUES:")
    for issue in sorted(set(issues)):
        print(f"  - {issue}")
else:
    print("No additional issues found")
