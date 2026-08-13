#!/usr/bin/env python3
"""Update whitepaper and lightpaper to link to the actual PDF file"""

# Update whitepaper
with open('/var/www/verdiscan/whitepaper/index.html', 'r') as f:
    html = f.read()

# Replace window.print() with direct PDF link in hero
html = html.replace(
    'onclick="window.print();return false" class="btn-secondary">Download PDF \u2193',
    'href="/whitepaper/verdis-whitepaper.pdf" target="_blank" download class="btn-secondary">Download PDF \u2193'
)
# Replace window.print() in CTA section too
html = html.replace(
    'onclick="window.print();return false" class="btn-secondary" style="text-decoration:none">Download PDF \u2193',
    'href="/whitepaper/verdis-whitepaper.pdf" target="_blank" download class="btn-secondary" style="text-decoration:none">Download PDF \u2193'
)

with open('/var/www/verdiscan/whitepaper/index.html', 'w') as f:
    f.write(html)
with open('/opt/verdis-chain-rust/web/whitepaper/index.html', 'w') as f:
    f.write(html)

# Update lightpaper
with open('/var/www/verdiscan/lightpaper/index.html', 'r') as f:
    lp = f.read()

# Update the "Download PDF" button to point to actual PDF
lp = lp.replace(
    'href="/whitepaper/" onclick="window.print();return false" class="btn-secondary">Download PDF \u2192',
    'href="/whitepaper/verdis-whitepaper.pdf" target="_blank" download class="btn-secondary">Download PDF \u2192'
)

# Add a "Download PDF" button to the light paper hero too
lp = lp.replace(
    '<div class="hero-stats">',
    '<div class="hero-actions" style="margin-bottom:20px"><a href="/whitepaper/verdis-whitepaper.pdf" target="_blank" download class="btn-primary" style="font-size:12px;padding:8px 20px">Download Full PDF \u2193</a></div><div class="hero-stats">'
)

with open('/var/www/verdiscan/lightpaper/index.html', 'w') as f:
    f.write(lp)
with open('/opt/verdis-chain-rust/web/lightpaper/index.html', 'w') as f:
    f.write(lp)

# Verify
with open('/var/www/verdiscan/whitepaper/index.html', 'r') as f:
    wp = f.read()
with open('/var/www/verdiscan/lightpaper/index.html', 'r') as f:
    lp = f.read()

checks = [
    ('/whitepaper/verdis-whitepaper.pdf' in wp, 'Whitepaper links to PDF file'),
    ('window.print()' not in wp, 'No more window.print() in whitepaper'),
    ('/whitepaper/verdis-whitepaper.pdf' in lp, 'Lightpaper links to PDF file'),
]
for ok, label in checks:
    print('OK' if ok else 'FAIL', ':', label)

import os
print(f"PDF size: {os.path.getsize('/var/www/verdiscan/whitepaper/verdis-whitepaper.pdf') / 1024:.1f} KB")
