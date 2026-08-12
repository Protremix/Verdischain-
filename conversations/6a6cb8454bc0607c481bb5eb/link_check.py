#!/usr/bin/env python3
"""Check all internal links on all pages for 404s."""
import requests, re

BASE = 'https://verdischain.com'
pages = ['/', '/explorer/', '/dex/', '/whitepaper/', '/wallet/', '/sale/',
    '/tokenomics/', '/faucet/', '/validators/', '/eco/',
    '/docs/', '/transactions/', '/analytics/', '/monitoring/', '/governance/',
    '/blog/', '/developers/', '/download/', '/referral/', '/incentives/',
    '/contact/', '/privacy/', '/terms/', '/cookies/', '/security/',
    '/disclaimer/', '/status/', '/api/']

all_links = set()
for page in pages:
    try:
        r = requests.get(BASE + page, timeout=10)
        html = r.text
        # Find all href links
        for match in re.finditer(r'href\s*=\s*["\']([^"\']+)["\']', html):
            l = match.group(1)
            if l.startswith('/') and not l.startswith('/assets/') and not l.startswith('/css/') and not l.startswith('/js/') and not l.startswith('/rpc') and not l.startswith('/api/') and l != '/':
                all_links.add(l)
    except Exception as e:
        print(f'ERROR fetching {page}: {e}')

print(f'Total unique internal links found: {len(all_links)}')
broken = []
for link in sorted(all_links):
    try:
        lr = requests.get(BASE + link, timeout=5, allow_redirects=False)
        if lr.status_code == 404:
            broken.append(f'{link} -> 404')
    except:
        broken.append(f'{link} -> timeout')

if broken:
    print(f'BROKEN LINKS ({len(broken)}):')
    for b in broken:
        print(f'  {b}')
else:
    print('All internal links OK (no 404s)')

# Also check for hardcoded fake data
print('\n=== CHECKING FOR HARDCODED/FAKE DATA ===')
faucet = requests.get(BASE + '/faucet/', timeout=10).text
if '1,847' in faucet or '1847' in faucet:
    print('  FAUCET: still has fake 1847 claim count')
else:
    print('  FAUCET: OK (no fake count)')

eco = requests.get(BASE + '/eco/', timeout=10).text
if '526,000' in eco or '526000' in eco:
    print('  ECO: still has fake 526,000 trees')
else:
    print('  ECO: OK (no fake tree count)')

dex = requests.get(BASE + '/dex/', timeout=10).text
if '$32,400,000' in dex or '32,400,000' in dex:
    print('  DEX: still has hardcoded $32.4M TVL')
elif '$32' in dex and 'M' in dex:
    # Check more carefully
    import re as re2
    hardcoded_tvl = re2.search(r'[\$]?\d{2,3}[,.]?\d{3,6}\s*(?:USD|M\b)', dex)
    if hardcoded_tvl:
        print(f'  DEX: possible hardcoded TVL: {hardcoded_tvl.group()}')
    else:
        print('  DEX: OK')
else:
    print('  DEX: OK (no hardcoded TVL)')
