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

for folder, name in PAGES:
    filepath = f"audit_pages/{folder}/index.html"
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    
    print(f"\n==================================================")
    print(f"ANALYSIS FOR PAGE: {folder} ({name})")
    print(f"==================================================")

    # 1. LOGO
    print("--- LOGO ---")
    logo_imgs = []
    all_imgs = soup.find_all('img')
    for img in all_imgs:
        src = img.get('src', '')
        alt = img.get('alt', '')
        cls = " ".join(img.get('class', []))
        id_ = img.get('id', '')
        # Check if in nav/header or logo class/src/alt
        parent = img.parent
        is_in_nav = False
        while parent:
            if parent.name in ['nav', 'header'] or 'nav' in parent.get('class', []) or 'brand' in parent.get('class', []):
                is_in_nav = True
                break
            parent = parent.parent
        if is_in_nav or 'logo' in src.lower() or 'logo' in alt.lower() or 'logo' in cls.lower() or 'brand' in cls.lower():
            logo_imgs.append((src, alt, cls, is_in_nav))
    
    print("Logo images found:", logo_imgs)

    # 2. NAV
    print("--- NAV ---")
    nav = soup.find('nav') or soup.find('header')
    if not nav:
        print("NAV: MISSING")
    else:
        nav_links = nav.find_all('a')
        nav_list = [(a.get_text(strip=True), a.get('href', '')) for a in nav_links]
        print(f"Nav links ({len(nav_list)}):", nav_list)
        # Check standard nav links
        missing_nav = []
        for label, hrefs in STD_NAV_REQUIRED:
            found = False
            for txt, href in nav_list:
                if label.lower() in txt.lower() or any(h.lower() == href.strip('/').lower() for h in hrefs):
                    found = True
                    break
            if not found:
                missing_nav.append(label)
        print("Missing required nav links:", missing_nav)

    # 3. FOOTER
    print("--- FOOTER ---")
    footer = soup.find('footer')
    if not footer:
        print("FOOTER: MISSING")
    else:
        footer_links = footer.find_all('a')
        footer_list = [(a.get_text(strip=True), a.get('href', '')) for a in footer_links]
        print(f"Footer links ({len(footer_list)}):", footer_list)
        missing_footer = []
        for label, hrefs in STD_FOOTER_REQUIRED:
            found = False
            for txt, href in footer_list:
                if label.lower() in txt.lower() or any(h.lower() in href.lower() for h in hrefs):
                    found = True
                    break
            if not found:
                missing_footer.append(label)
        print("Missing required footer links:", missing_footer)

    # 4. TEXT
    print("--- TEXT ---")
    # Check tickers
    # Note: search for standalone "VERDIS" as token ticker (e.g. "100 VERDIS", "VERDIS token", "VERDIS balance") vs "Verdis Chain" / "Verdis"
    # Search for regex: token ticker usage of VERDIS vs VRDX
    verdis_as_ticker = re.findall(r'\b\d+\s*VERDIS\b|\bVERDIS\s*token|\bVERDIS\s*balance|\bVERDIS/|\bVERDIS-|\bVERDIS\s*Price', html, re.IGNORECASE)
    print("VERDIS as ticker occurrences:", verdis_as_ticker)
    
    # Supply
    supplies = re.findall(r'\b\d+[\d,._]*\s*(?:Billion|B|M|Million)?\s*(?:VRDX|VERDIS|tokens|supply)?', html, re.IGNORECASE)
    # Filter interesting ones
    supply_matches = [s for s in supplies if any(k in s.lower() for k in ['100', 'billion', 'supply', 'total', 'cap']) and len(s) < 30]
    print("Supply matches:", supply_matches[:10])

    # Decimals
    decimal_matches = re.findall(r'.{0,30}decimal.{0,30}', html, re.IGNORECASE)
    print("Decimal mentions:", [d.strip() for d in decimal_matches])

    # Broken links or hardcoded/fake data
    dead_links = [a.get('href') for a in soup.find_all('a') if a.get('href') == '#' or a.get('href', '').startswith('javascript:')]
    print(f"Dead/Placeholder links count: {len(dead_links)}", dead_links[:5])

    # 5. DESIGN
    print("--- DESIGN ---")
    # CSS variables
    bg1 = '--bg-1' in html
    bg2 = '--bg-2' in html
    accent = '--accent' in html
    print(f"CSS vars: --bg-1: {bg1}, --bg-2: {bg2}, --accent: {accent}")

    # 3D floating UI cluster
    has_3d = any(k in html.lower() for k in ['floating-ui', 'ui-cluster', '3d', 'perspective', 'cube', 'sphere', 'spline', 'three.js', 'canvas-3d', 'hero-3d', 'floating-cards', 'cluster-container'])
    print("3D Cluster check:", has_3d)

    # Hardcoded colors check
    # Find hex codes in style tags or style attributes
    style_content = "".join([s.get_text() for s in soup.find_all('style')])
    inline_styles = "".join([e.get('style', '') for e in soup.find_all(True) if e.get('style')])
    all_styles = style_content + inline_styles
    hex_in_styles = set(re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', all_styles))
    print(f"Hardcoded hex colors count in styles: {len(hex_in_styles)} (Sample: {list(hex_in_styles)[:8]})")

