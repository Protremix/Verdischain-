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
        issues.append(f"HTTP {status_code}")

    # 1. Logo image in <img ...> tags specifically: grep for 'verdis-logo' or 'logo' in img tags
    img_tags = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
    has_logo_img = any(('verdis-logo' in img.lower() or 'logo' in img.lower()) for img in img_tags)
    logo_str = "YES" if has_logo_img else "NO"
    if not has_logo_img and status_code == 200:
        issues.append("No logo image tag")

    # 2. Footer: grep for 'footer' tag or class
    has_footer_tag = bool(re.search(r'<footer[^>]*>', html, re.IGNORECASE))
    has_footer_class = bool(re.search(r'class=["\'][^"\']*\bfooter\b[^"\']*["\']', html, re.IGNORECASE))
    has_footer = has_footer_tag or has_footer_class
    footer_str = "YES" if has_footer else "NO"
    if not has_footer and status_code == 200:
        issues.append("No footer element")

    # 3. Nav: grep for 'nav' tag, class, or navigation links
    has_nav_tag = bool(re.search(r'<nav[^>]*>', html, re.IGNORECASE))
    has_nav_class = bool(re.search(r'class=["\'][^"\']*\b(?:nav|navbar|navigation)\b[^"\']*["\']', html, re.IGNORECASE))
    has_nav_id = bool(re.search(r'id=["\'][^"\']*\b(?:nav|verdis-nav)\b[^"\']*["\']', html, re.IGNORECASE))
    has_nav = has_nav_tag or has_nav_class or has_nav_id
    nav_str = "YES" if has_nav else "NO"
    if not has_nav and status_code == 200:
        issues.append("No navigation")

    # 4. Gradient UI UX template: grep for 'gradient' class names
    has_gradient_class = bool(re.search(r'class=["\'][^"\']*\bgradient\b[^"\']*["\']', html, re.IGNORECASE))
    gradient_str = "YES" if has_gradient_class else "NO"
    if not has_gradient_class and status_code == 200:
        issues.append("Missing 'gradient' class name from gradient-ui-ux template")

    # 5. CSS variables: check for --bg-1, --primary, etc.
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
    if not has_css_vars and status_code == 200:
        issues.append("Missing CSS variables")

    # 6. Broken links: check href values
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)
    broken_hrefs = []
    for h in set(hrefs):
        if h == 'https://github.com/Protremix/Verdischain-':
            broken_hrefs.append(f"Incomplete URL: {h}")

    if broken_hrefs:
        issues.append("; ".join(broken_hrefs))

    issues_str = ", ".join(issues) if issues else "None"

    print(f"PAGE: {path} | HTTP: {status_code} | Logo: {logo_str} | Footer: {footer_str} | Nav: {nav_str} | Gradient: {gradient_str} | CSS vars: {css_vars_str} | Issues: {issues_str}")

