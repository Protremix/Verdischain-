import re
import os
from bs4 import BeautifulSoup

PAGES = [
    ('eco', 'eco'),
    ('docs', 'documentation'),
    ('faucet', 'faucet'),
    ('wallet', 'web wallet'),
    ('monitoring', 'monitoring'),
    ('analytics', 'analytics'),
    ('status', 'status'),
    ('security', 'security')
]

STD_NAV_REQUIRED = [
    ('Verdiscan', ['/explorer', 'verdiscan', '/explorer/']),
    ('DEX', ['/dex', '/dex/']),
    ('Whitepaper', ['/whitepaper', '/whitepaper/']),
    ('Wallet', ['/wallet', '/wallet/']),
    ('Sale', ['/sale', '/sale/']),
    ('Tokenomics', ['/tokenomics', '/tokenomics/']),
    ('Faucet', ['/faucet', '/faucet/'])
]

STD_FOOTER_REQUIRED = [
    ('Home', ['/', '/index.html']),
    ('Explorer', ['/explorer', '/explorer/']),
    ('DEX', ['/dex', '/dex/']),
    ('Whitepaper', ['/whitepaper', '/whitepaper/']),
    ('Wallet', ['/wallet', '/wallet/']),
    ('Sale', ['/sale', '/sale/']),
    ('Tokenomics', ['/tokenomics', '/tokenomics/']),
    ('Faucet', ['/faucet', '/faucet/']),
    ('Validators', ['/validators', '/validators/']),
    ('Eco', ['/eco', '/eco/']),
    ('Docs', ['/docs', '/docs/']),
    ('Governance', ['/governance', '/governance/']),
    ('GitHub', ['github.com'])
]

