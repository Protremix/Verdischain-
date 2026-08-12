import urllib.request
import re
import ssl
from urllib.parse import urljoin

pages = [
    "https://verdischain.com/",
    "https://verdischain.com/explorer/",
    "https://verdischain.com/dex/",
    "https://verdischain.com/whitepaper/",
    "https://verdischain.com/wallet/",
    "https://verdischain.com/sale/",
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

checked_links = {}

for p in pages:
    req = urllib.request.Request(p, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)
            for h in set(hrefs):
                if h.startswith('#') or h.startswith('javascript:') or h.startswith('mailto:'):
                    continue
                full_url = urljoin(p, h)
                if full_url not in checked_links:
                    try:
                        c_req = urllib.request.Request(full_url, headers=headers, method='HEAD')
                        with urllib.request.urlopen(c_req, timeout=5, context=ctx) as c_resp:
                            checked_links[full_url] = c_resp.status
                    except urllib.error.HTTPError as e:
                        if e.code == 405: # try GET
                            try:
                                g_req = urllib.request.Request(full_url, headers=headers)
                                with urllib.request.urlopen(g_req, timeout=5, context=ctx) as g_resp:
                                    checked_links[full_url] = g_resp.status
                            except urllib.error.HTTPError as e2:
                                checked_links[full_url] = e2.code
                            except Exception as ex:
                                checked_links[full_url] = f"ERR: {ex}"
                        else:
                            checked_links[full_url] = e.code
                    except Exception as ex:
                        checked_links[full_url] = f"ERR: {ex}"
                
                status = checked_links[full_url]
                if status not in (200, 301, 302, 303, 307, 308):
                    print(f"Page {p} -> Broken link: {h} (Status: {status})")
    except Exception as e:
        print(f"Error fetching page {p}: {e}")

