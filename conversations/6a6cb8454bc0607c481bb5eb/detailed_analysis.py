import re
import os
import glob
import urllib.request
import urllib.parse

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AuditBot/1.0'}

pages_info = [
    ("/developers/", "developers.html"),
    ("/download/", "download.html"),
    ("/referral/", "referral.html"),
    ("/incentives/", "incentives.html"),
    ("/partners/", "partners_error.html"),
    ("/roadmap/", "roadmap_error.html"),
    ("/community/", "community_error.html"),
    ("/staking/", "staking_error.html"),
    ("/bridge/", "bridge_error.html"),
    ("/nft/", "nft_error.html"),
    ("/launchpad/", "launchpad_error.html"),
    ("/api/", "api.html"),
    ("/status/", "status.html"),
    ("/support/", "support_error.html"),
    ("/privacy/", "privacy.html"),
    ("/terms/", "terms.html")
]

link_cache = {}

def check_url_status(url):
    if url in link_cache:
        return link_cache[url]
    try:
        req = urllib.request.Request(url, headers=headers, method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as res:
            link_cache[url] = res.getcode()
            return res.getcode()
    except urllib.error.HTTPError as e:
        if e.code == 405: # Method Not Allowed for HEAD, try GET
            try:
                req = urllib.request.Request(url, headers=headers, method='GET')
                with urllib.request.urlopen(req, timeout=5) as res:
                    link_cache[url] = res.getcode()
                    return res.getcode()
            except urllib.error.HTTPError as e2:
                link_cache[url] = e2.code
                return e2.code
            except Exception as e2:
                link_cache[url] = f"ERR: {e2}"
                return f"ERR: {e2}"
        link_cache[url] = e.code
        return e.code
    except Exception as e:
        link_cache[url] = f"ERR: {e}"
        return f"ERR: {e}"

for path, filename in pages_info:
    filepath = os.path.join("html_dumps", filename)
    print("==================================================")
    print(f"PATH: {path}")
    if not os.path.exists(filepath):
        print("File not found -> HTTP: 404")
        continue
    
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Status
    is_404 = "error.html" in filename or "404" in html[:500]
    http_status = 404 if is_404 else 200

    if http_status == 404:
        print(f"HTTP: 404 | Page not found")
        continue

    # 2. Logo image: grep for 'verdis-logo' or 'logo' in img tags
    # Let's find all <img> tags
    img_tags = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
    logo_imgs = [img for img in img_tags if 'verdis-logo' in img.lower() or 'logo' in img.lower()]
    has_logo = len(logo_imgs) > 0

    # Also check inline svg or class/id if img not found
    svg_logo = re.findall(r'<svg[^>]*class="[^"]*logo[^"]*"[^>]*>', html, re.IGNORECASE)
    
    # 3. Footer: grep for 'footer' tag or class
    footer_match = re.findall(r'<footer[^>]*>|class="[^"]*footer[^"]*"|id="footer"', html, re.IGNORECASE)
    has_footer = len(footer_match) > 0

    # 4. Nav: grep for 'nav' or navigation links
    nav_match = re.findall(r'<nav[^>]*>|class="[^"]*nav[^"]*"|id="nav"|<header[^>]*>', html, re.IGNORECASE)
    has_nav = len(nav_match) > 0

    # 5. Gradient: grep for 'gradient' class names
    gradient_matches = re.findall(r'class="[^"]*gradient[^"]*"', html, re.IGNORECASE)
    # Also check any class attribute containing 'gradient'
    all_classes = re.findall(r'class=["\']([^"\']+)["\']', html)
    gradient_classes = [c for c in all_classes if 'gradient' in c.lower()]
    has_gradient = len(gradient_classes) > 0

    # 6. CSS variables: check for --bg-1, --primary, etc.
    # Check in HTML directly or link stylesheets
    css_vars = re.findall(r'--[a-zA-Z0-9_-]+:', html)
    # Check specifically for --bg-1, --primary
    has_bg1 = '--bg-1' in html
    has_primary = '--primary' in html
    
    # Also check linked CSS files
    css_links = re.findall(r'<link[^>]+href=["\']([^"\']+\.css[^"\']*)["\']', html, re.IGNORECASE)
    linked_vars = []
    for css_rel in css_links:
        css_url = urllib.parse.urljoin(f"https://verdischain.com{path}", css_rel)
        try:
            req = urllib.request.Request(css_url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as c_res:
                c_text = c_res.read().decode('utf-8', errors='ignore')
                if '--bg-1' in c_text:
                    has_bg1 = True
                if '--primary' in c_text:
                    has_primary = True
                vars_found = re.findall(r'--[a-zA-Z0-9_-]+:', c_text)
                linked_vars.extend(vars_found)
        except Exception as e:
            print(f"  CSS fetch error ({css_url}): {e}")

    has_css_vars = has_bg1 or has_primary or len(css_vars) > 0 or len(linked_vars) > 0

    # 7. Check href values / broken links
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    page_broken_links = []
    for href in set(hrefs):
        href_strip = href.strip()
        if not href_strip or href_strip == '#':
            page_broken_links.append(f"Empty/hash href ('{href}')")
            continue
        if href_strip.startswith(('javascript:', 'mailto:', 'tel:')):
            continue
        full_url = urllib.parse.urljoin(f"https://verdischain.com{path}", href_strip)
        # test URL status
        st = check_url_status(full_url)
        if st != 200 and st != 301 and st != 302:
            page_broken_links.append(f"{href_strip} -> HTTP {st}")

    print(f"  HTTP: {http_status}")
    print(f"  Logo Imgs found: {logo_imgs}")
    print(f"  Has Logo: {has_logo}")
    print(f"  Has Footer: {has_footer} (matches: {footer_match[:2]})")
    print(f"  Has Nav: {has_nav} (matches: {nav_match[:2]})")
    print(f"  Gradient classes: {gradient_classes}")
    print(f"  Has Gradient: {has_gradient}")
    print(f"  Has --bg-1: {has_bg1}, Has --primary: {has_primary}")
    print(f"  Has CSS vars: {has_css_vars}")
    print(f"  Hrefs count: {len(hrefs)}")
    print(f"  Broken links: {page_broken_links}")

