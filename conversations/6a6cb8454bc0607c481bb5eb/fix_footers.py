#!/usr/bin/env python3
"""Fix all placeholder footer links across all Verdis pages."""

import re
import os

# What each footer link text maps to
LINK_MAP = {
    # Ecosystem column
    "Eco DEX": "/dashboard",
    "Carbon Market": "/markets",
    "Green Staking": "/dashboard",
    "Explorer": "/explorer",
    # Developers column
    "Documentation": "/api-docs",
    "Docs": "/api-docs",
    "GitHub Repos": "https://github.com/verdischain/Verdis",
    "GitHub Repo": "https://github.com/verdischain/Verdis",
    "Smart Contracts": "/templates",
    "Validator Setup": "/ecosystem",
    # Governance column
    "Green DAO": "/ecosystem",
    "Eco DAO Governance": "/ecosystem",
    "Eco DAO": "/ecosystem",
    "VRS Tokenomics": "/whitepaper",
    "Tokenomics": "/whitepaper",
    "Proposals": "/ecosystem",
    "Treasury Stats": "/status",
    "Bug Bounty Program": "/ecosystem",
    "Submit DApp Proposal": "/ecosystem",
    # Social
    "Twitter/X": "https://x.com/Verdischain",
    "Twitter / X": "https://x.com/Verdischain",
    "Discord Community": "https://discord.gg/verdis",
    "Discord": "https://discord.gg/verdis",
    "Telegram Group": "https://t.me/verdischain",
    "Telegram News": "https://t.me/verdischain",
    "Telegram": "https://t.me/verdischain",
    "GitHub": "https://github.com/verdischain/Verdis",
    "Governance Forum": "/ecosystem",
    "Security Audit": "/api-docs",
    "Buy VCO": "/token-sale",
    "Buy $VCO": "/token-sale",
    "Buy $VRS": "/token-sale",
    "Join IDO": "/token-sale",
}

def fix_file(filepath):
    if not os.path.exists(filepath):
        return 0
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    fixes = 0
    
    # 1. Fix <a href="#" ...>Text</a> with text content
    def replace_text_link(match):
        nonlocal fixes
        full = match.group(0)
        text = match.group(2).strip()
        
        if 'class="logo"' in full or 'class="brand-logo"' in full:
            return full
        if 'onclick' in full:
            return full
        
        if text in LINK_MAP:
            target = LINK_MAP[text]
            new_tag = full.replace('href="#"', f'href="{target}"')
            if target.startswith('http') and 'target=' not in new_tag:
                new_tag = new_tag.replace('<a ', '<a target="_blank" rel="noopener noreferrer" ', 1)
            fixes += 1
            return new_tag
        
        for key, val in LINK_MAP.items():
            if key.lower() == text.lower():
                new_tag = full.replace('href="#"', f'href="{val}"')
                if val.startswith('http') and 'target=' not in new_tag:
                    new_tag = new_tag.replace('<a ', '<a target="_blank" rel="noopener noreferrer" ', 1)
                fixes += 1
                return new_tag
        
        return full
    
    content = re.sub(r'(<a\s+href="#"[^>]*>)([^<]+)(</a>)', replace_text_link, content)
    
    # 2. Fix social links with title attr: <a href="#" class="social-link" title="X">
    def replace_social_link(match):
        nonlocal fixes
        full = match.group(0)
        title = match.group(1)
        
        title_map = {
            "Twitter/X": "https://x.com/Verdischain",
            "Discord": "https://discord.gg/verdis",
            "Telegram": "https://t.me/verdischain",
            "GitHub": "https://github.com/verdischain/Verdis",
            "Medium": "https://medium.com/@verdischain",
        }
        
        if title in title_map:
            target = title_map[title]
            new_tag = full.replace('href="#"', f'href="{target}"')
            if 'target=' not in new_tag:
                new_tag = new_tag.replace('<a ', '<a target="_blank" rel="noopener noreferrer" ', 1)
            fixes += 1
            return new_tag
        return full
    
    content = re.sub(
        r'(<a\s+href="#"[^>]*title="([^"]*)"[^>]*>.*?</a>)',
        replace_social_link,
        content,
        flags=re.DOTALL
    )
    
    # 3. Fix social links with icon classes: <a href="#" class="social-link"><i class="fa-brands fa-x-twitter"></i></a>
    def replace_icon_social(match):
        nonlocal fixes
        full = match.group(0)
        inner = match.group(2)
        
        icon_map = {
            "fa-x-twitter": "https://x.com/Verdischain",
            "fa-twitter": "https://x.com/Verdischain",
            "fa-discord": "https://discord.gg/verdis",
            "fa-telegram": "https://t.me/verdischain",
            "fa-github": "https://github.com/verdischain/Verdis",
            "fa-medium": "https://medium.com/@verdischain",
        }
        
        for icon, url in icon_map.items():
            if icon in inner:
                new_tag = full.replace('href="#"', f'href="{url}"')
                if 'target=' not in new_tag:
                    new_tag = new_tag.replace('<a ', '<a target="_blank" rel="noopener noreferrer" ', 1)
                fixes += 1
                return new_tag
        return full
    
    content = re.sub(
        r'(<a\s+href="#"[^>]*>)(<i\s+[^>]*>\s*</i>\s*</a>)',
        replace_icon_social,
        content
    )
    
    if fixes > 0:
        with open(filepath, 'w') as f:
            f.write(content)
    
    return fixes

pages = [
    "landing.html", "whitepaper.html", "ecosystem.html",
    "token-sale.html", "bridge.html", "markets.html",
    "dashboard.html", "explorer.html", "download.html",
    "status.html", "api-docs.html", "templates.html",
]

base = "/opt/verdis/app/dist/web"
total = 0
for page in pages:
    path = os.path.join(base, page)
    n = fix_file(path)
    if n > 0:
        print(f"  {page}: {n} links fixed")
        total += n
    else:
        print(f"  {page}: no placeholder links found")

print(f"\nTotal: {total} links fixed across all pages")
