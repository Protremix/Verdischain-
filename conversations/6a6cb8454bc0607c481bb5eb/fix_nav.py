#!/usr/bin/env python3
"""Standardize navigation across all Verdis Chain pages."""
import re, os

WEB_ROOT = "/var/www/verdiscan"

STANDARD_NAV_CSS = """
/* STANDARD NAV */
nav.std-nav { position: sticky; top: 0; z-index: 1000; background: rgba(10,10,10,0.85); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1px solid #222; padding: 0 24px; height: 64px; display: flex; align-items: center; justify-content: space-between; }
nav.std-nav .nav-brand { display: flex; align-items: center; gap: 10px; text-decoration: none; color: #e8e8e8; }
nav.std-nav .nav-brand .logo { width: 32px; height: 32px; background: #caff33; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #000; font-size: 16px; }
nav.std-nav .nav-brand span { font-weight: 600; font-size: 16px; }
nav.std-nav .nav-links { display: flex; gap: 4px; flex-wrap: wrap; }
nav.std-nav .nav-links a { color: #888; text-decoration: none; padding: 8px 12px; border-radius: 8px; font-size: 13px; font-weight: 500; transition: all .2s; }
nav.std-nav .nav-links a:hover, nav.std-nav .nav-links a.active { color: #caff33; background: #141414; }
nav.std-nav .nav-status { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #888; }
nav.std-nav .nav-status .dot { width: 8px; height: 8px; border-radius: 50%; background: #4ade80; box-shadow: 0 0 8px #4ade80; animation: std-pulse 2s infinite; }
@keyframes std-pulse { 0%,100% { opacity: 1; } 50% { opacity: .5; } }
@media (max-width: 768px) { nav.std-nav .nav-links { display: none; } nav.std-nav .nav-brand span { font-size: 14px; } }
"""

def make_nav(active=None):
    links = [
        ("/", "Home"),
        ("/explorer/", "Explorer"),
        ("/dex/", "DEX"),
        ("/validators/", "Validators"),
        ("/eco/", "Eco"),
        ("/faucet/", "Faucet"),
        ("/wallet/", "Wallet"),
        ("/sale/", "Sale"),
        ("/docs/", "Docs"),
    ]
    link_html = ""
    for href, label in links:
        cls = ' class="active"' if href.strip("/") == (active or "") else ""
        link_html += f'<a href="{href}"{cls}>{label}</a>\n    '
    return f'''<nav class="std-nav">
  <a href="/" class="nav-brand"><div class="logo">V</div><span>Verdis Chain</span></a>
  <div class="nav-links">
    {link_html}
  </div>
  <div class="nav-status"><div class="dot"></div><span class="nav-text">Connected</span></div>
</nav>'''

PAGES = {
    "index.html": "/",
    "explorer/index.html": "explorer",
    "dex/index.html": "dex",
    "wallet/index.html": "wallet",
    "faucet/index.html": "faucet",
    "sale/index.html": "sale",
    "referral/index.html": "",
    "incentives/index.html": "",
    "docs/index.html": "docs",
}

for filename, active in PAGES.items():
    filepath = os.path.join(WEB_ROOT, filename)
    if not os.path.exists(filepath):
        print(f"  SKIP {filename} (not found)")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    new_nav = make_nav(active)
    
    if filename == "index.html":
        content = re.sub(r'<nav class="hero-nav">.*?</nav>', new_nav, content, flags=re.DOTALL)
    else:
        content = re.sub(r'<nav[^>]*>.*?</nav>', new_nav, content, count=1, flags=re.DOTALL)
    
    if 'std-nav' not in content:
        if '</style>' in content:
            content = content.replace('</style>', STANDARD_NAV_CSS + '\n</style>', 1)
        elif '<style>' in content:
            content = content.replace('<style>', '<style>\n' + STANDARD_NAV_CSS, 1)
        else:
            content = content.replace('</head>', f'<style>{STANDARD_NAV_CSS}</style>\n</head>', 1)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  FIXED {filename}")
    else:
        print(f"  NO CHANGE {filename}")

print("\nNav standardization complete!")
