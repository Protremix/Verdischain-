#!/usr/bin/env python3
"""Remove old duplicate footers from pages that have both old and new footers."""
import os
import re

BASE = "/var/www/verdiscan"

# Pages to check for duplicate footers
PAGES = [
    ("Wallet", "wallet/index.html"),
    ("Docs", "docs/index.html"),
    ("Contact", "contact/index.html"),
    ("Landing", "index.html"),
    ("DEX", "dex/index.html"),
    ("Validators", "validators/index.html"),
    ("Eco", "eco/index.html"),
    ("Faucet", "faucet/index.html"),
    ("Sale", "sale/index.html"),
    ("Referral", "referral/index.html"),
    ("Incentives", "incentives/index.html"),
    ("Whitepaper", "whitepaper/index.html"),
    ("API", "api/index.html"),
]

for name, path in PAGES:
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        continue
    
    with open(full, 'r', errors='replace') as f:
        content = f.read()
    
    original = content
    
    # Find all <footer> tags - there should be exactly one (the standard one)
    footer_matches = list(re.finditer(r'<footer[^>]*>.*?</footer>', content, re.DOTALL | re.IGNORECASE))
    
    # Also check for <div class="footer"> that aren't the standard footer
    div_footer_matches = list(re.finditer(r'<div\s+class="footer"[^>]*>.*?</div>', content, re.DOTALL | re.IGNORECASE))
    
    # If we have a <footer> tag AND a <div class="footer">, remove the div one
    if footer_matches and div_footer_matches:
        # Remove all <div class="footer"> blocks (keep only <footer> ones)
        for match in reversed(div_footer_matches):
            # Check if this is NOT the standard footer (which uses <footer> not <div>)
            block = match.group(0)
            if 'footer-links' not in block or '<footer' not in block:
                content = content[:match.start()] + content[match.end():]
    
    # If there are multiple <footer> tags, keep only the last one (standard)
    if len(footer_matches) > 1:
        # Keep the last footer, remove the others
        for match in reversed(footer_matches[:-1]):
            content = content[:match.start()] + content[match.end():]
    
    # Also remove any standalone footer-like divs that contain "© 2026" but aren't the standard footer
    # Pattern: <div class="...footer..."> ... © 2026 ... </div> that doesn't have footer-links
    standalone_footers = re.findall(r'<div[^>]*class="[^"]*footer[^"]*"[^>]*>(.*?)</div>', content, re.DOTALL | re.IGNORECASE)
    for sf in standalone_footers:
        if '© 2026' in sf and 'footer-links' not in sf and 'footer-copy' not in sf:
            # This is an old footer div - remove it
            full_block = re.search(r'<div[^>]*class="[^"]*footer[^"]*"[^>]*>' + re.escape(sf) + r'</div>', content, re.DOTALL | re.IGNORECASE)
            if full_block:
                content = content[:full_block.start()] + content[full_block.end():]
    
    # Clean up multiple consecutive blank lines left behind
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    if content != original:
        with open(full, 'w') as f:
            f.write(content)
        print(f"  {name}: removed duplicate old footer")
    else:
        print(f"  {name}: no duplicates")
