import re

# === 1. Add Light Paper page to the server ===
with open('/tmp/lightpaper.html', 'r', encoding='utf-8') as f:
    lightpaper = f.read()

import os
os.makedirs('/var/www/verdiscan/lightpaper', exist_ok=True)
os.makedirs('/opt/verdis-chain-rust/web/lightpaper', exist_ok=True)

with open('/var/www/verdiscan/lightpaper/index.html', 'w', encoding='utf-8') as f:
    f.write(lightpaper)
with open('/opt/verdis-chain-rust/web/lightpaper/index.html', 'w', encoding='utf-8') as f:
    f.write(lightpaper)
print(f'Light paper created: {len(lightpaper)} bytes')

# === 2. Add PDF print button and Light Paper link to the whitepaper ===
with open('/var/www/verdiscan/whitepaper/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add print CSS to the whitepaper (before </style>)
print_css = """
@media print{nav,.hero-right,.hero-visual,.wp-doc,.wp-card,.wp-team,.wp-roadmap,.wp-carbon,.float-tag,.hero-lime-circle,#hero-canvas,#cursor-glow,#scroll-bar,.cta-card .hero-actions,.footer-social{display:none!important}nav.std-nav{display:none}.hero-section{padding:0}.hero-container{background:#fff!important;border:none;border-radius:0}.hero-left{padding:20px 0}.hero-title{color:#000}.hero-desc{color:#333}.hero-badge{border:1px solid #16a34a}.btn-primary,.btn-secondary{display:none}.hero-actions{display:none}body{background:#fff;color:#000}.section-block{page-break-inside:avoid;margin-bottom:16px}.card-panel{border:1px solid #ccc}.specs-table{border:1px solid #ccc}.rm-content{border:1px solid #ccc;box-shadow:none}.improve-item{page-break-inside:avoid}.footer{background:#000!important}.reveal{opacity:1!important;transform:none!important}}
"""
html = html.replace('</style>', print_css + '</style>')

# Update hero buttons: add Light Paper and PDF download
old_buttons = '<div class="hero-actions"><a href="#story" class="btn-primary">Read Whitepaper \u2193</a><a href="#tokenomics" class="btn-secondary">Tokenomics \u2192</a></div>'
new_buttons = '<div class="hero-actions"><a href="#story" class="btn-primary">Read Whitepaper \u2193</a><a href="/lightpaper/" class="btn-secondary">Light Paper \u2192</a><a href="#" onclick="window.print();return false" class="btn-secondary">Download PDF \u2193</a></div>'
html = html.replace(old_buttons, new_buttons)

# Add Light Paper link to nav (after Whitepaper)
old_nav = '<a href="/whitepaper/" class="active">Whitepaper</a>'
new_nav = '<a href="/whitepaper/" class="active">Whitepaper</a><a href="/lightpaper/">Light Paper</a>'
html = html.replace(old_nav, new_nav)

# Also add to footer resources
old_footer = '<a href="/whitepaper/">Whitepaper</a><a href="/tokenomics/">Tokenomics</a>'
new_footer = '<a href="/whitepaper/">Whitepaper</a><a href="/lightpaper/">Light Paper</a><a href="/tokenomics/">Tokenomics</a>'
html = html.replace(old_footer, new_footer)

# Update CTA section to include Light Paper and PDF
old_cta = '<div class="hero-actions" style="justify-content:center">\n<a href="/explorer/" class="btn-primary" style="text-decoration:none">Open Explorer \u2192</a>\n<a href="/sale/" class="btn-secondary" style="text-decoration:none">View Token Sale \u2192</a>\n</div>'
new_cta = '<div class="hero-actions" style="justify-content:center">\n<a href="/explorer/" class="btn-primary" style="text-decoration:none">Open Explorer \u2192</a>\n<a href="/lightpaper/" class="btn-secondary" style="text-decoration:none">Light Paper \u2192</a>\n<a href="#" onclick="window.print();return false" class="btn-secondary" style="text-decoration:none">Download PDF \u2193</a>\n</div>'
html = html.replace(old_cta, new_cta)

# Write updated whitepaper
with open('/var/www/verdiscan/whitepaper/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('/opt/verdis-chain-rust/web/whitepaper/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Whitepaper updated: {len(html)} bytes')

# === 3. Add Light Paper to all other pages' nav ===
import glob
pages_updated = 0
for page_path in glob.glob('/var/www/verdiscan/*/index.html'):
    with open(page_path, 'r', encoding='utf-8') as f:
        page = f.read()

    if '/lightpaper/' in page:
        continue  # Already has it

    # Add to nav after Whitepaper
    if '<a href="/whitepaper/">Whitepaper</a>' in page:
        page = page.replace(
            '<a href="/whitepaper/">Whitepaper</a>',
            '<a href="/whitepaper/">Whitepaper</a><a href="/lightpaper/">Light Paper</a>'
        )

    # Add to footer
    if '/whitepaper/">Whitepaper</a>' in page and '/lightpaper/' not in page:
        page = page.replace(
            '<a href="/whitepaper/">Whitepaper</a>',
            '<a href="/whitepaper/">Whitepaper</a><a href="/lightpaper/">Light Paper</a>'
        )

    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(page)

    # Also update the repo copy
    repo_path = page_path.replace('/var/www/verdiscan', '/opt/verdis-chain-rust/web')
    if os.path.exists(os.path.dirname(repo_path)):
        with open(repo_path, 'w', encoding='utf-8') as f:
            f.write(page)

    pages_updated += 1

print(f'Updated {pages_updated} pages with Light Paper nav link')

# === Verify ===
with open('/var/www/verdiscan/whitepaper/index.html', 'r', encoding='utf-8') as f:
    wp = f.read()

with open('/var/www/verdiscan/lightpaper/index.html', 'r', encoding='utf-8') as f:
    lp = f.read()

checks = [
    ('/lightpaper/' in wp, 'Whitepaper has Light Paper link'),
    ('window.print()' in wp, 'Whitepaper has PDF print button'),
    ('@media print' in wp, 'Whitepaper has print CSS'),
    ('Download PDF' in wp, 'Whitepaper has Download PDF button'),
    ('Light Paper' in wp, 'Whitepaper has Light Paper button'),
    ('Verdis Chain' in lp, 'Light paper has branding'),
    ('100B' in lp, 'Light paper has supply'),
    ('DPoS' in lp, 'Light paper has consensus'),
    ('AMM DEX' in lp, 'Light paper has DEX'),
    ('Carbon' in lp, 'Light paper has carbon'),
    ('EvolvixOS' in lp, 'Light paper has EvolvixOS'),
    ('Roadmap' in lp, 'Light paper has roadmap'),
    ('Space Grotesk' in lp, 'Light paper uses Space Grotesk'),
    ('verdis-logo-black.png' in lp, 'Light paper has black logo'),
    ('#0a0e14' in lp, 'Light paper has black footer'),
]
for ok, label in checks:
    print('OK' if ok else 'FAIL', ':', label)
