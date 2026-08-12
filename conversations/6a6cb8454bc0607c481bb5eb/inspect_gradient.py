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
            # find all class attributes containing 'gradient' or 'bg-' or template markers
            classes = re.findall(r'class=["\']([^"\']+)["\']', html)
            gradient_cls = [c for c in classes if 'gradient' in c.lower()]
            print(f"{url} -> {gradient_cls}")
    except Exception as e:
        print(f"{url} -> Error {e}")
