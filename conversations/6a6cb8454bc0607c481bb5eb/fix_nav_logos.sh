#!/usr/bin/env bash
set -e

# =====================================================
# FIX 1: Unified logo across explorer.html
# =====================================================
python3 << 'PYEOF'
with open('/opt/verdis/app/dist/web/explorer.html', 'r') as f:
    content = f.read()

# Replace the inline SVG logo with the standard verdis-logo-nav.svg
old_logo = '''  <a href="/" class="nav-logo">
    <svg viewBox="0 0 24 24" fill="none"><path d="M12 2L3 7v10l9 5 9-5V7z" stroke="#14f195" stroke-width="1.5" fill="rgba(20,241,149,0.08)"/><path d="M8 14l4-8 4 8" stroke="#14f195" stroke-width="1.5" fill="none"/></svg>
    Verdiscan
  </a>'''

new_logo = '''  <a href="/" class="nav-logo">
    <img src="/verdis-logo-nav.svg" width="28" height="28" style="filter:drop-shadow(0 0 6px rgba(0,255,136,0.3));" />
    Verdiscan
  </a>'''

content = content.replace(old_logo, new_logo, 1)

# Also add nav links for wallet, token-sale, download if missing
old_nav_links = '''  <div class="nav-links">
    <a href="/explorer" class="active">Explorer</a>
    <a href="/dashboard">Dashboard</a>'''

new_nav_links = '''  <div class="nav-links">
    <a href="/explorer" class="active">Verdiscan</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/wallet">Wallet</a>
    <a href="/token-sale">Buy VRDX</a>
    <a href="/download">Get App</a>'''

content = content.replace(old_nav_links, new_nav_links, 1)

with open('/opt/verdis/app/dist/web/explorer.html', 'w') as f:
    f.write(content)
print('Explorer: logo + nav fixed')
PYEOF

# =====================================================
# FIX 2: Unified logo across wallet.html
# =====================================================
python3 << 'PYEOF'
with open('/opt/verdis/app/dist/web/wallet.html', 'r') as f:
    content = f.read()

# Find the header logo SVG and replace with the standard logo
import re
# Replace inline SVG in header-logo with img tag
pattern = r'(<a[^>]*class="header-logo"[^>]*>)\s*<svg[^>]*>.*?</svg>\s*(<span[^>]*class="header-logo-text"[^>]*>.*?</span>)'
replacement = r'\1<img src="/verdis-logo-nav.svg" width="36" height="36" />\2'
content_new = re.sub(pattern, replacement, content, flags=re.DOTALL)

if content_new != content:
    content = content_new
    print('Wallet: inline SVG logo replaced')
else:
    # Try another approach - find any SVG in header-logo context
    pattern2 = r'(<a[^>]*class="header-logo"[^>]*>)(.*?)(</a>)'
    m = re.search(pattern2, content, re.DOTALL)
    if m:
        old_inner = m.group(2)
        new_inner = '<img src="/verdis-logo-nav.svg" width="36" height="36" style="animation:logoGlow 3s ease-in-out infinite;" /><span class="header-logo-text">VERDIS</span>'
        content = content[:m.start(2)] + new_inner + content[m.end(2):]
        print('Wallet: header logo replaced via regex')
    else:
        print('Wallet: could not find header logo to replace')

with open('/opt/verdis/app/dist/web/wallet.html', 'w') as f:
    f.write(content)
PYEOF

# =====================================================
# FIX 3: Dashboard — add proper navigation bar with Verdiscan
# =====================================================
python3 << 'PYEOF'
with open('/opt/verdis/app/dist/web/dashboard.html', 'r') as f:
    content = f.read()

# Find the dashboard header and replace with a proper nav bar
# The current header has: logo + title + "Home" link + "API Docs" link + social links + wallet pill
# We need to add: Verdiscan, Wallet, Token Sale, Download links

# Find the header div and add navigation links after the "Home" link
old_header_links = '''<a href="/" style="display:inline-flex;align-items:center;gap:4px;padding:6px 14px;background:rgba(0,2.5.236,0.1);border:1px solid rgba(0,2.5.236,0.3);border-radius:8px;color:#00ff88;font-size:0.8rem;font-weight:600;text-decoration:none;margin-left:12px;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,2.5.236,0.2)'" onmouseout="this.style.background='rgba(0,2.5.236,0.1)'">🏠 Home</a><a href="/api-docs" style="font-size:12px;color:var(--text-muted);text-decoration:none;margin-left:8px" target="_blank">API Docs</a>'''

