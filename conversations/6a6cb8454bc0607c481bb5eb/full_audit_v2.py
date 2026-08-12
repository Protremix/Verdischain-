#!/usr/bin/env python3
"""Full audit: check every page, every link, every element properly."""
import requests, re, sys

BASE = 'https://verdischain.com'

pages = [
    '/', '/explorer/', '/dex/', '/whitepaper/', '/wallet/', '/sale/',
    '/tokenomics/', '/faucet/', '/validators/', '/eco/',
    '/docs/', '/transactions/', '/analytics/', '/monitoring/', '/governance/',
    '/blog/', '/developers/', '/download/', '/referral/', '/incentives/',
    '/contact/', '/privacy/', '/terms/', '/cookies/', '/security/',
    '/disclaimer/', '/status/', '/api/',
]

# 7 main pages that MUST have 3D floating cluster
MAIN_PAGES = ['/', '/explorer/', '/dex/', '/whitepaper/', '/validators/', '/eco/', '/docs/']

# All known 3D floating element class names across different page templates
THREE_D_PATTERNS = [
    'hero-visual', 'float-card', 'hero-circle', 'hero-canvas',  # explorer/validators style
    'floating-cluster', 'floating-card-main', 'floating-badge',  # DEX style
    'float-3d-card', 'hero-3d-cluster',  # docs style
    'verdis-splash-logo', 'verdis-anim-logo',  # blog/developers style
]

all_issues = []

for page in pages:
    try:
        r = requests.get(BASE + page, timeout=10, allow_redirects=False)
        status = r.status_code
        
        if status in [301, 302]:
            print(f'{page:25s} -> HTTP {status} (redirect)')
            continue
        
        if status != 200:
            all_issues.append(f'{page}: HTTP {status}')
            print(f'{page:25s} -> HTTP {status} FAIL')
            continue
        
        html = r.text
        issues = []
        
        # 1. Logo check (PNG, SVG, or nav-logo)
        has_logo = bool(re.search(r'src\s*=\s*["\'][^"\']*(?:logo|brand)[^"\']*["\']', html, re.I))
        has_svg_logo = bool(re.search(r'verdis-anim-logo|verdis-splash-logo|nav-logo.*img', html, re.I))
        if not has_logo and not has_svg_logo:
            issues.append('NO LOGO')
        
        # 2. Footer check
        has_footer = bool(re.search(r'<footer|class\s*=\s*["\'].*footer', html, re.I))
        if not has_footer:
            issues.append('NO FOOTER')
        
        # 3. Nav check
        has_nav = bool(re.search(r'<nav|id\s*=\s*["\']verdis-nav', html, re.I))
        if not has_nav:
            issues.append('NO NAV')
        
        # 4. 3D floating cluster check (for main pages only)
        if page in MAIN_PAGES:
            has_3d = any(p in html for p in THREE_D_PATTERNS)
            if not has_3d:
                issues.append('MISSING 3D TEMPLATE')
        
        # 5. Check for hardcoded fake data
        if page == '/dex/' and ('$32,400,000' in html or '32,400,000' in html):
            issues.append('HARDCODED TVL $32.4M')
        if page == '/faucet/' and ('1,847' in html or '1847' in html):
            issues.append('FAKE FAUCET COUNT')
        if page == '/eco/' and ('526,000' in html or '526000' in html):
            issues.append('FAKE ECO TREES')
        
        if issues:
            print(f'{page:25s} -> HTTP {status} FAIL: {", ".join(issues)}')
            for issue in issues:
                all_issues.append(f'{page}: {issue}')
        else:
            print(f'{page:25s} -> HTTP {status} OK')
            
    except Exception as e:
        print(f'{page:25s} -> ERROR: {e}')
        all_issues.append(f'{page}: {e}')

# Check ALL internal links
print(f'\n=== LINK CHECK ===')
all_links = set()
for page in pages:
    try:
        r = requests.get(BASE + page, timeout=10)
        for match in re.finditer(r'href\s*=\s*["\']([^"\']+)["\']', r.text):
            l = match.group(1)
            if l.startswith('/') and not l.startswith('/assets/') and not l.startswith('/css/') and not l.startswith('/js/') and not l.startswith('/rpc') and not l.startswith('/api/') and l != '/':
                all_links.add(l)
    except:
        pass

broken = []
for link in sorted(all_links):
    try:
        lr = requests.get(BASE + link, timeout=5, allow_redirects=False)
        if lr.status_code == 404:
            broken.append(f'{link} -> 404')
    except:
        broken.append(f'{link} -> timeout')

if broken:
    for b in broken:
        print(f'  BROKEN: {b}')
        all_issues.append(f'BROKEN LINK: {b}')
else:
    print(f'All {len(all_links)} internal links OK')

print(f'\n{"="*60}')
print(f'TOTAL ISSUES: {len(all_issues)}')
if all_issues:
    for issue in all_issues:
        print(f'  FAIL: {issue}')
else:
    print('ALL PAGES PASS')
