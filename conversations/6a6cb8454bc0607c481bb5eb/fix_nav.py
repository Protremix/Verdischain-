#!/usr/bin/env python3
"""
Comprehensive navigation fix for all Verdis pages:
1. Add nav bars to pages missing them (team, audit-report)
2. Fix dashboard.html#dex -> /dashboard#dex in markets.html
3. Fix canonical/meta URLs with .html extensions
4. Add nav links to pages with incomplete nav (token-sale, whitepaper, templates)
"""

import re

# Standard nav bar HTML (matching existing dark theme)
NAV_BAR = '''<nav style="position:sticky;top:0;z-index:100;background:rgba(5,10,8,0.85);backdrop-filter:blur(20px);border-bottom:1px solid rgba(0,255,136,0.1);padding:0 24px;display:flex;align-items:center;gap:20px;height:60px;">
  <a href="/" style="display:inline-flex;align-items:center;gap:8px;text-decoration:none;">
    <object data="/verdis-logo-nav.svg" type="image/svg+xml" width="28" height="28" style="flex-shrink:0;pointer-events:none;"></object>
    <span style="font-weight:700;font-size:1.05rem;color:#e0e0e0;letter-spacing:0.5px;">VERDIS</span>
  </a>
  <div style="display:flex;gap:0;margin-left:8px;">
    <a href="/dashboard" style="color:#8ba898;font-size:0.85rem;font-weight:500;padding:8px 14px;border-radius:8px;text-decoration:none;transition:all 0.15s;" onmouseover="this.style.background='rgba(0,255,136,0.08)';this.style.color='#00ff88'" onmouseout="this.style.background='transparent';this.style.color='#8ba898'">Dashboard</a>
    <a href="/explorer" style="color:#8ba898;font-size:0.85rem;font-weight:500;padding:8px 14px;border-radius:8px;text-decoration:none;transition:all 0.15s;" onmouseover="this.style.background='rgba(0,255,136,0.08)';this.style.color='#00ff88'" onmouseout="this.style.background='transparent';this.style.color='#8ba898'">Explorer</a>
    <a href="/wallet" style="color:#8ba898;font-size:0.85rem;font-weight:500;padding:8px 14px;border-radius:8px;text-decoration:none;transition:all 0.15s;" onmouseover="this.style.background='rgba(0,255,136,0.08)';this.style.color='#00ff88'" onmouseout="this.style.background='transparent';this.style.color='#8ba898'">Wallet</a>
    <a href="/token-sale" style="color:#8ba898;font-size:0.85rem;font-weight:500;padding:8px 14px;border-radius:8px;text-decoration:none;transition:all 0.15s;" onmouseover="this.style.background='rgba(0,255,136,0.08)';this.style.color='#00ff88'" onmouseout="this.style.background='transparent';this.style.color='#8ba898'">Buy VRDX</a>
    <a href="/whitepaper" style="color:#8ba898;font-size:0.85rem;font-weight:500;padding:8px 14px;border-radius:8px;text-decoration:none;transition:all 0.15s;" onmouseover="this.style.background='rgba(0,255,136,0.08)';this.style.color='#00ff88'" onmouseout="this.style.background='transparent';this.style.color='#8ba898'">Whitepaper</a>
  </div>
  <a href="/token-sale" style="margin-left:auto;display:inline-flex;align-items:center;gap:6px;padding:8px 16px;background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:8px;color:#00ff88;font-size:0.85rem;font-weight:600;text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,136,0.2)'" onmouseout="this.style.background='rgba(0,255,136,0.1)'">Buy VRDX</a>
</nav>'''

BASE = "/opt/verdis/app/dist/web"
changes = []

# === FIX 1: Add nav bar to team.html ===
with open(f"{BASE}/team.html") as f:
    content = f.read()

# team.html has <body> then some divs, then <div class="container"> with <a href="/whitepaper" class="nav-back">
# Add nav bar right after <body>
if '<nav style="position:sticky;top:0' not in content:
    # Insert after <body> tag
    content = content.replace('<body>', '<body>\n' + NAV_BAR, 1)
    with open(f"{BASE}/team.html", "w") as f:
        f.write(content)
    changes.append("Added nav bar to team.html")

# === FIX 2: Add nav bar to audit-report.html ===
with open(f"{BASE}/audit-report.html") as f:
    content = f.read()

if '<nav style="position:sticky;top:0' not in content:
    content = content.replace('<body>', '<body>\n' + NAV_BAR, 1)
    with open(f"{BASE}/audit-report.html", "w") as f:
        f.write(content)
    changes.append("Added nav bar to audit-report.html")

# === FIX 3: Fix dashboard.html#dex -> /dashboard#dex in markets.html ===
with open(f"{BASE}/markets.html") as f:
    content = f.read()

count = content.count('dashboard.html#dex')
content = content.replace('dashboard.html#dex', '/dashboard#dex')
with open(f"{BASE}/markets.html", "w") as f:
    f.write(content)
if count > 0:
    changes.append(f"Fixed {count} dashboard.html#dex -> /dashboard#dex in markets.html")

# === FIX 4: Fix canonical/meta URLs with .html extensions ===
meta_fixes = {
    "dashboard.html": ("https://verdischain.com/dashboard.html", "https://verdischain.com/dashboard"),
    "ssh-terminal.html": ("https://verdischain.com/ssh-terminal.html", "https://verdischain.com/ssh-terminal"),
    "status.html": ("https://verdischain.com/status.html", "https://verdischain.com/status"),
    "templates.html": ("https://verdischain.com/templates.html", "https://verdischain.com/templates"),
    "whitepaper.html": ("https://verdischain.com/whitepaper.html", "https://verdischain.com/whitepaper"),
}

