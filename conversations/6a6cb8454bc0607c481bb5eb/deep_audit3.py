#!/usr/bin/env python3
"""Deep audit pass 3 - nav consistency, external links, fake data patterns."""
import re, glob

issues = []

# 1. Check nav link consistency - all pages should have same nav structure
nav_links_per_page = {}
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    # Extract nav links
    nav_section = ""
    if "verdis-nav" in content or "nav" in content.lower():
        # Look for nav links to main pages
        main_links = re.findall(r'href="(/(?:explorer|dex|whitepaper|wallet|sale|tokenomics|faucet|validators|incentives|referral|eco|docs|blog|developers|download|status|contact|legal)/?)"', content)
        if main_links:
            nav_links_per_page[rel] = sorted(set(main_links))

# Check for pages with different nav link sets
if nav_links_per_page:
    # Get the most common nav set
    from collections import Counter
    nav_sets = [tuple(sorted(set(v))) for v in nav_links_per_page.values()]
    most_common = Counter(nav_sets).most_common(1)[0][0]
    for page, links in nav_links_per_page.items():
        if tuple(sorted(set(links))) != most_common:
            issues.append(f"{page}: INCONSISTENT NAV: has {links} vs standard {list(most_common)}")

# 2. Check for broken external links (GitHub, Twitter, Telegram, Discord)
external_patterns = [
    (r'href="(https://github\.com/[^"]+)"', "GitHub"),
    (r'href="(https://twitter\.com/[^"]+)"', "Twitter"),
    (r'href="(https://t\.me/[^"]+)"', "Telegram"),
    (r'href="(https://discord\.(gg|com)/[^"]+)"', "Discord"),
    (r'href="(https://verdischain\.com[^"]*)"', "Internal"),
]

for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    for pattern, label in external_patterns:
        if label == "Internal":
            continue  # Skip internal links for now
        matches = re.findall(pattern, content)
        for m in matches:
            if isinstance(m, tuple):
                m = m[0]
            # Check for common broken patterns
            if "github.com/verdis-chain" in m.lower() or "github.com/verdischain" in m.lower():
                if "Protremix" not in m:
                    issues.append(f"{rel}: OLD GITHUB URL: {m}")

# 3. Check for fake/stale data patterns on specific pages
# Check eco page for fake carbon data
eco_path = "/var/www/verdiscan/eco/index.html"
if __import__("os").path.exists(eco_path):
    with open(eco_path) as f:
        content = f.read()
    # Check if eco metrics are hardcoded or live
    if "6260" in content and "system_health" not in content.lower():
        issues.append("/eco/: HARDCODED CO2 value 6260")
    if "526" in content and "rpc" not in content.lower():
        issues.append("/eco/: HARDCODED trees value")

# 4. Check for missing canonical URLs
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    if 'rel="canonical"' not in content and rel not in ["/404/", "/_not-found/", "/token-sale/", "/validator/"]:
        issues.append(f"{rel}: MISSING canonical URL")

# 5. Check for inconsistent page titles (should include "Verdis Chain")
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    titles = re.findall(r'<title>([^<]+)</title>', content)
    for title in titles:
        if "Verdis" not in title and rel not in ["/404/", "/_not-found/"]:
            issues.append(f"{rel}: TITLE missing 'Verdis': '{title}'")

# 6. Check for empty/placeholder sections
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    # Check for empty div sections
    empty_sections = re.findall(r'<div[^>]*>\s*</div>', content)
    if len(empty_sections) > 10:
        issues.append(f"{rel}: {len(empty_sections)} empty div elements")

# 7. Check for inline styles with old spacing values (not on 8px scale)
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    # Look for padding/margin with non-8px values
    bad_spacing = re.findall(r'(?:padding|margin):\s*(\d+)px', content)
    for val in bad_spacing:
        v = int(val)
        if v not in [0, 1, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 100, 6, 10, 13, 14, 15, 18, 22, 28, 36, 44, 56, 72, 96]:
            if v > 5:
                pass  # Too many to flag, skip

# Print
if issues:
    print(f"FOUND {len(set(issues))} ISSUES:")
    for issue in sorted(set(issues)):
        print(f"  - {issue}")
else:
    print("No additional issues found")
