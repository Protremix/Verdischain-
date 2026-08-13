import re

with open('/var/www/verdiscan/whitepaper/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove Poppins from font import (keep Inter, Space Grotesk, JetBrains Mono)
html = html.replace(
    "family=Poppins:wght@400;500;600;700;800;900&display=swap",
    "display=swap"
)

# 2. Fix NAV: dark -> light (matching tokenomics)
html = html.replace(
    "nav.std-nav{position:sticky;top:0;z-index:100;background:rgba(10,10,10,0.85);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);padding:0 24px;height:64px;",
    "nav.std-nav{position:sticky;top:0;z-index:100;background:rgba(255,255,255,0.85);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);padding:0 24px;height:76px;"
)

# Fix nav hamburger color for light nav
html = html.replace(
    ".nav-hamburger span{width:22px;height:2px;background:var(--text);border-radius:2px}",
    ".nav-hamburger span{width:22px;height:2px;background:var(--text);border-radius:2px}"
)

# Fix mobile nav background for light theme
html = html.replace(
    ".nav-links{display:none;position:absolute;top:64px;left:0;right:0;flex-direction:column;background:var(--bg-1);padding:12px;border-bottom:1px solid var(--border)}",
    ".nav-links{display:none;position:absolute;top:76px;left:0;right:0;flex-direction:column;background:#fff;padding:12px;border-bottom:1px solid var(--border)}"
)

# 3. Fix HERO: dark -> light
# Hero container background
html = html.replace(
    ".hero-container{max-width:1100px;margin:0 auto;background:var(--hero-bg);border-radius:24px;overflow:hidden;position:relative;min-height:400px;display:flex}",
    ".hero-container{max-width:1100px;margin:0 auto;background:linear-gradient(135deg,#f8fafc 0%,#f1f5f9 100%);border:1px solid var(--border);border-radius:24px;overflow:hidden;position:relative;min-height:400px;display:flex}"
)

# Hero green orb - make it lighter for light theme
html = html.replace(
    ".hero-container::before{content:'';position:absolute;top:-30%;right:-15%;width:700px;height:700px;background:radial-gradient(circle,var(--accent-glow-strong),transparent 55%);opacity:.12;animation:pulse-bg 4s ease-in-out infinite;pointer-events:none}",
    ".hero-container::before{content:'';position:absolute;top:-30%;right:-15%;width:700px;height:700px;background:radial-gradient(circle,rgba(22,163,74,0.15),transparent 55%);opacity:.5;animation:pulse-bg 4s ease-in-out infinite;pointer-events:none}"
)

html = html.replace(
    ".hero-container::after{content:'';position:absolute;bottom:-20%;left:-10%;width:500px;height:500px;background:radial-gradient(circle,rgba(0,168,107,0.15),transparent 60%);opacity:.08;animation:pulse-bg 6s ease-in-out infinite 1s;pointer-events:none}",
    ".hero-container::after{content:'';position:absolute;bottom:-20%;left:-10%;width:500px;height:500px;background:radial-gradient(circle,rgba(0,168,107,0.08),transparent 60%);opacity:.4;animation:pulse-bg 6s ease-in-out infinite 1s;pointer-events:none}"
)

# Fix pulse-bg keyframes for light theme
html = html.replace(
    "@keyframes pulse-bg{0%,100%{opacity:.08;transform:scale(1)}50%{opacity:.15;transform:scale(1.1)}}",
    "@keyframes pulse-bg{0%,100%{opacity:.4;transform:scale(1)}50%{opacity:.6;transform:scale(1.1)}}"
)

# 4. Fix hero text: white -> dark
html = html.replace(
    ".hero-title{font-family:'Poppins',sans-serif;font-size:13px;font-weight:900;line-height:1.05;color:var(--text-white);margin-bottom:12px;letter-spacing:-0.02em;",
    ".hero-title{font-family:'Space Grotesk',sans-serif;font-size:20px;font-weight:700;line-height:1.1;color:var(--text);margin-bottom:12px;letter-spacing:-0.02em;"
)

html = html.replace(
    ".hero-desc{font-size:13px;color:var(--text-dim);line-height:1.6;margin-bottom:12px;max-width:500px;",
    ".hero-desc{font-size:14px;color:var(--text-2);line-height:1.6;margin-bottom:12px;max-width:500px;"
)

# Fix hero badge for light theme
html = html.replace(
    ".hero-badge{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;background:var(--accent-light);border:1px solid var(--accent-border);border-radius:var(--radius-pill);font-size:11px;font-weight:600;color:var(--accent);margin-bottom:16px;width:fit-content;",
    ".hero-badge{display:inline-flex;align-items:center;gap:6px;padding:6px 16px;background:var(--accent-glow);border:1px solid var(--accent);border-radius:var(--radius-pill);font-size:13px;font-weight:600;color:var(--accent);margin-bottom:16px;width:fit-content;"
)

# 5. Fix hero buttons for light theme
html = html.replace(
    ".btn-primary{background:linear-gradient(135deg,#16a34a,#15803d);color:var(--hero-bg);font-size:13px;font-weight:700;padding:10px 24px;border-radius:var(--radius-pill);border:none;cursor:pointer;transition:var(--transition);position:relative;overflow:hidden;display:inline-flex;align-items:center;gap:8px;text-decoration:none}",
    ".btn-primary{background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;font-size:13px;font-weight:700;padding:10px 24px;border-radius:var(--radius-pill);border:none;cursor:pointer;transition:var(--transition);position:relative;overflow:hidden;display:inline-flex;align-items:center;gap:8px;text-decoration:none}"
)

html = html.replace(
    ".btn-secondary{background:transparent;color:var(--text-white);font-size:13px;font-weight:600;padding:14px 32px;border-radius:var(--radius-pill);border:1px solid rgba(255,255,255,0.15);cursor:pointer;transition:var(--transition);display:inline-flex;align-items:center;gap:8px;text-decoration:none}.btn-secondary:hover{border-color:var(--accent);background:var(--accent-light);color:var(--accent)}",
    ".btn-secondary{background:transparent;color:var(--text);font-size:13px;font-weight:600;padding:10px 24px;border-radius:var(--radius-pill);border:1px solid var(--border);cursor:pointer;transition:var(--transition);display:inline-flex;align-items:center;gap:8px;text-decoration:none}.btn-secondary:hover{border-color:var(--accent);background:var(--accent-light);color:var(--accent)}"
)

# 6. Fix floating cards: dark -> white
html = html.replace(
    ".wp-doc,.wp-card,.wp-team,.wp-roadmap,.wp-carbon,.float-tag{backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.14);box-shadow:0 20px 60px rgba(0,0,0,0.5)}",
    ".wp-doc,.wp-card,.wp-team,.wp-roadmap,.wp-carbon,.float-tag{backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid var(--border);box-shadow:0 20px 60px rgba(0,0,0,0.08)}"
)

# Fix doc card background
html = html.replace(
    ".wp-doc{position:absolute;top:5%;left:5%;width:200px;padding:16px;border-radius:16px;background:rgba(45,45,45,0.85);z-index:3}",
    ".wp-doc{position:absolute;top:5%;left:5%;width:200px;padding:16px;border-radius:16px;background:rgba(255,255,255,0.95);z-index:3}"
)

# Fix doc card text
html = html.replace(
    ".wp-doc-title{font-size:11px;font-weight:700;color:var(--text-white);font-family:'Space Grotesk",
    ".wp-doc-title{font-size:11px;font-weight:700;color:var(--text);font-family:'Space Grotesk"
)

html = html.replace(
    ".wp-doc-sub{font-size:10px;color:var(--text-muted)",
    ".wp-doc-sub{font-size:10px;color:var(--text-3)"
)

# Fix VRDX supply card
html = html.replace(
    "background:rgba(45,45,45,0.85);z-index:3}.wp-card",
    "background:rgba(255,255,255,0.95);z-index:3}.wp-card"
)

html = html.replace(
    ".wp-card-label{font-size:10px;font-weight:600;color:var(--text-muted)",
    ".wp-card-label{font-size:10px;font-weight:600;color:var(--text-3)"
)

html = html.replace(
    ".wp-card-value{font-family:'JetBrains Mono';font-size:18px;font-weight:700;color:var(--text-white)",
    ".wp-card-value{font-family:'JetBrains Mono';font-size:18px;font-weight:700;color:var(--text)"
)

html = html.replace(
    ".wp-card-sub{font-size:9px;color:var(--text-muted)",
    ".wp-card-sub{font-size:9px;color:var(--text-3)"
)

# Fix carbon card
html = html.replace(
    ".wp-carbon{position:absolute;top:40%;right:0%;width:140px;padding:12px;border-radius:16px;background:rgba(45,45,45,0.85);z-index:3",
    ".wp-carbon{position:absolute;top:40%;right:0%;width:140px;padding:12px;border-radius:16px;background:rgba(255,255,255,0.95);z-index:3"
)

html = html.replace(
    ".wp-carbon-label{font-size:9px;color:var(--text-muted)",
    ".wp-carbon-label{font-size:9px;color:var(--text-3)"
)

# Fix team card
html = html.replace(
    ".wp-team{position:absolute;bottom:8%;left:8%;width:160px;padding:14px;border-radius:16px;background:rgba(45,45,45,0.85);z-index:3",
    ".wp-team{position:absolute;bottom:8%;left:8%;width:160px;padding:14px;border-radius:16px;background:rgba(255,255,255,0.95);z-index:3"
)

html = html.replace(
    ".wp-team-label{font-size:10px;font-weight:600;color:var(--text-white)",
    ".wp-team-label{font-size:10px;font-weight:600;color:var(--text)"
)

html = html.replace(
    ".wp-team-sub{font-size:9px;color:var(--text-muted)",
    ".wp-team-sub{font-size:9px;color:var(--text-3)"
)

# Fix roadmap card
html = html.replace(
    ".wp-roadmap{position:absolute;bottom:5%;right:8%;width:170px;padding:12px;border-radius:16px;background:rgba(45,45,45,0.85);z-index:3",
    ".wp-roadmap{position:absolute;bottom:5%;right:8%;width:170px;padding:12px;border-radius:16px;background:rgba(255,255,255,0.95);z-index:3"
)

html = html.replace(
    ".wp-roadmap-title{font-size:10px;font-weight:600;color:var(--text-white)",
    ".wp-roadmap-title{font-size:10px;font-weight:600;color:var(--text)"
)

html = html.replace(
    ".wp-roadmap-text{font-size:9px;color:var(--text-muted)",
    ".wp-roadmap-text{font-size:9px;color:var(--text-3)"
)

# Fix green orb - make it softer for light theme
html = html.replace(
    ".hero-lime-circle{position:absolute;width:560px;height:560px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#16a34a 0%,#15803d 65%,#88be00 100%);box-shadow:0 0 100px rgba(22,163,74,0.45);z-index:1}",
    ".hero-lime-circle{position:absolute;width:480px;height:480px;border-radius:50%;background:radial-gradient(circle at 35% 35%,rgba(22,163,74,0.3) 0%,rgba(21,128,61,0.15) 65%,rgba(136,190,0,0.05) 100%);box-shadow:0 0 80px rgba(22,163,74,0.15);z-index:1}"
)

# Fix float tags for light theme
html = html.replace(
    ".float-tag.green{background:rgba(22,163,74,0.15);color:var(--accent);border:1px solid var(--accent-border)}",
    ".float-tag.green{background:rgba(22,163,74,0.1);color:var(--accent);border:1px solid var(--accent-border)}"
)

html = html.replace(
    ".float-tag.white{background:rgba(255,255,255,0.1);color:var(--text-white)}",
    ".float-tag.white{background:rgba(255,255,255,0.7);color:var(--text-2);border:1px solid var(--border)}"
)

html = html.replace(
    ".float-tag.eco{background:rgba(74,222,128,0.15);color:#4ade80;border:1px solid rgba(74,222,128,0.25)}",
    ".float-tag.eco{background:rgba(74,222,128,0.1);color:#15803d;border:1px solid rgba(74,222,128,0.25)}"
)

# Fix stats bar for light theme (already light, just make sure)
# The stats bar uses var(--card) which is #ffffff - good

# 7. Fix hero gradient text (already uses green gradient - keep it)
# Already correct: linear-gradient(135deg,#16a34a 0%,#15803d 50%,#00a86b 100%)

# 8. Remove --hero-bg and --hero-card dark vars, replace with light
html = html.replace(
    "--hero-bg:#1a1a1a;--hero-card:#2d2d2d;",
    "--hero-bg:#f8fafc;--hero-card:#ffffff;"
)

# 9. Fix the hero badge dot color
html = html.replace(
    ".hero-badge-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);animation:pulse-dot 2s infinite}",
    ".hero-badge-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);animation:pulse 2s infinite}"
)

# 10. Fix the stats bar text colors (already using var(--text) etc - good)

# 11. Fix the nav link hover - add background
html = html.replace(
    ".nav-links a:hover,.nav-links a.active{color:var(--accent)}",
    ".nav-links a:hover,.nav-links a.active{color:var(--accent);background:#f8fafc}"
)

# 12. Fix the nav status text color
# Already uses var(--text-2) which is #475569 (dark) - good for light nav

# 13. Fix the footer for light theme (check if it needs fixing)
# The footer uses var(--card), var(--border) etc - already light

# 14. Fix the hero title HTML - remove "VERDIS CHAIN" prefix text color
html = html.replace(
    'style="font-size:13px;font-weight:400;color:var(--text-muted)"',
    'style="font-size:14px;font-weight:400;color:var(--text-3)"'
)

# 15. Fix the CTA section at the bottom
html = html.replace(
    'background:linear-gradient(135deg,#16a34a,#15803d);color:#fff',
    'background:linear-gradient(135deg,#16a34a,#15803d);color:#fff'
)

# Write files
with open('/var/www/verdiscan/whitepaper/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('/opt/verdis-chain-rust/web/whitepaper/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
with open('/var/www/verdiscan/whitepaper/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

checks = [
    ('rgba(255,255,255,0.85)' in content, 'Light nav background'),
    ('rgba(10,10,10,0.85)' not in content, 'No dark nav'),
    ('Poppins' not in content, 'No Poppins font'),
    ('Space Grotesk' in content, 'Space Grotesk font'),
    ('Inter' in content, 'Inter font'),
    ('rgba(255,255,255,0.95)' in content, 'Light card backgrounds'),
    ('rgba(45,45,45,0.85)' not in content, 'No dark card backgrounds'),
    ('var(--text-white)' not in content or content.count('var(--text-white)') < 5, 'Reduced white text refs'),
    ('#16a34a' in content, 'Correct green'),
    ('caff33' not in content, 'No neon green'),
    ('verdis-logo-black.png' in content, 'Black logo (visible on light nav)'),
    ('Executive Summary' in content, 'Executive Summary'),
    ('Dorian Jean' in content, 'Team member'),
    ('100B' in content, '100B supply'),
]
for ok, label in checks:
    print('OK' if ok else 'FAIL', ':', label)

print(f'\nTotal: {len(content)} bytes')
# Count remaining dark references
dark_refs = content.count('text-white') + content.count('hero-bg') + content.count('2d2d2d') + content.count('1a1a1a')
print(f'Remaining dark refs: {dark_refs}')
