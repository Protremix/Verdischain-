import re

with open("/opt/verdis/app/dist/web/download.html", "r", errors="replace") as f:
    content = f.read()

# ── 1. Remove "AI Generated" labels everywhere ──────────────────────────────
content = content.replace("🌱 Verdis Logo — AI Generated", "🌱 Verdis Logo")
content = content.replace("Verdis Logo — AI Generated", "Verdis Logo")
content = content.replace("AI Generated PNG", "Official PNG")
content = content.replace("AI Generated SVG", "Animated SVG")
content = content.replace("AI generated", "Official")
content = content.replace("AI-generated", "Official")
content = content.replace("AI Generated", "Official")

# ── 2. Replace the entire broken logo-download-section ──────────────────────
# Find it and replace with a clean version

CLEAN_LOGO_SVG_100 = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100" height="100" '
    'style="display:block;pointer-events:none;">'
    '<defs>'
    '<linearGradient id="dlg1" x1="0%" y1="100%" x2="0%" y2="0%">'
    '<stop offset="0%" stop-color="#00aa55"/>'
    '<stop offset="50%" stop-color="#00ff88"/>'
    '<stop offset="100%" stop-color="#66ffbb"/>'
    '</linearGradient>'
    '<linearGradient id="dlg2" x1="0%" y1="0%" x2="100%" y2="100%">'
    '<stop offset="0%" stop-color="#00ff88"/>'
    '<stop offset="100%" stop-color="#2dd4bf"/>'
    '</linearGradient>'
    '<filter id="dgf">'
    '<feGaussianBlur stdDeviation="3" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
    '</filter>'
    '</defs>'
    '<polygon points="100,18 168,58 168,142 100,182 32,142 32,58" fill="none" stroke="url(#dlg2)" stroke-width="2" opacity="0.5"/>'
    '<polygon points="100,28 160,65 160,135 100,172 40,135 40,65" fill="none" stroke="url(#dlg2)" stroke-width="2.5" filter="url(#dgf)"/>'
    '<path d="M100,58 C100,58 74,78 71,104 C68,130 84,148 100,152 C116,148 132,130 129,104 C126,78 100,58 100,58 Z" fill="url(#dlg1)" opacity="0.9"/>'
    '<line x1="100" y1="58" x2="100" y2="152" stroke="#00ff88" stroke-width="1.5" opacity="0.6"/>'
    '<line x1="100" y1="105" x2="128" y2="87" stroke="#00ff88" stroke-width="1" opacity="0.4"/>'
    '<line x1="100" y1="105" x2="72" y2="87" stroke="#00ff88" stroke-width="1" opacity="0.4"/>'
    '</svg>'
)

CLEAN_LOGO_SVG_60 = CLEAN_LOGO_SVG_100.replace('width="100" height="100"', 'width="60" height="60"')

CLEAN_SECTION = '''<div class="logo-download-section">
    <h2 style="text-align:center;color:#00ff88;font-size:1.5rem;margin-bottom:8px;">🌱 Verdis Logo</h2>
    <p style="text-align:center;color:#888;font-size:0.85rem;margin-bottom:24px;">Official hexagonal leaf logo — PNG &amp; animated SVG</p>
    <div class="logo-preview">
        <div class="logo-preview-item">
            ''' + CLEAN_LOGO_SVG_100 + '''
            <div class="label">Animated SVG</div>
        </div>
        <div class="logo-preview-item">
            <img src="/verdis-logo-ai.png" width="60" height="60" alt="Verdis Logo PNG" style="border-radius:12px;">
            <div class="label">Official PNG</div>
        </div>
    </div>
    <div class="logo-download-buttons">
        <a href="/verdis-logo-ai.png" download="verdis-logo.png" class="btn-png">&#128444; Download PNG (1024&#215;1024)</a>
        <a href="/verdis-logo-animated.svg" download="verdis-logo-animated.svg" class="btn-svg">&#127907; Download Animated SVG</a>
        <a href="/verdis-favicon-ai.png" download="verdis-favicon.png" class="btn-svg">&#127991; Download Favicon (32&#215;32)</a>
    </div>
</div>'''

# Replace the old broken logo-download-section
new_content = re.sub(
    r'<div class="logo-download-section">.*?</div>\s*(?=<div|<section|<footer|<!--)',
    CLEAN_SECTION + '\n',
    content,
    flags=re.DOTALL
)

if new_content == content:
    print("WARNING: logo-download-section pattern not found, trying alternate")
    # Fallback: just replace the title and AI labels
    new_content = content

# ── 3. Double-check no "AI" remains in visible text ─────────────────────────
remaining = re.findall(r'AI [Gg]enerat\w+', new_content)
print("Remaining AI labels:", remaining)

with open("/opt/verdis/app/dist/web/download.html", "w") as f:
    f.write(new_content)

# Verify SVG balance
opens = new_content.count("<svg")
closes = new_content.count("</svg>")
print(f"SVG balance: {opens} open / {closes} close — balanced={opens==closes}")
print(f"File size: {len(new_content):,} bytes")
print("Done")
