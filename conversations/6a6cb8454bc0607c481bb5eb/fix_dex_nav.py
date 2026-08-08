#!/usr/bin/env python3
"""Fix DEX page to add standard site navigation."""

with open("/var/www/verdiscan/dex/index.html", "r") as f:
    content = f.read()

# Standard nav CSS (from Explorer)
NAV_CSS = '''.nav{position:sticky;top:0;z-index:40;background:rgba(255,255,255,.92);backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}
.nav-inner{max-width:1200px;margin:0 auto;padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:56px;gap:16px}
.nav-logo{display:flex;align-items:center;gap:8px;flex-shrink:0}
.nav-logo img{height:32px;width:auto}
.nav-links{display:flex;align-items:center;gap:4px;flex:1;justify-content:center;flex-wrap:wrap}
.nav-links a{padding:6px 10px;font-size:12px;font-weight:500;color:var(--text-2);border-radius:6px;transition:all .2s;text-decoration:none}
.nav-links a:hover{color:var(--text);background:rgba(0,0,0,.04)}
.nav-links a.active{color:#00b364;background:rgba(0,179,100,.08)}
.nav-status{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-2);flex-shrink:0}
.pulse-dot{width:8px;height:8px;border-radius:50%;background:#22c55e;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.nav-menu-btn{display:none;padding:8px;background:none;border:none;cursor:pointer;flex-direction:column;gap:4px}
.nav-menu-btn span{width:20px;height:2px;background:#333;border-radius:2px}
@media(max-width:768px){
  .nav-links{display:none}
  .nav-links.mobile{display:flex;flex-direction:column;position:absolute;top:56px;left:0;right:0;background:#fff;border-bottom:1px solid #e0e0e0;padding:12px;gap:0}
  .nav-links.mobile a{padding:10px 14px}
  .nav-menu-btn{display:flex}
}'''

# Standard nav HTML
NAV_HTML = '''<nav class="nav">
  <div class="nav-inner">
    <a href="/" class="nav-logo"><img src="/assets/verdis-logo-black.png" alt="Verdis Chain"></a>
    <div class="nav-links" id="navLinks">
      <a href="/">Home</a>
      <a href="/explorer/">Verdiscan</a>
      <a href="/dex/" class="active">DEX</a>
      <a href="/validators/">Validators</a>
      <a href="/eco/">Eco</a>
      <a href="/faucet/">Faucet</a>
      <a href="/wallet/">Wallet</a>
      <a href="/sale/">Sale</a>
      <a href="/contact/">Contact</a>
      <a href="/api/">API</a>
      <a href="/docs/">Docs</a>
    </div>
    <div class="nav-status"><span class="pulse-dot"></span><span>Testnet Live</span></div>
    <button class="nav-menu-btn" onclick="document.getElementById('navLinks').classList.toggle('mobile')"><span></span><span></span><span></span></button>
  </div>
</nav>'''

# Add nav CSS before the first </style>
if '.nav{' not in content:
    last_style = content.rfind('</style>')
    if last_style != -1:
        content = content[:last_style] + NAV_CSS + '\n' + content[last_style:]

# Replace the old <header class="sticky-nav"> with standard nav
# Keep the DEX-specific tabs below as a sub-nav
old_header_pattern = r'<header class="sticky-nav">.*?</header>'
import re
match = re.search(old_header_pattern, content, re.DOTALL)
if match:
    # Extract the DEX-specific tabs from the old header
    old_header = match.group(0)
    # Find the tab links (Swap, Pools, Liquidity)
    tabs_match = re.findall(r'<li><a[^>]*onclick="switchTab\([^)]*\)"[^>]*>[^<]+</a></li>', old_header)
    
    # Build a sub-nav for DEX tabs
    sub_nav = ''
    if tabs_match:
        sub_nav = '<div style="max-width:1200px;margin:0 auto;padding:0 24px;display:flex;gap:4px;border-bottom:1px solid #e0e0e0">'
        for tab in tabs_match:
            sub_nav += tab.replace('class="nav-link', 'style="padding:10px 16px;font-size:13px;font-weight:500;color:#666;cursor:pointer;border-bottom:2px solid transparent;text-decoration:none')
            sub_nav += '\n'
        sub_nav += '</div>'
    
    content = content[:match.start()] + NAV_HTML + '\n' + sub_nav + content[match.end():]
    print("DEX nav replaced with standard nav + sub-nav")
else:
    # Just add nav after <body>
    body_idx = content.find('<body')
    if body_idx != -1:
        # Find the end of the body opening tag
        body_end = content.find('>', body_idx) + 1
        content = content[:body_end] + '\n' + NAV_HTML + '\n' + content[body_end:]
        print("Standard nav added after <body>")

with open("/var/www/verdiscan/dex/index.html", "w") as f:
    f.write(content)

print("DEX page fixed!")
