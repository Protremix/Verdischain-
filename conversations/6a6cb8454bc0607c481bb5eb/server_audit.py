#!/usr/bin/env python3
"""Server-side audit of all Verdis Chain HTML pages."""
import re, os, glob

issues = []

# 1. Check for hardcoded/fake values
fake_patterns = [
    (r"\b8 peers\b", "hardcoded peer count"),
    (r"\b21 validators\b", "hardcoded validator count"),
    (r"\b18 services\b", "hardcoded service count"),
    (r"\b14 peers\b", "hardcoded peer count"),
    (r"\$300M\b", "old hard cap (should be $17.5M)"),
    (r"\$250M\b", "old hard cap (should be $17.5M)"),
    (r"\b3 IDO phases\b", "should be 4 IDO phases"),
    (r"\b\$1,847\b", "fake faucet distribution"),
    (r"\b1,847\b", "fake faucet number"),
    (r"\bTODO\b", "TODO comment"),
    (r"\bFIXME\b", "FIXME comment"),
    (r"\blorem ipsum\b", "lorem ipsum"),
    (r"\bexample\.com\b", "example domain"),
]

for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    try:
        with open(filepath) as f:
            content = f.read()
        for pattern, desc in fake_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                issues.append(f"{rel}: {desc} -> '{matches[0]}'")
    except:
        pass

# 2. Check for old IDO pricing (should be $0.0005/$0.001/$0.002/$0.0025)
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    try:
        with open(filepath) as f:
            content = f.read()
        if "$0.005 / VRDX" in content or "$0.010 / VRDX" in content or "$0.025 / VRDX" in content:
            if rel in ["/sale/", "/tokenomics/"]:
                issues.append(f"{rel}: old IDO price found")
        if "$0.05 / VRDX" in content and rel in ["/sale/", "/tokenomics/"]:
            issues.append(f"{rel}: old public sale price $0.05")
    except:
        pass

# 3. Check for broken internal links
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    try:
        with open(filepath) as f:
            content = f.read()
        link_pattern = r'href=["\x27]([^"\x27]+)["\x27]'
        links = re.findall(link_pattern, content)
        for link in links:
            if link.startswith("/") and not link.startswith("//") and not link.startswith("/api/") and not link.startswith("/rpc") and not link.startswith("/ws") and not link.startswith("/assets/"):
                target = link.rstrip("/")
                if not target:
                    target = "/"
                if target == "/":
                    target_path = "/var/www/verdiscan/index.html"
                elif target.endswith(".html"):
                    target_path = "/var/www/verdiscan" + target
                else:
                    target_path = "/var/www/verdiscan" + target + "/index.html"
                
                if not os.path.exists(target_path):
                    # Check if it's an anchor link
                    if "#" in link:
                        continue
                    issues.append(f"{rel}: BROKEN LINK -> {link}")
    except:
        pass

# 4. Check for missing alt text on images
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    try:
        with open(filepath) as f:
            content = f.read()
        img_pattern = r'<img[^>]*>'
        imgs = re.findall(img_pattern, content)
        for img in imgs:
            if 'alt=' not in img:
                src_match = re.search(r'src="([^"]+)"', img)
                src = src_match.group(1) if src_match else "?"
                if not src.startswith("data:"):
                    issues.append(f"{rel}: IMG without alt text -> {src}")
    except:
        pass

# 5. Check for "lorem", "test", "placeholder" in visible text
for filepath in sorted(glob.glob("/var/www/verdiscan/**/*.html", recursive=True)):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    try:
        with open(filepath) as f:
            content = f.read()
        for word in ["lorem ipsum", "test data", "placeholder text"]:
            if word in content.lower():
                issues.append(f"{rel}: placeholder text -> {word}")
    except:
        pass

# Print results
if issues:
    print(f"FOUND {len(set(issues))} UNIQUE ISSUES:")
    for issue in sorted(set(issues)):
        print(f"  - {issue}")
else:
    print("No server-side issues found")
