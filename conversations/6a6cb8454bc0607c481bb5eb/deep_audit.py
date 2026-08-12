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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

for url in pages:
    path = urlparse(url).path or '/'
    req = urllib.request.Request(url, headers=headers)
    status_code = None
    html_content = ""
    
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            status_code = resp.getcode()
            html_content = resp.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        status_code = e.code
        try:
            html_content = e.read().decode('utf-8', errors='ignore')
        except:
            html_content = ""
    except Exception as e:
        status_code = "ERR"
        html_content = ""

    issues = []

    # 1. Status check
    if status_code != 200:
        issues.append(f"HTTP {status_code}")

    # 2. Logo check: grep for 'verdis-logo' or 'logo' in img tags
    # Let's inspect img tags specifically
    img_matches = re.findall(r'<img[^>]*>', html_content, re.IGNORECASE)
    has_logo_in_img = any('logo' in img.lower() or 'verdis-logo' in img.lower() for img in img_matches)
    # Also check svg or general logo mention
    has_logo_general = ('logo' in html_content.lower() or 'verdis-logo' in html_content.lower())
    has_logo = has_logo_in_img or has_logo_general

    # 3. Footer check: grep for 'footer' tag or class
    has_footer_tag = bool(re.search(r'<footer[^>]*>', html_content, re.IGNORECASE))
    has_footer_class = bool(re.search(r'class=["\'][^"\']*footer[^"\']*["\']', html_content, re.IGNORECASE))
    has_footer = has_footer_tag or has_footer_class

    # 4. Nav check: grep for 'nav' or navigation links
    has_nav_tag = bool(re.search(r'<nav[^>]*>', html_content, re.IGNORECASE))
    has_nav_class = bool(re.search(r'class=["\'][^"\']*(?:nav|navbar|navigation)[^"\']*["\']', html_content, re.IGNORECASE))
    has_nav = has_nav_tag or has_nav_class

    # 5. Gradient UI UX template check: grep for 'gradient' class names
    gradient_classes = re.findall(r'class=["\'][^"\']*\b(?:gradient|gradient-[a-zA-Z0-9_-]+)\b[^"\']*["\']', html_content, re.IGNORECASE)
    has_gradient = len(gradient_classes) > 0

    # 6. CSS variables check: check for --bg-1, --primary, etc.
    # Check in html or linked css files
    css_links = re.findall(r'<link[^>]+href=["\']([^"\']+\.css[^"\']*)["\']', html_content, re.IGNORECASE)
    css_links += re.findall(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']stylesheet["\']', html_content, re.IGNORECASE)
    
    combined_css = html_content
    for link in css_links:
        full_css_url = urljoin(url, link)
        try:
            c_req = urllib.request.Request(full_css_url, headers=headers)
            with urllib.request.urlopen(c_req, timeout=5, context=ctx) as c_resp:
                combined_css += "\n" + c_resp.read().decode('utf-8', errors='ignore')
        except:
            pass

    found_vars = []
    for var in ['--bg-1', '--primary', '--bg-2', '--accent', '--text-primary', '--border']:
        if var in combined_css:
            found_vars.append(var)

    has_css_vars = len(found_vars) > 0

    # 7. Check links on page for issues
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html_content)
    broken_links = []
    for href in set(hrefs):
        if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:'):
            continue
        full_url = urljoin(url, href)
        # Check if URL looks broken or returns 404
        if href.rstrip('/').endswith('-') or href.rstrip('/').endswith('github.com/Protremix/Verdischain-'):
            broken_links.append(f"Incomplete URL ({href})")
        elif full_url.startswith('https://verdischain.com'):
            # test internal page
            try:
                t_req = urllib.request.Request(full_url, headers=headers)
                with urllib.request.urlopen(t_req, timeout=5, context=ctx) as t_resp:
                    if t_resp.status >= 400:
                        broken_links.append(f"{href} ({t_resp.status})")
            except urllib.error.HTTPError as e:
                broken_links.append(f"{href} ({e.code})")
            except Exception as e:
                broken_links.append(f"{href} (error)")

    if not has_logo:
        issues.append("Missing logo")
    if not has_footer:
        issues.append("Missing footer")
    if not has_nav:
        issues.append("Missing nav")
    if not has_gradient:
        issues.append("Missing gradient classes")
    if not has_css_vars:
        issues.append("Missing CSS variables")
    if broken_links:
        issues.append("Broken links: " + ", ".join(broken_links))

    print(f"PAGE: {path}")
    print(f"  HTTP: {status_code}")
    print(f"  Logo: {'YES' if has_logo else 'NO'} ({has_logo_in_img=}, {has_logo_general=})")
    print(f"  Footer: {'YES' if has_footer else 'NO'} ({has_footer_tag=}, {has_footer_class=})")
    print(f"  Nav: {'YES' if has_nav else 'NO'} ({has_nav_tag=}, {has_nav_class=})")
    print(f"  Gradient: {'YES' if has_gradient else 'NO'} (found {len(gradient_classes)} matches)")
    print(f"  CSS vars: {'YES' if has_css_vars else 'NO'} (found: {found_vars})")
    print(f"  Issues: {', '.join(issues) if issues else 'None'}")
    print("-" * 50)

