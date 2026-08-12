import urllib.request
import re
import ssl
from urllib.parse import urljoin, urlparse

pages = [
    ("https://verdischain.com/", "/"),
    ("https://verdischain.com/explorer/", "/explorer/"),
    ("https://verdischain.com/dex/", "/dex/"),
    ("https://verdischain.com/whitepaper/", "/whitepaper/"),
    ("https://verdischain.com/wallet/", "/wallet/"),
    ("https://verdischain.com/sale/", "/sale/"),
    ("https://verdischain.com/token/", "/token/"),
    ("https://verdischain.com/faucet/", "/faucet/"),
    ("https://verdischain.com/validators/", "/validators/"),
    ("https://verdischain.com/eco/", "/eco/"),
    ("https://verdischain.com/docs/", "/docs/"),
    ("https://verdischain.com/transactions/", "/transactions/"),
    ("https://verdischain.com/analytics/", "/analytics/"),
    ("https://verdischain.com/monitoring/", "/monitoring/"),
    ("https://verdischain.com/governance/", "/governance/"),
    ("https://verdischain.com/blog/", "/blog/")
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for full_url, path in pages:
    req = urllib.request.Request(full_url, headers=headers)
    status_code = None
    html = ""
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            status_code = resp.getcode()
            html = resp.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        status_code = e.code
        try:
            html = e.read().decode('utf-8', errors='ignore')
        except:
            html = ""
    except Exception as e:
        status_code = "ERR"

    issues = []

    if status_code != 200:
        issues.append(f"HTTP {status_code} Forbidden/Error")

    # 1. Logo check: grep for 'verdis-logo' or 'logo' in img tags
    img_tags = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
    has_logo = any(('verdis-logo' in img.lower() or 'logo' in img.lower()) for img in img_tags)
    logo_str = "YES" if has_logo else "NO"

    # 2. Footer check: grep for 'footer' tag or class
    has_footer = bool(re.search(r'<footer[^>]*>|class=["\'][^"\']*\bfooter\b[^"\']*["\']', html, re.IGNORECASE))
    footer_str = "YES" if has_footer else "NO"

    # 3. Nav check: grep for 'nav' tag, class, or id
    has_nav = bool(re.search(r'<nav[^>]*>|class=["\'][^"\']*\b(?:nav|navbar|navigation)\b[^"\']*["\']|id=["\'][^"\']*\bverdis-nav\b[^"\']*["\']', html, re.IGNORECASE))
    nav_str = "YES" if has_nav else "NO"

    # 4. Gradient template check: grep for 'gradient' class names
    has_gradient = bool(re.search(r'class=["\'][^"\']*\bgradient\b[^"\']*["\']', html, re.IGNORECASE))
    gradient_str = "YES" if has_gradient else "NO"

    # 5. CSS variables check: check for --bg-1, --primary, --accent, etc.
    styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    css_links = re.findall(r'href=["\']([^"\']+\.css[^"\']*)["\']', html)
    css_content = "".join(styles)
    for link in css_links:
        full_css_url = urljoin(full_url, link)
        try:
            c_req = urllib.request.Request(full_css_url, headers=headers)
            with urllib.request.urlopen(c_req, timeout=5, context=ctx) as c_resp:
                css_content += c_resp.read().decode('utf-8', errors='ignore')
        except:
            pass

    has_css_vars = ('--bg-1' in css_content) or ('--primary' in css_content) or ('--bg-primary' in css_content) or ('--accent' in css_content)
    css_vars_str = "YES" if has_css_vars else "NO"

    # Issues collation
    if status_code == 200:
        if not has_logo:
            issues.append("Missing img tag with logo/verdis-logo")
        if not has_footer:
            issues.append("Missing footer tag or class")
        if not has_nav:
            issues.append("Missing nav tag/class")
        if not has_gradient:
            issues.append("Missing 'gradient' class name")
        if not has_css_vars:
            issues.append("Missing CSS variables")

    # Broken link checks
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)
    for h in set(hrefs):
        if 'github.com/Protremix/Verdischain-' in h:
            issues.append("Broken link: https://github.com/Protremix/Verdischain- (truncated URL)")

    issues_str = "; ".join(issues) if issues else "None"

    print(f"PAGE: {path} | HTTP: {status_code} | Logo: {logo_str} | Footer: {footer_str} | Nav: {nav_str} | Gradient: {gradient_str} | CSS vars: {css_vars_str} | Issues: [{issues_str}]")

