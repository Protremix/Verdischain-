#!/usr/bin/env python3
"""Audit all Verdis Chain pages for footer consistency, text sizes, and broken elements."""
import os
import re
from html.parser import HTMLParser

BASE = "/var/www/verdiscan"
PAGES = [
    ("Landing", "index.html"),
    ("Explorer", "explorer/index.html"),
    ("DEX", "dex/index.html"),
    ("Validators", "validators/index.html"),
    ("Eco", "eco/index.html"),
    ("Faucet", "faucet/index.html"),
    ("Wallet", "wallet/index.html"),
    ("Sale", "sale/index.html"),
    ("Referral", "referral/index.html"),
    ("Incentives", "incentives/index.html"),
    ("Docs", "docs/index.html"),
    ("Whitepaper", "whitepaper/index.html"),
    ("Contact", "contact/index.html"),
    ("API", "api/index.html"),
]

# Expected footer links (from the homepage)
EXPECTED_FOOTER = ["Landing", "Verdiscan", "DEX", "Validators", "Eco", "Contact", "API", "Docs", "GitHub"]

# Expected nav links
EXPECTED_NAV = ["Home", "Verdiscan", "DEX", "Validators", "Eco", "Faucet", "Wallet", "Sale", "Contact", "API", "Docs"]

print("=" * 80)
print("VERDIS CHAIN PAGE AUDIT")
print("=" * 80)

# 1. FOOTER AUDIT
print("\n## 1. FOOTER LINKS AUDIT")
print("-" * 40)
footer_ref = None
for name, path in PAGES:
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        print(f"  {name}: MISSING FILE!")
        continue
    with open(full, 'r', errors='replace') as f:
        content = f.read()
    
    # Extract footer section - look for <footer> tag
    footer_match = re.search(r'<footer[^>]*>(.*?)</footer>', content, re.DOTALL | re.IGNORECASE)
    if not footer_match:
        # Try to find footer by looking for copyright text
        footer_match = re.search(r'(© 2026.*?</div>\s*</div>\s*</div>)', content, re.DOTALL | re.IGNORECASE)
    
    if footer_match:
        footer_html = footer_match.group(1)
        # Extract all links from footer
        links = re.findall(r'<a[^>]*>(.*?)</a>', footer_html, re.DOTALL)
        links_clean = [re.sub(r'<[^>]+>', '', l).strip() for l in links]
        
        if footer_ref is None:
            footer_ref = links_clean
            print(f"  {name} (REFERENCE): {links_clean}")
        else:
            if links_clean == footer_ref:
                print(f"  {name}: ✓ MATCHES reference")
            else:
                missing = [l for l in footer_ref if l not in links_clean]
                extra = [l for l in links_clean if l not in footer_ref]
                if missing or extra:
                    print(f"  {name}: ✗ MISMATCH")
                    if missing: print(f"    Missing: {missing}")
                    if extra: print(f"    Extra: {extra}")
                else:
                    print(f"  {name}: ~ Same links, different order")
    else:
        print(f"  {name}: ✗ NO FOOTER FOUND")

# 2. NAVIGATION AUDIT
print("\n## 2. NAVIGATION LINKS AUDIT")
print("-" * 40)
nav_ref = None
for name, path in PAGES:
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        continue
    with open(full, 'r', errors='replace') as f:
        content = f.read()
    
    # Look for nav section
    nav_match = re.search(r'<nav[^>]*>(.*?)</nav>', content, re.DOTALL | re.IGNORECASE)
    if nav_match:
        nav_html = nav_match.group(1)
        links = re.findall(r'<a[^>]*>(.*?)</a>', nav_html, re.DOTALL)
        links_clean = [re.sub(r'<[^>]+>', '', l).strip() for l in links if l.strip()]
        
        if nav_ref is None:
            nav_ref = links_clean
            print(f"  {name} (REFERENCE): {links_clean}")
        else:
            missing = [l for l in nav_ref if l not in links_clean]
            extra = [l for l in links_clean if l not in nav_ref]
            if not missing and not extra:
                print(f"  {name}: ✓ MATCHES nav")
            else:
                print(f"  {name}: ✗ MISMATCH")
                if missing: print(f"    Missing: {missing}")
                if extra: print(f"    Extra: {extra}")
    else:
        print(f"  {name}: ✗ NO <nav> TAG")

# 3. TEXT SIZE AUDIT
print("\n## 3. TEXT SIZE AUDIT (looking for large/inline font-size)")
print("-" * 40)
for name, path in PAGES:
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        continue
    with open(full, 'r', errors='replace') as f:
        content = f.read()
    
    # Find all inline font-size declarations
    sizes = re.findall(r'font-size:\s*([0-9.]+)px', content, re.IGNORECASE)
    large_sizes = [s for s in sizes if float(s) > 20]
    
    # Find all Tailwind text-* classes that are large
    tailwind_large = re.findall(r'text-(?:xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)\b', content)
    
    # Find font-size in <style> blocks
    style_sizes = re.findall(r'font-size:\s*([0-9.]+)\s*(?:px|rem|em)', content)
    style_large = [s for s in style_sizes if float(s.replace('px','').replace('rem','').replace('em','')) > 20]
    
    issues = []
    if large_sizes:
        issues.append(f"Inline large sizes: {large_sizes}")
    if tailwind_large:
        issues.append(f"Tailwind large classes: {tailwind_large[:5]}...")
    if style_large:
        issues.append(f"Style block large: {style_large[:5]}...")
    
    if issues:
        print(f"  {name}: ⚠️  {', '.join(issues)}")
    else:
        print(f"  {name}: ✓ No large text sizes")

