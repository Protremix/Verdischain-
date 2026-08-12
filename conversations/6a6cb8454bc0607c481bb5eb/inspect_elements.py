import urllib.request
import re
import ssl

pages = [
    "https://verdischain.com/",
    "https://verdischain.com/explorer/",
    "https://verdischain.com/dex/",
    "https://verdischain.com/whitepaper/",
    "https://verdischain.com/wallet/",
    "https://verdischain.com/sale/",
    "https://verdischain.com/token/",
    "https://verdischain.com/faucet/",
    "https://verdischain.com/validators/",
    "https://verdischain.com/eco/",
    "https://verdischain.com/docs/",
    "https://verdischain.com/transactions/",
    "https://verdischain.com/analytics/",
    "https://verdischain.com/monitoring/",
    "https://verdischain.com/governance/",
    "https://verdischain.com/blog/"
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

for url in pages:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # Check img tags with verdis-logo or logo
            img_logos = re.findall(r'<img[^>]*?(?:verdis-logo|logo)[^>]*?>', html, re.IGNORECASE)
            
            # Check footer
            footers = re.findall(r'<footer[^>]*>.*?</footer>|class=["\'][^"\']*footer[^"\']*["\']', html, re.DOTALL | re.IGNORECASE)
            
            # Check nav
            navs = re.findall(r'<nav[^>]*>.*?</nav>|class=["\'][^"\']*(?:nav|navbar|navigation)[^"\']*["\']', html, re.DOTALL | re.IGNORECASE)

            # Check broken links or bad URLs on page
            hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)
            bad_hrefs = [h for h in hrefs if 'Protremix/Verdischain-' in h or h.endswith('404')]

            print(f"URL: {url}")
            print(f"  Img logos found: {len(img_logos)} -> {img_logos[:2]}")
            print(f"  Footer found: {bool(footers)}")
            print(f"  Nav found: {bool(navs)}")
            print(f"  Bad hrefs: {bad_hrefs}")
    except Exception as e:
        print(f"URL: {url} -> {e}")
