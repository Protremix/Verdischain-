import urllib.request
import re
import ssl
from urllib.parse import urljoin, urlparse

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

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def check_link(url):
    req = urllib.request.Request(url, headers=headers, method='HEAD')
    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        if e.code == 405: # Method Not Allowed for HEAD, try GET
            try:
                req_get = urllib.request.Request(url, headers=headers, method='GET')
                with urllib.request.urlopen(req_get, timeout=5, context=ctx) as resp_get:
                    return resp_get.status
            except urllib.error.HTTPError as e2:
                return e2.code
            except Exception:
                return "ERR"
        return e.code
    except Exception:
        return "ERR"

link_cache = {}

for url in pages:
    path = urlparse(url).path or '/'
    req = urllib.request.Request(url, headers=headers)
    status_code = None
    html_content = ""
    issues = []
    
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            status_code = response.getcode()
            raw = response.read()
            html_content = raw.decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        status_code = e.code
        try:
            html_content = e.read().decode('utf-8', errors='ignore')
        except:
            html_content = ""
    except Exception as e:
        status_code = "ERR"
        issues.append(f"Fetch failed ({str(e)})")

    if status_code != 200 and status_code != "ERR":
        issues.append(f"HTTP status {status_code}")

    # Check 1: Logo image (grep for 'verdis-logo' or 'logo' in img tags or svg/src)
    # Check img tags specifically for verdis-logo or logo
    img_tags = re.findall(r'<img[^>]+>', html_content, re.IGNORECASE)
    has_logo = False
    for img in img_tags:
        if 'verdis-logo' in img.lower() or 'logo' in img.lower():
            has_logo = True
            break
    if not has_logo:
        # Check svg or header logo references
        if 'verdis-logo' in html_content.lower() or 'logo.png' in html_content.lower() or 'logo.svg' in html_content.lower():
            has_logo = True

    # Check 2: Footer (grep for 'footer' tag or class)
    has_footer = bool(re.search(r'<footer|\bfooter\b', html_content, re.IGNORECASE))

    # Check 3: Nav (grep for 'nav' or navigation links)
    has_nav = bool(re.search(r'<nav|\bnav\b|\bnavbar\b|\bnavigation\b', html_content, re.IGNORECASE))

    # Check 4: Gradient UI UX template (grep for 'gradient' class names)
    has_gradient = bool(re.search(r'class=["\'][^"\']*\bgradient[^\s"\']*', html_content, re.IGNORECASE))

    # Check 5: CSS variables (--bg-1, --primary, etc.)
    # Check html content or linked css files
    css_files = re.findall(r'href=["\']([^"\']+\.css[^"\']*)["\']', html_content, re.IGNORECASE)
    css_content_combined = html_content
    for css_href in css_files:
        css_url = urljoin(url, css_href)
        if css_url not in link_cache:
            try:
                c_req = urllib.request.Request(css_url, headers=headers)
                with urllib.request.urlopen(c_req, timeout=5, context=ctx) as c_res:
                    link_cache[css_url] = c_res.read().decode('utf-8', errors='ignore')
            except Exception:
                link_cache[css_url] = ""
        css_content_combined += "\n" + link_cache[css_url]

    has_css_vars = ('--bg-1' in css_content_combined) or ('--primary' in css_content_combined) or ('--bg-' in css_content_combined) or ('--text-' in css_content_combined) or ('--accent' in css_content_combined)

    # Check missing items as issues
    if not has_logo:
        issues.append("Missing logo image")
    if not has_footer:
        issues.append("Missing footer")
    if not has_nav:
        issues.append("Missing navigation")
    if not has_gradient:
        issues.append("Missing gradient class names")
    if not has_css_vars:
        issues.append("Missing CSS variables (--bg-1, --primary)")

    # Check 6: Broken links in hrefs on the page
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html_content)
    broken_hrefs = []
    for h in set(hrefs):
        if h.startswith('#') or h.startswith('javascript:') or h.startswith('mailto:') or h.startswith('tel:'):
            continue
        full_href = urljoin(url, h)
        # Check domain - focus on internal links or all links
        if full_href not in link_cache:
            st = check_link(full_href)
            link_cache[full_href] = st
        else:
            st = link_cache[full_href]
        
        if st not in (200, 301, 302, 303, 307, 308):
            broken_hrefs.append(f"{h} ({st})")

    if broken_hrefs:
        issues.append(f"Broken links: {', '.join(broken_hrefs[:5])}" + (f" (+{len(broken_hrefs)-5} more)" if len(broken_hrefs)>5 else ""))

    logo_str = "YES" if has_logo else "NO"
    footer_str = "YES" if has_footer else "NO"
    nav_str = "YES" if has_nav else "NO"
    gradient_str = "YES" if has_gradient else "NO"
    css_str = "YES" if has_css_vars else "NO"
    issues_str = ", ".join(issues) if issues else "None"

    print(f"PAGE: {path} | HTTP: {status_code} | Logo: {logo_str} | Footer: {footer_str} | Nav: {nav_str} | Gradient: {gradient_str} | CSS vars: {css_str} | Issues: {issues_str}")