# 4. BROKEN ELEMENTS AUDIT
print("\n## 4. BROKEN ELEMENTS AUDIT")
print("-" * 40)
for name, path in PAGES:
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        continue
    with open(full, 'r', errors='replace') as f:
        content = f.read()
    
    issues = []
    
    # Check for unclosed tags (basic check)
    open_divs = content.count('<div')
    close_divs = content.count('</div>')
    if open_divs != close_divs:
        issues.append(f"div mismatch: {open_divs} open vs {close_divs} close")
    
    # Check for missing images
    img_srcs = re.findall(r'<img[^>]*src=["\']([^"\']*)["\']', content)
    for src in img_srcs:
        if src.startswith('http'):
            continue  # External, skip
        if src.startswith('/'):
            img_path = os.path.join(BASE, src.lstrip('/'))
        else:
            img_path = os.path.join(os.path.dirname(full), src)
        if not os.path.exists(img_path):
            issues.append(f"Missing image: {src}")
    
    # Check for broken internal links (href to pages that don't exist)
    hrefs = re.findall(r'href=["\']/?((?:[a-z][a-z0-9-]*/?)*)["\']', content, re.IGNORECASE)
    for href in hrefs:
        if not href or href.startswith('#') or href.startswith('http') or href.startswith('mailto'):
            continue
        # Check if the linked page exists
        link_path = os.path.join(BASE, href.rstrip('/'), 'index.html')
        if href.endswith('.html'):
            link_path = os.path.join(BASE, href)
        if not os.path.exists(link_path) and not os.path.exists(os.path.join(BASE, href)):
            # Skip common non-page paths
            if href not in ['assets/', 'css/', 'js/', 'favicon.ico', 'favicon.svg', 'robots.txt', 'sitemap.xml', 'rpc', 'ws', 'api']:
                issues.append(f"Broken link: /{href}")
    
    # Check for JavaScript errors (basic syntax check)
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    for i, script in enumerate(scripts):
        if not script.strip():
            continue
        # Check for common issues
        if 'undefined' in script and 'typeof' not in script:
            pass  # Too many false positives
        try:
            compile(script, f"{name}_script_{i}", 'exec')
        except SyntaxError as e:
            issues.append(f"JS syntax error: {e}")
    
    # Check for empty sections (elements with no content)
    empty_sections = re.findall(r'<(h[1-6])[^>]*>\s*</\1>', content)
    if empty_sections:
        issues.append(f"Empty headings: {len(empty_sections)}")
    
    # Check for placeholder text
    placeholders = ['TODO', 'FIXME', 'PLACEHOLDER', 'Lorem ipsum', 'Coming soon', 'Coming Soon']
    for p in placeholders:
        if p in content:
            issues.append(f"Placeholder text: '{p}'")
    
    if issues:
        print(f"  {name}: ⚠️  {'; '.join(issues[:5])}")
    else:
        print(f"  {name}: ✓ No issues found")

# 5. CSS CONSISTENCY
print("\n## 5. CSS/THEME CONSISTENCY")
print("-" * 40)
for name, path in PAGES:
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        continue
    with open(full, 'r', errors='replace') as f:
        content = f.read()
    
    # Check if page has inline <style> or external CSS
    has_inline_style = '<style>' in content
    has_external_css = 'stylesheet' in content or '.css' in content
    
    # Check for Tailwind CDN (should not be present)
    has_tailwind_cdn = 'cdn.tailwindcss.com' in content
    
    # Check for color values
    hardcoded_colors = re.findall(r'(?:color|background|bg):\s*(#[0-9a-fA-F]{3,8})', content)
    inline_hex = re.findall(r'style=["\'][^"\']*color:\s*#[0-9a-fA-F]{3,8}', content)
    
    issues = []
    if has_tailwind_cdn:
        issues.append("Has Tailwind CDN (should be removed)")
    if inline_hex:
        issues.append(f"Inline hex colors: {len(inline_hex)}")
    
    if issues:
        print(f"  {name}: ⚠️  {'; '.join(issues)}")
    else:
        print(f"  {name}: ✓ CSS clean")

# 6. RESPONSIVE CHECK
print("\n## 6. RESPONSIVE/META CHECK")
print("-" * 40)
for name, path in PAGES:
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        continue
    with open(full, 'r', errors='replace') as f:
        content = f.read()
    
    issues = []
    if 'viewport' not in content:
        issues.append("Missing viewport meta")
    if '<meta name="description"' not in content.lower():
        issues.append("Missing meta description")
    if 'lang=' not in content[:200]:
        issues.append("Missing lang attribute")
    
    if issues:
        print(f"  {name}: ⚠️  {'; '.join(issues)}")
    else:
        print(f"  {name}: ✓ Meta tags present")

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
