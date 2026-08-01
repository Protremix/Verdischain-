import re, os

CLEAN_LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="38" height="38" '
    'style="flex-shrink:0;pointer-events:none;">'
    '<defs>'
    '<linearGradient id="vlg1" x1="0%" y1="100%" x2="0%" y2="0%">'
    '<stop offset="0%" stop-color="#00aa55"/>'
    '<stop offset="50%" stop-color="#00ff88"/>'
    '<stop offset="100%" stop-color="#66ffbb"/>'
    '</linearGradient>'
    '<linearGradient id="vlg2" x1="0%" y1="0%" x2="100%" y2="100%">'
    '<stop offset="0%" stop-color="#00ff88"/>'
    '<stop offset="100%" stop-color="#2dd4bf"/>'
    '</linearGradient>'
    '<filter id="vgf1">'
    '<feGaussianBlur stdDeviation="3" result="blur"/>'
    '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
    '</filter>'
    '</defs>'
    '<polygon points="100,18 168,58 168,142 100,182 32,142 32,58" fill="none" stroke="url(#vlg2)" stroke-width="2.5" opacity="0.5"/>'
    '<polygon points="100,28 160,65 160,135 100,172 40,135 40,65" fill="none" stroke="url(#vlg2)" stroke-width="3" filter="url(#vgf1)"/>'
    '<path d="M100,60 C100,60 75,80 72,105 C69,130 85,148 100,152 C115,148 131,130 128,105 C125,80 100,60 100,60 Z" fill="url(#vlg1)" opacity="0.9"/>'
    '<line x1="100" y1="60" x2="100" y2="152" stroke="#00ff88" stroke-width="1.5" opacity="0.6"/>'
    '<line x1="100" y1="105" x2="130" y2="85" stroke="#00ff88" stroke-width="1" opacity="0.4"/>'
    '<line x1="100" y1="105" x2="70" y2="85" stroke="#00ff88" stroke-width="1" opacity="0.4"/>'
    '</svg>'
)

CLEAN_NAV_ANCHOR = (
    '<a href="/" class="verdis-logo-wrap" aria-label="Verdis Home" '
    'style="display:inline-flex;align-items:center;gap:10px;text-decoration:none;cursor:pointer;">'
    + CLEAN_LOGO_SVG
    + '<span style="font-weight:700;font-size:1.05rem;color:#e0e0e0;letter-spacing:0.5px;">VERDIS</span>'
    + '</a>'
)

def fix_logo_in_file(content):
    """Find the nav logo anchor (which contains an SVG) and replace it cleanly."""
    # Find opening of the logo-wrap anchor in the <nav> element
    # The anchor starts with: <a href="/" class="verdis-logo-wrap"
    # and we need to find the MATCHING </a> — not just the first one.
    
    start_tag = '<a href="/" class="verdis-logo-wrap"'
    start_pos = content.find(start_tag)
    if start_pos == -1:
        return content, False
    
    # Walk forward from start_pos counting <a...> openings and </a> closings
    pos = start_pos + len(start_tag)
    depth = 1
    while pos < len(content) and depth > 0:
        next_open = content.find('<a', pos)
        next_close = content.find('</a>', pos)
        
        if next_close == -1:
            break
        
        if next_open != -1 and next_open < next_close:
            # Another <a> opens before this one closes
            depth += 1
            pos = next_open + 2
        else:
            # A </a> closes
            depth -= 1
            if depth == 0:
                end_pos = next_close + 4  # include </a>
                content = content[:start_pos] + CLEAN_NAV_ANCHOR + content[end_pos:]
                return content, True
            pos = next_close + 4
    
    return content, False

webdir = "/opt/verdis/app/dist/web"
fixed = 0

for fname in sorted(os.listdir(webdir)):
    if not fname.endswith(".html"):
        continue
    filepath = os.path.join(webdir, fname)
    with open(filepath, "r", errors="replace") as f:
        content = f.read()

    new_content, changed = fix_logo_in_file(content)

    if changed:
        with open(filepath, "w") as f:
            f.write(new_content)
        # Count remaining leaks
        leaks = new_content.count('stroke-linejoin') + new_content.count('animateTransform')
        fixed += 1
        print("Fixed: {:35s} leaks={}".format(fname, leaks))
    else:
        print("Skip:  " + fname)

print("\nTotal fixed: " + str(fixed) + " files")
