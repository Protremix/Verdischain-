import re
import os
import sys

pages = {
    "Homepage": "/var/www/verdiscan/index.html",
    "Sale": "/var/www/verdiscan/sale/index.html",
    "Tokenomics": "/var/www/verdiscan/tokenomics/index.html",
    "Whitepaper": "/var/www/verdiscan/whitepaper/index.html"
}

standard_nav_links = ["Verdiscan", "DEX", "Whitepaper", "Wallet", "Sale", "Tokenomics", "Faucet"]
standard_footer_links = ["Home", "Explorer", "DEX", "Whitepaper", "Wallet", "Sale", "Tokenomics", "Faucet", "Validators", "Eco", "Docs", "Governance", "GitHub"]

for name, path in pages.items():
    print("="*100)
    print(f"ANALYZING PAGE: {name} ({path})")
    print("="*100)
    
    if not os.path.exists(path):
        print("ERROR: File does not exist")
        continue

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # 1. LOGO CHECK
    print("\n--- 1. LOGO ANALYSIS ---")
    img_tags = re.findall(r'<img[^>]+>', html, re.IGNORECASE)
    logos = []
    for img in img_tags:
        src_m = re.search(r'src=["\']([^"\']+)["\']', img, re.IGNORECASE)
        alt_m = re.search(r'alt=["\']([^"\']+)["\']', img, re.IGNORECASE)
        class_m = re.search(r'class=["\']([^"\']+)["\']', img, re.IGNORECASE)
        src = src_m.group(1) if src_m else ""
        if 'logo' in src.lower() or 'logo' in (alt_m.group(1) if alt_m else "").lower() or 'logo' in (class_m.group(1) if class_m else "").lower():
            logos.append((src, img))
    print(f"Found {len(logos)} logo images:")
    for src, img in logos:
        print(f"  src: {src} | tag: {img}")

    # Also search for logo in header / nav specifically
    nav_match = re.search(r'<(nav|header)[^>]*>(.*?)</\1>', html, re.DOTALL | re.IGNORECASE)
    if nav_match:
        nav_html = nav_match.group(0)
        nav_logos = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', nav_html, re.IGNORECASE)
        print(f"  Logos specifically inside nav/header: {nav_logos}")

    # 2. FOOTER ANALYSIS
    print("\n--- 2. FOOTER ANALYSIS ---")
    footer_match = re.search(r'<footer[^>]*>(.*?)</footer>', html, re.DOTALL | re.IGNORECASE)
    if footer_match:
        footer_html = footer_match.group(1)
        print("  Footer tag present.")
        # Extract links in footer
        footer_links = re.findall(r'<a[^>]+href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', footer_html, re.DOTALL | re.IGNORECASE)
        clean_f_links = []
        for href, text in footer_links:
            text_clean = re.sub(r'<[^>]+>', '', text).strip()
            clean_f_links.append((text_clean, href))
        print("  Footer links found:")
        for t, h in clean_f_links:
            print(f"    - '{t}': '{h}'")
    else:
        print("  NO <footer> TAG FOUND!")

    # 3. NAVIGATION ANALYSIS
    print("\n--- 3. NAVIGATION ANALYSIS ---")
    if nav_match:
        nav_html = nav_match.group(0)
        print("  Nav/Header tag present.")
        nav_links = re.findall(r'<a[^>]+href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', nav_html, re.DOTALL | re.IGNORECASE)
        clean_n_links = []
        for href, text in nav_links:
            text_clean = re.sub(r'<[^>]+>', '', text).strip()
            clean_n_links.append((text_clean, href))
        print("  Nav links found:")
        for t, h in clean_n_links:
            print(f"    - '{t}': '{h}'")
    else:
        print("  NO <nav> or <header> TAG FOUND!")

    # 4. TEXT ANALYSIS
    print("\n--- 4. TEXT / DATA ANALYSIS ---")
    # Check tickers
    # Search for VERDIS vs VRDX in text (excluding attributes or script URLs if possible)
    # Let's clean tags out to inspect visible text
    text_only = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text_only = re.sub(r'<script[^>]*>.*?</script>', '', text_only, flags=re.DOTALL | re.IGNORECASE)
    text_only_clean = re.sub(r'<[^>]+>', ' ', text_only)
    
    verdis_count = len(re.findall(r'\bVERDIS\b', text_only_clean))
    vrdx_count = len(re.findall(r'\bVRDX\b', text_only_clean))
    print(f"  Ticker occurrences in body text -> VERDIS: {verdis_count}, VRDX: {vrdx_count}")
    if verdis_count > 0:
        # Find snippets where VERDIS is used as a token ticker
        verdis_snippets = re.findall(r'([^.\n]{0,30}\bVERDIS\b[^.\n]{0,30})', text_only_clean)
        print(f"  Sample VERDIS snippets: {verdis_snippets[:5]}")

    # Check supply mentions
    supply_matches = re.findall(r'([^.\n]{0,40}(?:supply|total supply|max supply|100|billion|b|trillion|t|million)[^.\n]{0,40})', text_only_clean, re.IGNORECASE)
    print(f"  Supply mentions ({len(supply_matches)} found):")
    for s in supply_matches[:10]:
        print(f"    - {s.strip()}")

    # Check decimals
    decimal_matches = re.findall(r'([^.\n]{0,40}decimal[^.\n]{0,40})', text_only_clean, re.IGNORECASE)
    print(f"  Decimal mentions ({len(decimal_matches)} found):")
    for d in decimal_matches:
        print(f"    - {d.strip()}")

    # Check hardcoded fake data / pricing / placeholder text
    placeholders = re.findall(r'([^.\n]{0,40}(?:lorem|ipsum|placeholder|fake|sample|0\.0000|\$0\.00|000,000|testnet|tbd)[^.\n]{0,40})', text_only_clean, re.IGNORECASE)
    if placeholders:
        print(f"  Potential placeholder/fake data text ({len(placeholders)} found):")
        for p in placeholders[:10]:
            print(f"    - {p.strip()}")

    # Check links (broken/empty/hash links)
    all_links = re.findall(r'<a[^>]+href=["\']([^"\']*)["\'][^>]*>', html, re.IGNORECASE)
    empty_links = [l for l in all_links if l == "" or l == "#" or l.startswith("javascript:")]
    print(f"  Total links: {len(all_links)}, Empty/Hash links: {len(empty_links)}")

    # 5. DESIGN ANALYSIS
    print("\n--- 5. DESIGN / CSS ANALYSIS ---")
    # CSS variables
    bg1 = re.findall(r'--bg-1\s*:\s*([^;}\n]+)', html)
    bg2 = re.findall(r'--bg-2\s*:\s*([^;}\n]+)', html)
    accent = re.findall(r'--accent\s*:\s*([^;}\n]+)', html)
    print(f"  CSS Variables defined in page -> --bg-1: {bg1}, --bg-2: {bg2}, --accent: {accent}")

    # Check external CSS link files
    css_files = re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    print(f"  CSS stylesheet files: {css_files}")

    # Check for 3D floating UI cluster
    floating_ui = re.findall(r'class=["\'][^"\']*(?:floating|cluster|ui-cluster|3d)[^"\']*["\']', html, re.IGNORECASE)
    print(f"  Floating/Cluster UI elements: {floating_ui[:5]}")

    # Check for hardcoded colors in style attributes
    inline_styles = re.findall(r'style=["\']([^"\']*)["\']', html, re.IGNORECASE)
    color_matches = []
    for style in inline_styles:
        colors = re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b|rgb\([^)]+\)|rgba\([^)]+\)', style)
        if colors:
            color_matches.extend(colors)
    print(f"  Inline style hardcoded colors count: {len(color_matches)} (Sample: {color_matches[:5]})")