new_header_links = '''<div style="display:inline-flex;align-items:center;gap:6px;margin-left:12px;">
<a href="/" style="display:inline-flex;align-items:center;gap:4px;padding:6px 14px;background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:8px;color:#00ff88;font-size:0.8rem;font-weight:600;text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,136,0.2)'" onmouseout="this.style.background='rgba(0,255,136,0.1)'">🏠 Home</a>
<a href="/explorer" target="_blank" style="display:inline-flex;align-items:center;gap:4px;padding:6px 14px;background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:8px;color:#00ff88;font-size:0.8rem;font-weight:600;text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,136,0.2)'" onmouseout="this.style.background='rgba(0,255,136,0.1)'">🔍 Verdiscan</a>
<a href="/wallet" style="display:inline-flex;align-items:center;gap:4px;padding:6px 14px;background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:8px;color:#00ff88;font-size:0.8rem;font-weight:600;text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,136,0.2)'" onmouseout="this.style.background='rgba(0,255,136,0.1)'">👛 Wallet</a>
<a href="/token-sale" style="display:inline-flex;align-items:center;gap:4px;padding:6px 14px;background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:8px;color:#00ff88;font-size:0.8rem;font-weight:600;text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,136,0.2)'" onmouseout="this.style.background='rgba(0,255,136,0.1)'">💰 Buy VRDX</a>
<a href="/download" style="display:inline-flex;align-items:center;gap:4px;padding:6px 14px;background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:8px;color:#00ff88;font-size:0.8rem;font-weight:600;text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,136,0.2)'" onmouseout="this.style.background='rgba(0,255,136,0.1)'">📱 Get App</a>
<a href="/whitepaper" target="_blank" style="display:inline-flex;align-items:center;gap:4px;padding:6px 14px;background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:8px;color:#00ff88;font-size:0.8rem;font-weight:600;text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,136,0.2)'" onmouseout="this.style.background='rgba(0,255,136,0.1)'">📄 Whitepaper</a>
<a href="/api-docs" target="_blank" style="font-size:12px;color:var(--text-muted);text-decoration:none;margin-left:4px;">API</a>
</div>'''

if old_header_links in content:
    content = content.replace(old_header_links, new_header_links, 1)
    print('Dashboard: nav links replaced (exact match)')
else:
    # Try with the 2.5.236 format (which is a CSS color trick for green)
    # The issue might be the rgba format - let me search more broadly
    import re
    # Find the Home link and API Docs link pattern
    pattern = r'<a href="/" style="display:inline-flex;align-items:center;gap:4px;padding:6px 14px;[^"]*"[^>]*>🏠 Home</a>\s*<a href="/api-docs"[^>]*>API Docs</a>'
    m = re.search(pattern, content)
    if m:
        content = content[:m.start()] + new_header_links + content[m.end():]
        print('Dashboard: nav links replaced (regex match)')
    else:
        print('Dashboard: WARNING - could not find nav links to replace')
        # Let's see what's actually there
        import re as re2
        home_match = re2.search(r'<a href="/"[^>]*>🏠 Home</a>', content)
        print(f"  Home link found: {bool(home_match)}")
        api_match = re2.search(r'<a href="/api-docs"[^>]*>API Docs</a>', content)
        print(f"  API Docs link found: {bool(api_match)}")

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.write(content)
PYEOF

# =====================================================
# FIX 4: Landing page — add Verdiscan label to Explorer link
# =====================================================
python3 << 'PYEOF'
with open('/opt/verdis/app/dist/web/landing.html', 'r') as f:
    content = f.read()

# Change "Explorer" to "Verdiscan" in the nav
content = content.replace(
    '<li><a href="/explorer" target="_blank">Explorer</a></li>',
    '<li><a href="/explorer" target="_blank">Verdiscan</a></li>',
    1
)

with open('/opt/verdis/app/dist/web/landing.html', 'w') as f:
    f.write(content)
print('Landing: Explorer -> Verdiscan label')
PYEOF

# =====================================================
# FIX 5: Favicon consistency — use the SVG everywhere
# =====================================================
for page in dashboard.html wallet.html download.html token-sale.html landing.html explorer.html; do
    ssh root@verdischain.com "sed -i 's|<link rel=\"icon\" type=\"image/png\" href=\"/verdis-logo-ai.png\">|<link rel=\"icon\" type=\"image/svg+xml\" href=\"/verdis-logo-nav.svg\">|' /opt/verdis/app/dist/web/$page 2>/dev/null && echo '$page: favicon updated' || true"
done

echo "=== ALL FIXES APPLIED ==="
