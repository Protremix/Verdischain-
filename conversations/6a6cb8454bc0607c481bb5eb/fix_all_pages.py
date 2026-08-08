#!/usr/bin/env python3
"""Fix footer links, text sizes, and broken elements across all Verdis Chain pages."""
import os
import re

BASE = "/var/www/verdiscan"
PAGES = [
    ("Landing", "index.html"),
    ("Explorer", "explorer/index.html"),
    ("DEX", "dex/index.html"),
    ("Validators", "validators/index.html"),
    ("Eco", "eco/index.html"),
    ("Faucet", "faucet/index.html"),
    ("Wallet", "wallet/index.html"),
    ("Sale", "sale/index.html"),
    ("Referral", "referral/index.html"),
    ("Incentives", "incentives/index.html"),
    ("Docs", "docs/index.html"),
    ("Whitepaper", "whitepaper/index.html"),
    ("Contact", "contact/index.html"),
    ("API", "api/index.html"),
]

# Standard footer HTML (matches Explorer style)
STANDARD_FOOTER = '''<footer class="footer">
  <div class="footer-links">
    <a href="/">Landing</a>
    <a href="/explorer/">Verdiscan</a>
    <a href="/dex/">DEX</a>
    <a href="/validators/">Validators</a>
    <a href="/eco/">Eco</a>
    <a href="/contact/">Contact</a>
    <a href="/api/">API</a>
    <a href="/docs/">Docs</a>
    <a href="https://github.com/Protremix/Verdischain-" target="_blank">GitHub</a>
  </div>
  <div class="footer-copy">© 2026 Verdis Chain. Powered by live Substrate RPC.</div>
</footer>'''

# Standard footer CSS
FOOTER_CSS = '''.footer{max-width:1200px;margin:0 auto;padding:32px 24px;border-top:1px solid var(--border);margin-top:40px}
.footer-links{display:flex;gap:20px;flex-wrap:wrap;margin-bottom:12px;justify-content:center}
.footer-links a{font-size:12px;color:var(--text-2);text-decoration:none;transition:color .2s}
.footer-links a:hover{color:var(--accent)}
.footer-copy{font-size:11px;color:var(--text-3);text-align:center}'''

fixed_count = 0

for name, path in PAGES:
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        print(f"  {name}: SKIP - file missing")
        continue
    
    with open(full, 'r', errors='replace') as f:
        content = f.read()
    
    original = content
    changes = []
    
    # 1. REPLACE FOOTER
    # Try to find and replace existing <footer>...</footer>
    footer_pattern = r'<footer[^>]*>.*?</footer>'
    footer_match = re.search(footer_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if footer_match:
        content = content[:footer_match.start()] + STANDARD_FOOTER + content[footer_match.end():]
        changes.append("footer replaced")
    elif '<footer' in content.lower():
        # Footer tag but maybe not properly closed - try to find it
        idx = content.lower().find('<footer')
        # Find the closing </footer> or </body>
        close_idx = content.lower().find('</footer>', idx)
        if close_idx == -1:
            close_idx = content.lower().find('</body>', idx)
            if close_idx != -1:
                content = content[:idx] + STANDARD_FOOTER + '\n' + content[close_idx:]
                changes.append("footer added (was unclosed)")
        else:
            close_idx += len('</footer>')
            content = content[:idx] + STANDARD_FOOTER + content[close_idx:]
            changes.append("footer replaced (unclosed)")
    else:
        # No footer at all - add before </body>
        if '</body>' in content:
            content = content.replace('</body>', STANDARD_FOOTER + '\n</body>', 1)
            changes.append("footer added (was missing)")
        else:
            content += STANDARD_FOOTER
    
    # 2. ADD FOOTER CSS IF MISSING
    if '.footer{' not in content and '.footer {' not in content:
        # Add before </style> or before </head>
        if '</style>' in content:
            # Find the last </style>
            last_style = content.rfind('</style>')
            content = content[:last_style] + FOOTER_CSS + '\n' + content[last_style:]
            changes.append("footer CSS added")
        elif '</head>' in content:
            content = content.replace('</head>', '<style>\n' + FOOTER_CSS + '\n</style>\n</head>', 1)
            changes.append("footer CSS added (new style block)")
    
    # 3. FIX LARGE TEXT SIZES
    # Replace any inline font-size > 20px with appropriate smaller values
    # Headings: cap at 20px, body: cap at 16px
    
    # Fix font-size in <style> blocks
    def fix_font_size(match):
        size = float(match.group(1))
        unit = match.group(2) if match.group(2) else 'px'
        if size > 32:
            return f'font-size: 20{unit}'
        elif size > 24:
            return f'font-size: 18{unit}'
        elif size > 20:
            return f'font-size: 16{unit}'
        return match.group(0)
    
    content = re.sub(r'font-size:\s*([0-9.]+)\s*(px|rem|em)?', fix_font_size, content)
    
    # Also fix Tailwind text-xl, text-2xl etc. in class attributes
    # Only replace in visible text elements, not in CSS class definitions
    tw_map = {
        'text-9xl': 'text-xl',
        'text-8xl': 'text-xl', 
        'text-7xl': 'text-xl',
        'text-6xl': 'text-xl',
        'text-5xl': 'text-xl',
        'text-4xl': 'text-lg',
        'text-3xl': 'text-lg',
        'text-2xl': 'text-base',
    }
    for old, new in tw_map.items():
        content = content.replace(f'class="{old}', f'class="{new}')
        content = content.replace(f' {old} ', f' {new} ')
        content = content.replace(f' {old}"', f' {new}"')
    
    if 'text-2xl' in content or 'text-3xl' in content or 'text-4xl' in content:
        changes.append("text sizes reduced")
    
    # 4. FIX DIV MISMATCH (Referral page)
    open_divs = content.count('<div')
    close_divs = content.count('</div>')
    if open_divs < close_divs:
        # Extra closing divs - remove the last extra one before </body>
        diff = close_divs - open_divs
        # Find and remove extra </div> tags before </body>
        body_idx = content.rfind('</body>')
        if body_idx != -1:
            before_body = content[:body_idx]
            for _ in range(diff):
                last_close = before_body.rfind('</div>')
                if last_close != -1:
                    before_body = before_body[:last_close] + before_body[last_close+6:]
            content = before_body + content[body_idx:]
            changes.append(f"removed {diff} extra </div>")
    
    if content != original:
        with open(full, 'w') as f:
            f.write(content)
        print(f"  {name}: ✓ FIXED ({', '.join(changes)})")
        fixed_count += 1
    else:
        print(f"  {name}: ✓ already good")

print(f"\n{fixed_count} pages fixed.")
