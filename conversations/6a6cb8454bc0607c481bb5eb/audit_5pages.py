#!/usr/bin/env python3
"""Thorough audit of 5 specific Verdis Chain pages."""
import requests, re, json

BASE = 'https://verdischain.com'
PAGES = ['/docs/', '/governance/', '/sale/', '/faucet/', '/eco/']

for page in PAGES:
    print(f'\n{"="*70}')
    print(f'PAGE: {page}')
    print(f'{"="*70}')
    
    try:
        r = requests.get(BASE + page, timeout=15)
        html = r.text
        print(f'HTTP Status: {r.status_code}')
        print(f'Page Size: {len(html)} bytes')
        
        # 1. Extract ALL links
        all_links = re.findall(r'href\s*=\s*["\']([^"\']+)["\']', html)
        internal = []
        external = []
        anchor = []
        for l in all_links:
            if l.startswith('#'):
                anchor.append(l)
            elif l.startswith('http'):
                external.append(l)
            elif l.startswith('/'):
                internal.append(l)
            elif l.startswith('mailto:') or l.startswith('tel:'):
                pass
            else:
                internal.append('/' + l)
        
        print(f'\nLINKS: {len(internal)} internal, {len(external)} external, {len(anchor)} anchors')
        
        # 2. Check internal links for 404
        broken_internal = []
        for l in set(internal):
            if l.startswith('/assets/') or l.startswith('/css/') or l.startswith('/js/'):
                continue
            try:
                lr = requests.get(BASE + l, timeout=5, allow_redirects=False)
                if lr.status_code in [404, 403]:
                    broken_internal.append(f'{l} -> HTTP {lr.status_code}')
            except:
                broken_internal.append(f'{l} -> timeout')
        
        if broken_internal:
            print(f'\nBROKEN INTERNAL LINKS ({len(broken_internal)}):')
            for b in broken_internal:
                print(f'  X {b}')
        else:
            print('\nInternal links: All OK')
        
        # 3. Check external links
        broken_external = []
        for l in set(external):
            if 'verdischain.com' in l:
                continue
            try:
                lr = requests.head(l, timeout=5, allow_redirects=True)
                if lr.status_code >= 400:
                    broken_external.append(f'{l} -> HTTP {lr.status_code}')
            except:
                broken_external.append(f'{l} -> unreachable')
        
        if broken_external:
            print(f'\nBROKEN EXTERNAL LINKS ({len(broken_external)}):')
            for b in broken_external:
                print(f'  X {b}')
        else:
            print('External links: All OK')
        
        # 4. Check for JS issues
        js_issues = []
        # Check for undefined variables
        if 'undefined' in html and 'function' not in html:
            js_issues.append('possible undefined reference')
        # Check for missing script src
        scripts = re.findall(r'<script[^>]*src\s*=\s*["\']([^"\']+)["\']', html)
        for s in scripts:
            if not s.startswith('http'):
                try:
                    sr = requests.get(BASE + s, timeout=5)
                    if sr.status_code != 200:
                        js_issues.append(f'script {s} -> HTTP {sr.status_code}')
                except:
                    js_issues.append(f'script {s} -> timeout')
        # Check for inline JS errors
        if 'catch(e){}' in html or 'catch(e) {}' in html:
            pass  # Normal error handling
        
        if js_issues:
            print(f'\nJS ISSUES ({len(js_issues)}):')
            for j in js_issues:
                print(f'  ! {j}')
        else:
            print('JS scripts: All loaded OK')
        
        # 5. Check CSS
        css_links = re.findall(r'<link[^>]*href\s*=\s*["\']([^"\']*\.css[^"\']*)["\']', html)
        css_issues = []
        for c in css_links:
            if not c.startswith('http'):
                try:
                    cr = requests.get(BASE + c, timeout=5)
                    if cr.status_code != 200:
                        css_issues.append(f'{c} -> HTTP {cr.status_code}')
                except:
                    css_issues.append(f'{c} -> timeout')
        if css_issues:
            print(f'\nCSS ISSUES ({len(css_issues)}):')
            for c in css_issues:
                print(f'  ! {c}')
        else:
            print('CSS: All loaded OK')
        
        # 6. Check images
        img_srcs = re.findall(r'<img[^>]*src\s*=\s*["\']([^"\']+)["\']', html)
        broken_imgs = []
        for img in set(img_srcs):
            if img.startswith('data:'):
                continue
            url = img if img.startswith('http') else BASE + img
            try:
                ir = requests.head(url, timeout=5)
                if ir.status_code >= 400:
                    broken_imgs.append(f'{img} -> HTTP {ir.status_code}')
            except:
                broken_imgs.append(f'{img} -> timeout')
        if broken_imgs:
            print(f'\nBROKEN IMAGES ({len(broken_imgs)}):')
            for b in broken_imgs:
                print(f'  X {b}')
        else:
            print(f'Images: All OK ({len(img_srcs)} images)')
        
        # 7. Check design elements
        print('\nDESIGN CHECK:')
        has_nav = bool(re.search(r'<nav|id\s*=\s*["\']verdis-nav|std-nav', html, re.I))
        has_footer = bool(re.search(r'<footer|class\s*=\s*["\'].*footer', html, re.I))
        has_logo = bool(re.search(r'logo.*\.(?:png|svg|jpg|webp)|verdis-anim-logo|verdis-splash-logo', html, re.I))
        has_3d = any(p in html for p in ['hero-visual', 'float-card', 'hero-circle', 'floating-cluster', 'float-3d-card', 'hero-3d-cluster'])
        has_meta_desc = bool(re.search(r'<meta\s+name\s*=\s*["\']description["\']', html, re.I))
        has_og_tags = bool(re.search(r'<meta\s+property\s*=\s*["\']og:', html, re.I))
        has_title = bool(re.search(r'<title>', html))
        has_viewport = bool(re.search(r'<meta\s+name\s*=\s*["\']viewport', html))
        has_responsive = bool(re.search(r'@media\s*\(\s*max-width', html))
        
        print(f'  Nav: {"YES" if has_nav else "NO"}')
        print(f'  Footer: {"YES" if has_footer else "NO"}')
        print(f'  Logo: {"YES" if has_logo else "NO"}')
        print(f'  3D Floating: {"YES" if has_3d else "NO"}')
        print(f'  Meta description: {"YES" if has_meta_desc else "NO"}')
        print(f'  OG tags: {"YES" if has_og_tags else "NO"}')
        print(f'  Title: {"YES" if has_title else "NO"}')
        print(f'  Viewport: {"YES" if has_viewport else "NO"}')
        print(f'  Responsive CSS: {"YES" if has_responsive else "NO"}')
        
        # 8. Check for hardcoded/fake data
        print('\nDATA CHECK:')
        fake_issues = []
        if '32,400,000' in html or '$32.4M' in html:
            fake_issues.append('Hardcoded $32.4M TVL')
        if '1,847' in html or '1847' in html:
            fake_issues.append('Fake faucet count 1847')
        if '526,000' in html or '526000' in html:
            fake_issues.append('Fake tree count 526,000')
        
        # Check for TODO/FIXME/HACK
        todos = re.findall(r'(?:TODO|FIXME|HACK|XXX|TEMP|PLACEHOLDER)', html, re.I)
        if todos:
            fake_issues.append(f'{len(todos)} TODO/FIXME markers')
        
        # Check for console.log
        console_logs = re.findall(r'console\.log', html)
        if console_logs:
            fake_issues.append(f'{len(console_logs)} console.log statements')
        
        # Check for hardcoded addresses
        hardcoded_addrs = re.findall(r'5[A-HJ-NP-Za-km-z1-9]{44,}', html)
        if hardcoded_addrs:
            fake_issues.append(f'{len(hardcoded_addrs)} hardcoded addresses')
        
        if fake_issues:
            print(f'  ISSUES:')
            for f in fake_issues:
                print(f'    ! {f}')
        else:
            print('  No fake data detected')
        
        # 9. Check for accessibility
        print('\nACCESSIBILITY:')
        has_alt = len(re.findall(r'<img[^>]*alt\s*=', html))
        has_no_alt = len(re.findall(r'<img(?![^>]*alt)[^>]*>', html))
        has_aria = len(re.findall(r'aria-', html))
        has_role = len(re.findall(r'\brole\s*=', html))
        has_lang = bool(re.search(r'<html[^>]*lang\s*=', html))
        print(f'  Images with alt: {has_alt}')
        print(f'  Images without alt: {has_no_alt}')
        print(f'  ARIA attributes: {has_aria}')
        print(f'  Role attributes: {has_role}')
        print(f'  HTML lang attribute: {"YES" if has_lang else "NO"}')
        
        # 10. Check for duplicate content
        print('\nCONTENT ISSUES:')
        # Duplicate nav links
        nav_links = re.findall(r'<a[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>([^<]+)</a>', html)
        nav_hrefs = [l[0] for l in nav_links]
        duplicates = [l for l in set(nav_hrefs) if nav_hrefs.count(l) > 2]
        if duplicates:
            print(f'  Links appearing >2 times: {duplicates}')
        else:
            print('  No duplicate links')
        
        # Check for empty sections
        empty_divs = len(re.findall(r'<div[^>]*>\s*</div>', html))
        if empty_divs > 5:
            print(f'  {empty_divs} empty divs (may indicate missing content)')
        
    except Exception as e:
        print(f'ERROR: {e}')

print(f'\n{"="*70}')
print('AUDIT COMPLETE')
print(f'{"="*70}')
