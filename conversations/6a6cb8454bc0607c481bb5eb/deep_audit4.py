#!/usr/bin/env python3
"""Deep audit pass 4 - CSS issues, JS errors, duplicate content, internal link consistency."""
import re, glob, os

issues = []

# 1. Check for CSS files referenced but not existing
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    css_refs = re.findall(r'href="([^"]+\.css[^"]*)"', content)
    for css in css_refs:
        if css.startswith("/"):
            css_path = css.split("?")[0]  # Remove query params
            full_path = "/var/www/verdiscan" + css_path
            if not os.path.exists(full_path):
                issues.append(f"{rel}: MISSING CSS: {css}")

# 2. Check for JS files referenced but not existing
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    js_refs = re.findall(r'src="([^"]+\.js[^"]*)"', content)
    for js in js_refs:
        if js.startswith("/") and not js.startswith("/_next/"):
            js_path = js.split("?")[0]
            full_path = "/var/www/verdiscan" + js_path
            if not os.path.exists(full_path):
                issues.append(f"{rel}: MISSING JS: {js}")

# 3. Check for image files referenced but not existing
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    img_refs = re.findall(r'src="([^"]+\.(png|jpg|jpeg|svg|gif|webp)[^"]*)"', content)
    for img, ext in img_refs:
        if img.startswith("/") and not img.startswith("/assets/"):
            img_path = img.split("?")[0]
            full_path = "/var/www/verdiscan" + img_path
            if not os.path.exists(full_path):
                issues.append(f"{rel}: MISSING IMG: {img}")
        elif img.startswith("/assets/"):
            img_path = img.split("?")[0]
            full_path = "/var/www/verdiscan" + img_path
            if not os.path.exists(full_path):
                issues.append(f"{rel}: MISSING IMG: {img}")

# 4. Check for broken anchor links (href="#..." without matching id)
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    # Get all ids
    ids = set(re.findall(r'id="([^"]+)"', content))
    # Get all anchor links
    anchors = re.findall(r'href="#([^"]+)"', content)
    for anchor in anchors:
        if anchor and anchor not in ids and anchor not in ["top", ""]:
            issues.append(f"{rel}: BROKEN ANCHOR: #{anchor}")

# 5. Check for duplicate IDs in same file
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    ids = re.findall(r'id="([^"]+)"', content)
    from collections import Counter
    dupes = [k for k, v in Counter(ids).items() if v > 1]
    for dup in dupes:
        issues.append(f"{rel}: DUPLICATE ID: {dup} ({Counter(ids)[dup]}x)")

# 6. Check for mixed protocol asset loading (http:// on https site)
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    if 'http://' in content and 'https://verdischain.com' not in content:
        http_refs = re.findall(r'(?:src|href)="(http://[^"]+)"', content)
        for ref in http_refs:
            if "localhost" not in ref and "127.0.0.1" not in ref:
                issues.append(f"{rel}: INSECURE HTTP: {ref}")

# Print
if issues:
    print(f"FOUND {len(set(issues))} ISSUES:")
    for issue in sorted(set(issues)):
        print(f"  - {issue}")
else:
    print("No additional issues found")