for filename, (old_url, new_url) in meta_fixes.items():
    filepath = f"{BASE}/{filename}"
    with open(filepath) as f:
        content = f.read()
    count = content.count(old_url)
    if count > 0:
        content = content.replace(old_url, new_url)
        with open(filepath, "w") as f:
            f.write(content)
        changes.append(f"Fixed {count} canonical/meta URLs in {filename}: {old_url} -> {new_url}")

# === FIX 5: Add more nav links to token-sale.html ===
with open(f"{BASE}/token-sale.html") as f:
    content = f.read()

# token-sale nav has: Home, Stats, Buy VRDX, Tokenomics, Vesting, Why Invest, FAQ, Whitepaper, Dashboard
# It's missing: Explorer, Wallet
# Find the nav links and add Explorer and Wallet
old_ts_nav = '<a href="/whitepaper">Whitepaper</a><a href="/dashboard">Dashboard</a>'
new_ts_nav = '<a href="/whitepaper">Whitepaper</a><a href="/explorer">Explorer</a><a href="/wallet">Wallet</a><a href="/dashboard">Dashboard</a>'
if old_ts_nav in content:
    content = content.replace(old_ts_nav, new_ts_nav)
    with open(f"{BASE}/token-sale.html", "w") as f:
        f.write(content)
    changes.append("Added Explorer and Wallet links to token-sale.html nav")
else:
    # Try alternative format
    old_ts_nav2 = '<a href="/whitepaper">Whitepaper</a>\n        <a href="/dashboard">Dashboard</a>'
    new_ts_nav2 = '<a href="/whitepaper">Whitepaper</a>\n        <a href="/explorer">Explorer</a>\n        <a href="/wallet">Wallet</a>\n        <a href="/dashboard">Dashboard</a>'
    if old_ts_nav2 in content:
        content = content.replace(old_ts_nav2, new_ts_nav2)
        with open(f"{BASE}/token-sale.html", "w") as f:
            f.write(content)
        changes.append("Added Explorer and Wallet links to token-sale.html nav (multiline)")

# === FIX 6: Add nav links to whitepaper.html ===
with open(f"{BASE}/whitepaper.html") as f:
    content = f.read()

# whitepaper.html has a nav element but no page links
# Check if it has any nav links already
if 'href="/dashboard"' not in content[:5000] and 'href="/explorer"' not in content[:5000]:
    # Find the nav element and add links
    # The whitepaper is a single-line HTML, need to find the nav section
    nav_match = re.search(r'<nav[^>]*>(.*?)</nav>', content[:10000], re.DOTALL)
    if nav_match:
        old_nav_content = nav_match.group(0)
        # Check if it has a logo
        if 'verdis-logo' in old_nav_content or 'VERDIS' in old_nav_content:
            # Add links after the logo
            new_nav_content = old_nav_content.replace(
                '</nav>',
                '<div style="display:flex;gap:0;margin-left:8px;"><a href="/dashboard" style="color:#8ba898;font-size:0.85rem;font-weight:500;padding:8px 14px;border-radius:8px;text-decoration:none;">Dashboard</a><a href="/explorer" style="color:#8ba898;font-size:0.85rem;font-weight:500;padding:8px 14px;border-radius:8px;text-decoration:none;">Explorer</a><a href="/token-sale" style="color:#8ba898;font-size:0.85rem;font-weight:500;padding:8px 14px;border-radius:8px;text-decoration:none;">Buy VRDX</a><a href="/team" style="color:#8ba898;font-size:0.85rem;font-weight:500;padding:8px 14px;border-radius:8px;text-decoration:none;">Team</a></div></nav>'
            )
            content = content.replace(old_nav_content, new_nav_content)
            with open(f"{BASE}/whitepaper.html", "w") as f:
                f.write(content)
            changes.append("Added nav links to whitepaper.html")

# === FIX 7: Add nav links to templates.html ===
with open(f"{BASE}/templates.html") as f:
    content = f.read()

# templates.html has: /status, /templates, /dashboard, /dashboard
# It's missing Explorer, Wallet, Whitepaper, Token Sale
old_tmpl_nav = '<a href="/status">Status</a>'
if old_tmpl_nav in content and 'href="/explorer"' not in content[:8000]:
    new_tmpl_nav = '<a href="/dashboard">Dashboard</a><a href="/explorer">Explorer</a><a href="/wallet">Wallet</a><a href="/token-sale">Buy VRDX</a><a href="/whitepaper">Whitepaper</a><a href="/status">Status</a>'
    # Find the nav links section and replace
    # Look for the pattern of multiple links
    old_links_pattern = re.compile(r'(<nav[^>]*>.*?)(<a href="/status[^>]*>[^<]*</a>)(.*?</nav>)', re.DOTALL)
    match = old_links_pattern.search(content[:10000])
    if match:
        # Replace all links between nav open and /status with our new set
        old_section = match.group(0)
        nav_open = match.group(1).rsplit('<a ', 1)[0]  # Get everything before the first link
        nav_close = match.group(3)
        new_section = nav_open + new_tmpl_nav + nav_close
        content = content.replace(old_section, new_section)
        with open(f"{BASE}/templates.html", "w") as f:
            f.write(content)
        changes.append("Enhanced templates.html nav with more links")

print(f"\n=== {len(changes)} fixes applied ===")
for c in changes:
    print(f"  ✓ {c}")
