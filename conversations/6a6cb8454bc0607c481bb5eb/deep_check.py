import re
import os
import urllib.request
import urllib.parse

files = {
    '/developers/': 'html_dumps/developers.html',
    '/download/': 'html_dumps/download.html',
    '/referral/': 'html_dumps/referral.html',
    '/incentives/': 'html_dumps/incentives.html',
    '/partners/': 'html_dumps/partners_error.html',
    '/roadmap/': 'html_dumps/roadmap_error.html',
    '/community/': 'html_dumps/community_error.html',
    '/staking/': 'html_dumps/staking_error.html',
    '/bridge/': 'html_dumps/bridge_error.html',
    '/nft/': 'html_dumps/nft_error.html',
    '/launchpad/': 'html_dumps/launchpad_error.html',
    '/api/': 'html_dumps/api.html',
    '/status/': 'html_dumps/status.html',
    '/support/': 'html_dumps/support_error.html',
    '/privacy/': 'html_dumps/privacy.html',
    '/terms/': 'html_dumps/terms.html'
}

for path, filepath in files.items():
    print(f"\n=================== {path} ===================")
    if 'error' in filepath:
        print("HTTP: 404 Not Found")
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Status
    print("HTTP: 200 OK")

    # 2. Logo
    img_tags = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
    logo_imgs = [img for img in img_tags if 'verdis-logo' in img.lower() or 'logo' in img.lower()]
    print(f"All <img> tags ({len(img_tags)}): {img_tags}")
    print(f"Logo <img> tags ({len(logo_imgs)}): {logo_imgs}")

    # 3. Footer
    footer_tags = re.findall(r'<footer[^>]*>.*?</footer>', html, re.IGNORECASE | re.DOTALL)
    footer_classes = re.findall(r'class="[^"]*footer[^"]*"', html, re.IGNORECASE)
    print(f"Footer tags: {len(footer_tags)}, Footer classes: {len(footer_classes)}")

    # 4. Nav
    nav_tags = re.findall(r'<nav[^>]*>.*?</nav>', html, re.IGNORECASE | re.DOTALL)
    nav_classes = re.findall(r'class="[^"]*nav[^"]*"', html, re.IGNORECASE)
    nav_links = re.findall(r'<a[^>]*href=["\'][^"\']+["\'][^>]*>.*?</a>', html, re.IGNORECASE)
    print(f"Nav tags: {len(nav_tags)}, Nav classes: {len(nav_classes)}")

    # 5. Gradient UI/UX
    gradient_in_classes = re.findall(r'class=["\'][^"\']*gradient[^"\']*["\']', html, re.IGNORECASE)
    gradient_in_html = re.findall(r'gradient', html, re.IGNORECASE)
    print(f"Gradient class matches: {gradient_in_classes}")
    print(f"Total 'gradient' word occurrences: {len(gradient_in_html)}")

    # 6. CSS variables
    bg1 = '--bg-1' in html
    primary = '--primary' in html
    all_vars = set(re.findall(r'--[a-zA-Z0-9_-]+', html))
    print(f"Has --bg-1: {bg1}, Has --primary: {primary}")
    print(f"All CSS vars in HTML ({len(all_vars)}): {sorted(list(all_vars))[:10]}")

    # Check external CSS stylesheets
    css_links = re.findall(r'<link[^>]+href=["\']([^"\']+\.css[^"\']*)["\']', html, re.IGNORECASE)
    print(f"Linked CSS files: {css_links}")
    for css_rel in css_links:
        css_url = urllib.parse.urljoin(f"https://verdischain.com{path}", css_rel)
        try:
            req = urllib.request.Request(css_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as res:
                css_text = res.read().decode('utf-8', errors='ignore')
                c_bg1 = '--bg-1' in css_text
                c_primary = '--primary' in css_text
                c_vars = set(re.findall(r'--[a-zA-Z0-9_-]+', css_text))
                print(f"  CSS {css_rel} -> --bg-1: {c_bg1}, --primary: {c_primary}, total vars: {len(c_vars)}")
                if len(c_vars) > 0:
                    print(f"  Sample CSS vars: {sorted(list(c_vars))[:10]}")
        except Exception as e:
            print(f"  CSS {css_rel} fetch failed: {e}")

