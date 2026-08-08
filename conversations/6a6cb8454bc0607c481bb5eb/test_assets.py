import urllib.request
import urllib.error
import ssl
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open("/tmp/sale_page.html", "r") as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

assets = []
for tag in soup.find_all(['img', 'link', 'script']):
    src = tag.get('src') or tag.get('href')
    if src and not src.startswith('data:') and not src.startswith('https://fonts.'):
        if src.startswith('/'):
            src = "https://verdischain.com" + src
        assets.append((tag.name, src))

print(f"Testing {len(assets)} assets...")
for name, url in set(assets):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        print(f"[{resp.status}] {name} -> {url}")
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] BROKEN ASSET: {name} -> {url}")
    except Exception as e:
        print(f"[ERR] FAILED: {name} -> {url} ({e})")
