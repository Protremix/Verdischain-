#!/usr/bin/env python3
"""
Comprehensive link fix for Verdis website.
- Fixes broken external links (GitHub, Discord, Medium)
- Fixes broken internal links (/wallet.html -> /wallet, missing PDFs)
- Adds consistent footer to all pages
- Fixes navigation inconsistencies
"""

import os
import re

WEB_DIR = "/opt/verdis/app/dist/web"

# Standard footer HTML (consistent across all pages)
FOOTER_HTML = '''<footer style="background:#080d0b;border-top:1px solid #1a2a20;padding:40px 20px 20px;margin-top:40px;">
  <div style="max-width:1200px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:30px;">
    <div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
        <span style="color:#10B981;font-weight:bold;font-size:1.3rem;">VERDIS</span>
      </div>
      <p style="color:#5a7a6a;font-size:0.85rem;line-height:1.6;max-width:280px;">The world's first fully green, carbon-negative blockchain ecosystem. Built on DPoS consensus with native carbon credits and reforestation tracking.</p>
    </div>
    <div>
      <h4 style="color:#10B981;font-size:0.8rem;text-transform:uppercase;margin-bottom:12px;letter-spacing:1px;">Ecosystem</h4>
      <a href="/dashboard" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">Dashboard</a>
      <a href="/explorer" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">Explorer</a>
      <a href="/wallet" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">Web Wallet</a>
      <a href="/staking" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">Staking</a>
      <a href="/markets" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">Markets</a>
    </div>
    <div>
      <h4 style="color:#10B981;font-size:0.8rem;text-transform:uppercase;margin-bottom:12px;letter-spacing:1px;">Resources</h4>
      <a href="/whitepaper" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">Whitepaper</a>
      <a href="/team" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">Team</a>
      <a href="/download" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">Download App</a>
      <a href="/api-docs" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">API Docs</a>
      <a href="/token-sale" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">Token Sale</a>
    </div>
    <div>
      <h4 style="color:#10B981;font-size:0.8rem;text-transform:uppercase;margin-bottom:12px;letter-spacing:1px;">Community</h4>
      <a href="https://x.com/Verdischain" target="_blank" rel="noopener" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">X / Twitter</a>
      <a href="https://t.me/verdischain" target="_blank" rel="noopener" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">Telegram</a>
      <a href="https://github.com/verdischain" target="_blank" rel="noopener" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">GitHub</a>
      <a href="/status" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">Network Status</a>
      <a href="/ecosystem" style="display:block;color:#7a9a8a;font-size:0.85rem;margin-bottom:8px;text-decoration:none;">Ecosystem</a>
    </div>
  </div>
  <div style="max-width:1200px;margin:30px auto 0;padding-top:20px;border-top:1px solid #1a2a20;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
    <p style="color:#4a6a5a;font-size:0.78rem;">&copy; 2026 Verdis Chain. All rights reserved.</p>
    <p style="color:#4a6a5a;font-size:0.78rem;">Chain 909 &middot; DPoS &middot; Carbon-Negative</p>
  </div>
</footer>'''

# Social link replacements (fix all variations)
SOCIAL_FIXES = [
    # GitHub fixes
    (r'https://github\.com/verdis-chain', 'https://github.com/verdischain'),
    (r'https://github\.com["\x27>]', 'https://github.com/verdischain'),
    (r'https://github\.comverdischain', 'https://github.com/verdischain'),
    # Discord - remove generic discord.com, keep discord.gg/verdis
    (r'https://discord\.com["\x27> ]', 'https://t.me/verdischain'),
    # Medium - remove, replace with Telegram
    (r'https://medium\.com/@verdischain', 'https://t.me/verdischain'),
    # verdis-tokenomics.pdf -> verdis-whitepaper.pdf
    (r'/verdis-tokenomics\.pdf', '/verdis-whitepaper.pdf'),
    # wallet.html -> /wallet
    (r'/wallet\.html', '/wallet'),
    # explorer.html -> /explorer
    (r'/explorer\.html', '/explorer'),
    # dashboard.html#bridge -> /bridge
    (r'dashboard\.html#bridge', '/bridge'),
]

# Pages that need footer added (no <footer> tag exists)
PAGES_NEEDING_FOOTER = [
    "api-docs.html",
    "code.html", 
    "competitive-analysis.html",
    "explorer.html",
    "ssh-terminal.html",
    "status.html",
    "templates.html",
    "trust-connect.html",
    "wallet.html",
    "audit-report.html",
]

def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    original = content
    changes = []
    
    # Apply social/external link fixes
    for pattern, replacement in SOCIAL_FIXES:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes.append(f"Fixed {pattern} -> {replacement}")
    
    # Check if page has a proper footer
    has_footer = bool(re.search(r"<footer", content, re.IGNORECASE))
    
    if not has_footer and os.path.basename(filepath) in PAGES_NEEDING_FOOTER:
        # Find </body> and insert footer before it
        body_close = content.rfind("</body>")
        if body_close >= 0:
            content = content[:body_close] + FOOTER_HTML + "\n" + content[body_close:]
            changes.append("Added footer")
        else:
            # No </body> tag, append at end
            content = content + "\n" + FOOTER_HTML
            changes.append("Appended footer (no </body> found)")
    
    # Also fix the Telegram bot link in footers - replace with main channel
    if "t.me/Verdis_official_bot" in content:
        content = content.replace("https://t.me/Verdis_official_bot", "https://t.me/verdischain")
        changes.append("Fixed Telegram bot -> main channel")
    
    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return changes
    return None

# Process all HTML files
all_changes = {}
for filename in sorted(os.listdir(WEB_DIR)):
    if not filename.endswith(".html"):
        continue
    filepath = os.path.join(WEB_DIR, filename)
    changes = fix_file(filepath)
    if changes:
        all_changes[filename] = changes
        print(f"[FIXED] {filename}:")
        for c in changes:
            print(f"  - {c}")
    else:
        print(f"[OK] {filename}")

print(f"\n=== SUMMARY ===")
print(f"Files modified: {len(all_changes)}")
print(f"Files unchanged: {len([f for f in os.listdir(WEB_DIR) if f.endswith('.html')]) - len(all_changes)}")
