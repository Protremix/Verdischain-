#!/usr/bin/env python3
"""
Fix navigation and footer across all Verdis Chain pages.
Top nav: Verdiscan, DEX, Whitepaper, Wallet, Sale, Tokenomics, Faucet
Footer: All other links + the nav links too
"""
import re
import os

PAGES = [
    "index.html",
    "explorer/index.html",
    "dex/index.html",
    "wallet/index.html",
    "sale/index.html",
    "faucet/index.html",
    "validators/index.html",
    "eco/index.html",
    "whitepaper/index.html",
    "docs/index.html",
    "contact/index.html",
    "incentives/index.html",
    "referral/index.html",
    "tokenomics/index.html",
]

# New nav links (top navigation only)
NAV_LINKS = [
    ("/explorer/", "Verdiscan"),
    ("/dex/", "DEX"),
    ("/whitepaper/", "Whitepaper"),
    ("/wallet/", "Wallet"),
    ("/sale/", "Sale"),
    ("/tokenomics/", "Tokenomics"),
    ("/faucet/", "Faucet"),
]

# Footer links (comprehensive - includes everything)
FOOTER_LINKS = [
    ("/", "Home"),
    ("/explorer/", "Verdiscan"),
    ("/dex/", "DEX"),
    ("/whitepaper/", "Whitepaper"),
    ("/wallet/", "Wallet"),
    ("/sale/", "Sale"),
    ("/tokenomics/", "Tokenomics"),
    ("/faucet/", "Faucet"),
    ("/validators/", "Validators"),
    ("/eco/", "Eco"),
    ("/referral/", "Referral"),
    ("/incentives/", "Incentives"),
    ("/contact/", "Contact"),
    ("/api/", "API"),
    ("/docs/", "Docs"),
    ("https://github.com/Protremix/Verdischain-", "GitHub"),
]

# Map page path to its nav href for active class
PAGE_NAV_MAP = {
    "index.html": "/",
    "explorer/index.html": "/explorer/",
    "dex/index.html": "/dex/",
    "wallet/index.html": "/wallet/",
    "sale/index.html": "/sale/",
    "faucet/index.html": "/faucet/",
    "validators/index.html": "/validators/",
    "eco/index.html": "/eco/",
    "whitepaper/index.html": "/whitepaper/",
    "docs/index.html": "/docs/",
    "contact/index.html": "/contact/",
    "incentives/index.html": "/incentives/",
    "referral/index.html": "/referral/",
    "tokenomics/index.html": "/tokenomics/",
}

def build_nav_links_html(page_path):
    """Build the nav links HTML for a specific page."""
    current_href = PAGE_NAV_MAP.get(page_path, "")
    links = []
    for href, label in NAV_LINKS:
        active_class = ' class="active"' if href == current_href else ""
        links.append(f'<a href="{href}"{active_class}>{label}</a>')
    return "\n      ".join(links)

def build_footer_links_html():
    """Build the footer links HTML."""
    links = []
    for href, label in FOOTER_LINKS:
        if href.startswith("http"):
            links.append(f'<a href="{href}" target="_blank">{label}</a>')
        else:
            links.append(f'<a href="{href}">{label}</a>')
    return "\n    ".join(links)

def fix_nav(content, page_path):
    """Replace nav links in the content."""
    new_nav_html = build_nav_links_html(page_path)
    
    # Pattern 1: <div class="nav-links">...</div> (landing page)
    pattern1 = r'(<div class="nav-links">\s*)(.*?)(\s*</div>)'
    
    # Pattern 2: <div class="nav-links" id="navLinks">...</div> (subpages)
    pattern2 = r'(<div class="nav-links" id="navLinks">\s*)(.*?)(\s*</div>)'
    
    changed = False
    
    def replacer(m):
        nonlocal changed
        changed = True
        prefix = m.group(1)
        suffix = m.group(3)
        return f"{prefix}{new_nav_html}{suffix}"
    
    # Try pattern 2 first (more specific)
    new_content = re.sub(pattern2, replacer, content, flags=re.DOTALL)
    if not changed:
        new_content = re.sub(pattern1, replacer, content, flags=re.DOTALL)
    
    if not changed:
        print(f"  WARN: Could not find nav-links div in {page_path}")
        return content
    
    return new_content

def fix_footer(content, page_path):
    """Replace footer links in the content."""
    new_footer_html = build_footer_links_html()
    
    # Pattern: <div class="footer-links">...</div>
    pattern = r'(<div class="footer-links">\s*)(.*?)(\s*</div>)'
    
    changed = False
    
    def replacer(m):
        nonlocal changed
        changed = True
        prefix = m.group(1)
        suffix = m.group(3)
        return f"{prefix}{new_footer_html}{suffix}"
    
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    if not changed:
        print(f"  WARN: Could not find footer-links div in {page_path}")
        return content
    
    return new_content

def main():
    base = "/var/www/verdiscan"
    for page_path in PAGES:
        full_path = os.path.join(base, page_path)
        if not os.path.exists(full_path):
            print(f"SKIP: {page_path} (not found)")
            continue
        
        with open(full_path) as f:
            content = f.read()
        
        original = content
        
        # Fix nav
        content = fix_nav(content, page_path)
        
        # Fix footer
        content = fix_footer(content, page_path)
        
        if content != original:
            with open(full_path, 'w') as f:
                f.write(content)
            print(f"FIXED: {page_path}")
        else:
            print(f"NO CHANGE: {page_path}")

if __name__ == "__main__":
    main()
