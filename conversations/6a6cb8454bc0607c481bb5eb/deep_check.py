import re
import os
from bs4 import BeautifulSoup

def deep_check(folder, name):
    filepath = f"audit_pages/{folder}/index.html"
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    print(f"==================================================")
    print(f"PAGE: {folder} ({name})")
    print(f"==================================================")

    # 1. LOGO ANALYSIS
    nav_brand = soup.find('a', class_=re.compile(r'nav-brand|brand', re.I)) or soup.find(class_=re.compile(r'nav-brand|brand', re.I))
    logo_img = nav_brand.find('img') if nav_brand else None
    if not logo_img:
        # Search all imgs for logo
        all_logo_imgs = [img for img in soup.find_all('img') if 'logo' in img.get('src', '').lower() or 'logo' in img.get('class', '')]
        logo_img = all_logo_imgs[0] if all_logo_imgs else None

    logo_src = logo_img.get('src') if logo_img else "No <img> tag used (Text/CSS/SVG or missing)"
    print(f"LOGO FILE USED: {logo_src}")

    # 2. FOOTER ANALYSIS
    footer = soup.find('footer')
    if not footer:
        print("FOOTER: Missing completely")
    else:
        footer_a = footer.find_all('a')
        footer_links = {a.get_text(strip=True): a.get('href', '') for a in footer_a}
        
        # Standard required links: Home, Explorer, DEX, Whitepaper, Wallet, Sale, Tokenomics, Faucet, Validators, Eco, Docs, Governance, GitHub
        req_footer = ['Home', 'Explorer', 'DEX', 'Whitepaper', 'Wallet', 'Sale', 'Tokenomics', 'Faucet', 'Validators', 'Eco', 'Docs', 'Governance', 'GitHub']
        present_footer = []
        missing_footer = []

        for req in req_footer:
            # Check if any link text or href contains this keyword
            found = False
            for txt, href in footer_links.items():
                if req.lower() in txt.lower() or (req.lower() in href.lower() and req.lower() != 'home'):
                    found = True
                    break
                if req == 'Home' and (href == '/' or href == '/index.html' or 'landing' in txt.lower() or 'home' in txt.lower()):
                    found = True
                    break
                if req == 'Explorer' and ('verdiscan' in txt.lower() or '/explorer' in href):
                    found = True
                    break
                if req == 'GitHub' and 'github.com' in href:
                    found = True
                    break
            if found:
                present_footer.append(req)
            else:
                missing_footer.append(req)

        print(f"FOOTER LINKS COUNT: {len(footer_links)}")
        print(f"FOOTER PRESENT REQUIRED: {present_footer}")
        print(f"FOOTER MISSING REQUIRED: {missing_footer}")

    # 3. NAVIGATION ANALYSIS
    nav = soup.find('nav') or soup.find('header')
    if not nav:
        print("NAV: Missing completely")
    else:
        nav_a = nav.find_all('a')
        nav_links = {a.get_text(strip=True): a.get('href', '') for a in nav_a}
        
        # Standard required links: Verdiscan, DEX, Whitepaper, Wallet, Sale, Tokenomics, Faucet
        req_nav = ['Verdiscan', 'DEX', 'Whitepaper', 'Wallet', 'Sale', 'Tokenomics', 'Faucet']
        present_nav = []
        missing_nav = []

        for req in req_nav:
            found = False
            for txt, href in nav_links.items():
                if req.lower() in txt.lower() or (req.lower() in href.lower()):
                    found = True
                    break
                if req == 'Verdiscan' and ('explorer' in href or 'verdiscan' in txt.lower()):
                    found = True
                    break
            if found:
                present_nav.append(req)
            else:
                missing_nav.append(req)

        print(f"NAV LINKS COUNT: {len(nav_links)}")
        print(f"NAV PRESENT REQUIRED: {present_nav}")
        print(f"NAV MISSING REQUIRED: {missing_nav}")

    # 4. TEXT ANALYSIS
    # Ticker: must be VRDX not VERDIS
    # Supply: must be 100B / 100,000,000,000
    # Decimals: must be 9
    # Hardcoded/fake data, stale pricing, broken links, typos
    text_content = soup.get_text()

    # Search ticker misuse
    # e.g., "100 VERDIS", "VERDIS token", "VERDIS ticker", etc.
    ticker_issues = re.findall(r'\b\d+[\d,.]*\s*VERDIS\b|\$\s*VERDIS\b|\bVERDIS\s*token\b|ticker:\s*VERDIS|symbol:\s*VERDIS', html, re.I)
    
    # Search wrong supply
    supply_issues = []
    # Search for supply numbers other than 100B / 100,000,000,000
    for match in re.finditer(r'(\d+[\d,.]*)\s*(billion|b|m|million|trillion)?\s*(vrdx|verdis|tokens)?\s*(supply|total supply|max supply)', html, re.I):
        m_str = match.group(0)
        if '100' not in m_str and '100,000,000,000' not in m_str:
            supply_issues.append(m_str)

    # Search wrong decimals
    decimal_matches = re.findall(r'(\d+)\s*decimals?', html, re.I)
    wrong_decimals = [d for d in decimal_matches if d != '9']

    # Broken links
    broken_links = [a.get('href') for a in soup.find_all('a') if not a.get('href') or a.get('href') == '#' or a.get('href').startswith('javascript:')]

    # Hardcoded/fake data or stale pricing
    fake_data = re.findall(r'\b(?:lorem|ipsum|0x1234567890abcdef|\$0\.05|\$0\.012|fake|mock|placeholder|dummy)\b', html, re.I)

    print(f"TICKER ISSUES: {ticker_issues}")
    print(f"SUPPLY ISSUES: {supply_issues}")
    print(f"DECIMAL MENTIONS: {decimal_matches} (Wrong: {wrong_decimals})")
    print(f"BROKEN LINKS COUNT: {len(broken_links)} -> {broken_links[:5]}")
    print(f"FAKE/STALE DATA MATCHES: {set(fake_data)}")

    # 5. DESIGN ANALYSIS
    # gradient-ui-ux template, 3D floating UI cluster, hardcoded colors, CSS variables --bg-1, --bg-2, --accent
    has_bg1 = '--bg-1' in html
    has_bg2 = '--bg-2' in html
    has_accent = '--accent' in html
    
    uses_gradient_template = 'gradient-ui-ux' in html or 'gradient' in html.lower() or ('--bg-1' in html or '--accent' in html)
    
    # 3D floating UI cluster check
    has_3d_cluster = bool(soup.find(class_=re.compile(r'3d|floating-ui|ui-cluster|hero-3d|cluster-3d|canvas-3d', re.I)) or re.search(r'3d|floating-ui|ui-cluster|hero-3d', html, re.I))

    # Hardcoded colors
    style_content = "\n".join([s.get_text() for s in soup.find_all('style')])
    inline_styles = "\n".join([e.get('style', '') for e in soup.find_all(True) if e.get('style')])
    all_css = style_content + "\n" + inline_styles
    hardcoded_hex = set(re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', all_css))

    print(f"CSS VARS: --bg-1: {has_bg1}, --bg-2: {has_bg2}, --accent: {has_accent}")
    print(f"GRADIENT UI UX TEMPLATE: {uses_gradient_template}")
    print(f"3D FLOATING UI CLUSTER: {has_3d_cluster}")
    print(f"HARDCODED HEX COLORS COUNT: {len(hardcoded_hex)} (Sample: {list(hardcoded_hex)[:5]})")
    print("\n")

