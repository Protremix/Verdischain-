import re
import os
from bs4 import BeautifulSoup

PAGES = [
    ('eco', 'Eco'),
    ('docs', 'Documentation'),
    ('faucet', 'Faucet'),
    ('wallet', 'Web Wallet'),
    ('monitoring', 'Monitoring'),
    ('analytics', 'Analytics'),
    ('status', 'Status'),
    ('security', 'Security')
]

STD_NAV_LINKS = ['verdiscan', 'dex', 'whitepaper', 'wallet', 'sale', 'tokenomics', 'faucet']
STD_FOOTER_LINKS = ['home', 'explorer', 'dex', 'whitepaper', 'wallet', 'sale', 'tokenomics', 'faucet', 'validators', 'eco', 'docs', 'governance', 'github']

def run_audit():
    for folder, name in PAGES:
        filepath = f"audit_pages/{folder}/index.html"
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')

        print("="*60)
        print(f"PAGE: {folder} ({name})")
        print("="*60)

        # 1. LOGO
        logo_imgs = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            cls = " ".join(img.get('class', []))
            id_ = img.get('id', '')
            if 'logo' in src.lower() or 'logo' in alt.lower() or 'logo' in cls.lower() or 'logo' in id_.lower():
                logo_imgs.append((src, alt, cls))
        
        # also search for brand/logo divs or svgs or CSS background
        brand = soup.find(class_=re.compile(r'brand|logo', re.I)) or soup.find(id=re.compile(r'brand|logo', re.I))
        
        print("--- LOGO ---")
        if logo_imgs:
            for src, alt, cls in logo_imgs:
                print(f"Img logo src: {src} | alt: '{alt}' | class: '{cls}'")
        elif brand:
            print(f"Brand element found (no <img> logo): {brand.prettify()[:200]}")
        else:
            print("No logo image or brand element found!")

        # 2. NAVIGATION
        print("\n--- NAVIGATION ---")
        nav = soup.find('nav') or soup.find('header')
        if nav:
            nav_a = nav.find_all('a')
            nav_links = [(a.get_text(strip=True), a.get('href', '')) for a in nav_a]
            print(f"Nav found with {len(nav_links)} links:")
            for txt, href in nav_links:
                print(f"  - '{txt}' -> {href}")
        else:
            print("No <nav> or <header> tag found!")

        # 3. FOOTER
        print("\n--- FOOTER ---")
        footer = soup.find('footer')
        if footer:
            footer_a = footer.find_all('a')
            footer_links = [(a.get_text(strip=True), a.get('href', '')) for a in footer_a]
            print(f"Footer found with {len(footer_links)} links:")
            for txt, href in footer_links:
                print(f"  - '{txt}' -> {href}")
        else:
            print("No <footer> tag found!")

        # 4. TEXT & DATA
        print("\n--- TEXT & DATA CHECKS ---")
        # Check tickers: VERDIS as ticker vs VRDX
        # Search for token supply: 100B / 100,000,000,000
        # Search for decimals
        # Search for hardcoded data / fake stats / stale pricing
        
        # Token Ticker matches
        verdis_ticker_matches = re.findall(r'\bVERDIS\b', html)
        vrdx_ticker_matches = re.findall(r'\bVRDX\b', html)
        print(f"VERDIS count: {len(verdis_ticker_matches)} | VRDX count: {len(vrdx_ticker_matches)}")

        # Print snippets containing VERDIS or VRDX
        ticker_snippets = re.findall(r'.{0,40}(?:VERDIS|VRDX).{0,40}', html, re.IGNORECASE)
        print("Ticker snippets sample (first 10):")
        for snip in ticker_snippets[:10]:
            print("  ", repr(snip.strip().replace('\n', ' ')))

        # Supply / Decimals
        supply_snips = re.findall(r'.{0,40}(?:supply|billion|100b|100,000,000,000|decimal).{0,40}', html, re.IGNORECASE)
        print("Supply/Decimal snippets sample (first 10):")
        for snip in supply_snips[:10]:
            print("  ", repr(snip.strip().replace('\n', ' ')))

        # Link audit (#, javascript:void, dead links)
        all_links = soup.find_all('a')
        hash_links = [a.get('href') for a in all_links if a.get('href') == '#' or a.get('href', '').startswith('javascript:')]
        print(f"Placeholder/Hash links count: {len(hash_links)} ({hash_links[:5]})")

        # 5. DESIGN
        print("\n--- DESIGN CHECKS ---")
        has_bg1 = '--bg-1' in html
        has_bg2 = '--bg-2' in html
        has_accent = '--accent' in html
        has_grad_ui = 'gradient-ui-ux' in html or 'gradient' in html
        print(f"CSS Variables: --bg-1: {has_bg1}, --bg-2: {has_bg2}, --accent: {has_accent}")
        print(f"Gradient UI reference: {has_grad_ui}")

        # Check 3D cluster
        has_3d = any(k in html.lower() for k in ['3d', 'cluster', 'floating-ui', 'floating_ui', 'ui-cluster', 'perspective', 'spline', 'three.js', 'canvas', 'hero-3d'])
        print(f"3D Floating UI cluster check: {has_3d}")

        # Check hardcoded colors sample
        hex_colors = re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', html)
        print(f"Hardcoded hex colors count: {len(hex_colors)} (Sample: {set(hex_colors[:10])})")

        print("\n\n")

run_audit()
