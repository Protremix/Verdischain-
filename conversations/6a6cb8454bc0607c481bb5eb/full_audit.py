#!/usr/bin/env python3
"""Full audit: fetch every page, check every link, every element."""
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

all_issues = []

for page in pages:
    try:
        r = requests.get(BASE + page, timeout=10, allow_redirects=False)
        status = r.status_code
        
        if status in [301, 302]:
            loc = r.headers.get('Location', '?')
            print(f'{page:25s} -> HTTP {status} (redirect to {loc})')
            continue
        
        if status != 200:
            all_issues.append(f'{page}: HTTP {status}')
            print(f'{page:25s} -> HTTP {status} BROKEN')
            continue
        
        html = r.text
        issues = []
        
        # 1. Logo check
        has_logo = bool(re.search(r'src\s*=\s*["\'][^"\']*logo[^"\']*["\']', html, re.I))
        has_svg_logo = bool(re.search(r'verdis-anim-logo|verdis-splash-logo', html, re.I))
        has_nav_logo = bool(re.search(r'nav-logo.*img|nav-brand.*img', html, re.I))
        if not has_logo and not has_svg_logo and not has_nav_logo:
            issues.append('NO LOGO')
        
        # 2. Footer check
        has_footer = bool(re.search(r'<footer|class\s*=\s*["\'].*footer', html, re.I))
        if not has_footer:
            issues.append('NO FOOTER')
        
        # 3. Nav check
        has_nav = bool(re.search(r'<nav|id\s*=\s*["\']verdis-nav', html, re.I))
        if not has_nav:
            issues.append('NO NAV')
        
        # 4. Check ALL internal links for 404
        links = re.findall(r'href\s*=\s*["\']([^"\']+)["\']', html)
        internal_links = set()
        for l in links:
            if l.startswith('/') and not l.startswith('/assets/') and not l.startswith('/css/') and not l.startswith('/js/') and l != '/' and not l.startswith('/rpc') and not l.startswith('/api/'):
                internal_links.add(l)
        
        broken_links = []
        for link in internal_links:
            try:
                lr = requests.get(BASE + link, timeout=5, allow_redirects=False)
                if lr.status_code == 404:
                    broken_links.append(link)
            except:
                broken_links.append(f'{link} (timeout)')
        
        if broken_links:
            issues.append('BROKEN LINKS: ' + ', '.join(broken_links))
        
        # 5. Check token ticker
        # Look for "VERDIS" used as a token symbol (not just brand name)
        token_verdis = re.search(r'(?:token|symbol|ticker|coin)\s*(?:symbol)?\s*[:=]\s*VERDIS\b', html, re.I)
        if token_verdis and 'VRDX' not in html:
            issues.append('WRONG TICKER')
        
        # 6. Check for empty/missing content
        if len(html) < 1000:
            issues.append(f'PAGE TOO SHORT ({len(html)} bytes)')
        
        # 7. Check for JS errors — look for common patterns
        if 'innerHTML' in html and 'escapeHtml' not in html and 'escape' not in html:
            # Check if innerHTML is used with external data (potential XSS)
            pass
        
        # 8. Check for the gradient-ui-ux template on 7 main pages
        main_pages = ['/', '/explorer/', '/dex/', '/whitepaper/', '/validators/', '/eco/', '/docs/']
        if page in main_pages:
            has_3d = bool(re.search(r'hero-visual|float-card|hero-circle', html, re.I))
            if not has_3d:
                issues.append('MISSING 3D TEMPLATE')
        
        if issues:
            status_str = ' | '.join(issues)
            print(f'{page:25s} -> HTTP {status} FAIL: {status_str}')
            for issue in issues:
                all_issues.append(f'{page}: {issue}')
        else:
            print(f'{page:25s} -> HTTP {status} OK')
            
    except Exception as e:
        print(f'{page:25s} -> ERROR: {e}')
        all_issues.append(f'{page}: EXCEPTION {e}')

print(f'\n{"="*60}')
print(f'TOTAL ISSUES: {len(all_issues)}')
for issue in all_issues:
    print(f'  FAIL: {issue}')