def analyze_one(folder, name):
    filepath = f"audit_pages/{folder}/index.html"
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    print(f"==================== PAGE: {folder} ({name}) ====================")

    # 1. LOGO
    # Prompt: "What logo file is used? Subpages should use verdis-logo-black.png (black text for light backgrounds). Check the img src for the logo."
    logo_imgs = []
    for img in soup.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', '')
        cls = " ".join(img.get('class', []))
        if 'logo' in src.lower() or 'logo' in alt.lower() or 'logo' in cls.lower() or 'brand' in cls.lower() or img.find_parent('a', class_=re.compile(r'brand|logo', re.I)):
            logo_imgs.append((src, alt, cls))
    
    # Also check if nav brand has an img at all
    nav_brand = soup.find(class_=re.compile(r'nav-brand|brand|logo-link', re.I)) or soup.find('a', href='/')
    nav_brand_imgs = nav_brand.find_all('img') if nav_brand else []

    print(f"Nav Brand element: {nav_brand}")
    print(f"Nav Brand imgs: {nav_brand_imgs}")
    print(f"All logo/brand imgs found on page: {logo_imgs}")

    # 2. FOOTER
    # Prompt: "Does the footer exist? Does it match the standard footer (should have links to Home, Explorer, DEX, Whitepaper, Wallet, Sale, Tokenomics, Faucet, Validators, Eco, Docs, Governance, GitHub)? Is it consistent across pages?"
    footer = soup.find('footer')
    if not footer:
        print("FOOTER: NOT FOUND")
    else:
        f_links = [(a.get_text(strip=True), a.get('href', '')) for a in footer.find_all('a')]
        print(f"FOOTER: FOUND ({len(f_links)} links)")
        # Check standard required links
        found_labels = [txt for txt, href in f_links]
        found_hrefs = [href for txt, href in f_links]
        
        missing = []
        for req, pattern in STD_FOOTER_REQUIRED:
            has_req = any(req.lower() in t.lower() for t in found_labels) or any(p[0] in h for h in found_hrefs for p in pattern)
            if not has_req:
                missing.append(req)
        print("Footer links present:", f_links)
        print("Missing standard footer links:", missing)

    # 3. NAVIGATION
    # Prompt: "Does the top nav exist? Does it have the standard links (Verdiscan, DEX, Whitepaper, Wallet, Sale, Tokenomics, Faucet)? Is it consistent?"
    nav = soup.find('nav') or soup.find('header')
    if not nav:
        print("NAV: NOT FOUND")
    else:
        n_links = [(a.get_text(strip=True), a.get('href', '')) for a in nav.find_all('a')]
        print(f"NAV: FOUND ({len(n_links)} links)")
        missing_nav = []
        found_labels = [txt for txt, href in n_links]
        found_hrefs = [href for txt, href in n_links]
        for req, pattern in STD_NAV_REQUIRED:
            has_req = any(req.lower() in t.lower() for t in found_labels) or any(p[0] in h for h in found_hrefs for p in pattern)
            if not has_req:
                missing_nav.append(req)
        print("Nav links present:", n_links)
        print("Missing standard nav links:", missing_nav)

    # 4. TEXT
    # Prompt: "Check for typos, wrong token ticker (must be VRDX not VERDIS), wrong supply (must be 100B), wrong decimals (must be 9), any hardcoded/fake data, stale pricing, or broken links."
    
    # Check wrong ticker (using VERDIS as ticker symbol instead of VRDX, e.g. "100 VERDIS", "VERDIS Token", etc. Note: "Verdis Chain" or "Verdis" as brand name is fine, but ticker symbol must be VRDX).
    # Let's check for ticker symbol usage of VERDIS vs VRDX
    ticker_verdis_uses = re.findall(r'\b\d+\s*VERDIS\b|\$\s*VERDIS\b|VERDIS\s*token|VERDIS\s*ticker|symbol:\s*[\'"]?VERDIS[\'"]?|tokenSymbol\s*:\s*[\'"]?VERDIS[\'"]?', html, re.I)
    print("VERDIS ticker misuse:", ticker_verdis_uses)
    
    # Let's search for supply mentions (looking for 100B, 100 Billion, 100,000,000,000, or incorrect supply like 1B, 10B, 1Billion, etc.)
    supply_mentions = re.findall(r'.{0,40}(?:supply|total supply|max supply|100\s*b|billion|100,000,000,000).{0,40}', html, re.I)
    print("Supply mentions:", [s.strip().replace('\n', ' ') for s in supply_mentions[:5]])

    # Let's search for decimal mentions
    decimal_mentions = re.findall(r'.{0,40}(?:decimal|decimals|9 decimals|18 decimals).{0,40}', html, re.I)
    print("Decimal mentions:", [d.strip().replace('\n', ' ') for d in decimal_mentions[:5]])

    # Check for fake/hardcoded data / placeholder / stale prices
    fake_data_matches = re.findall(r'.{0,30}(?:lorem|fake|dummy|\$0\.\d+|\$1\.\d+|\$10\.\d+|hardcoded|mock|sample|0x1234|0x000|0xabcdef).{0,30}', html, re.I)
    print("Fake/hardcoded/stale data snippets (sample 5):", [f.strip().replace('\n', ' ') for f in fake_data_matches[:5]])

    # Broken links
    broken_links = [(a.get_text(strip=True), a.get('href')) for a in soup.find_all('a') if not a.get('href') or a.get('href') == '#' or a.get('href').startswith('javascript:')]
    print("Broken/placeholder links:", broken_links)

    # 5. DESIGN
    # Prompt: "Does the page use the gradient-ui-ux template? Check for the 3D floating UI cluster. Check for hardcoded colors. Check CSS variables --bg-1, --bg-2, --accent."
    
    # CSS variables
    has_bg1 = '--bg-1' in html
    has_bg2 = '--bg-2' in html
    has_accent = '--accent' in html
    
    # gradient-ui-ux template
    has_gradient_ui_ux = 'gradient-ui-ux' in html or 'gradient' in html.lower() or ('--bg-1' in html and '--bg-2' in html)
    
    # 3D floating UI cluster
    has_3d_cluster = any(k in html.lower() for k in ['floating-ui', 'ui-cluster', '3d-cluster', 'cluster-3d', 'floating-cluster', 'hero-3d', 'canvas', 'spline', 'three.js', 'perspective'])
    
    # Hardcoded colors
    # Check inside <style> tags or inline styles
    style_content = "\n".join([s.get_text() for s in soup.find_all('style')])
    inline_styles = "\n".join([e.get('style', '') for e in soup.find_all(True) if e.get('style')])
    css_text = style_content + "\n" + inline_styles
    hardcoded_hex = set(re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', css_text))
    
    print(f"DESIGN: CSS vars present: --bg-1: {has_bg1}, --bg-2: {has_bg2}, --accent: {has_accent}")
    print(f"DESIGN: gradient-ui-ux template reference: {has_gradient_ui_ux}")
    print(f"DESIGN: 3D floating UI cluster check: {has_3d_cluster}")
    print(f"DESIGN: Hardcoded hex colors count: {len(hardcoded_hex)} ({list(hardcoded_hex)[:5]})")
    print("\n")

for p, name in PAGES:
    analyze_one(p, name)
