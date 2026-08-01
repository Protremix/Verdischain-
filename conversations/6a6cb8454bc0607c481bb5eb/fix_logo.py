import re, os

CLEAN_LOGO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="38" height="38" style="flex-shrink:0;pointer-events:none;">
  <defs>
    <linearGradient id="lg1" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" stop-color="#00aa55"/>
      <stop offset="50%" stop-color="#00ff88"/>
      <stop offset="100%" stop-color="#66ffbb"/>
    </linearGradient>
    <linearGradient id="lg2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00ff88"/>
      <stop offset="100%" stop-color="#2dd4bf"/>
    </linearGradient>
    <filter id="gf1">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <polygon points="100,18 168,58 168,142 100,182 32,142 32,58" fill="none" stroke="url(#lg2)" stroke-width="2.5" opacity="0.5"/>
  <polygon points="100,28 160,65 160,135 100,172 40,135 40,65" fill="none" stroke="url(#lg2)" stroke-width="3" filter="url(#gf1)"/>
  <path d="M100,60 C100,60 75,80 72,105 C69,130 85,148 100,152 C115,148 131,130 128,105 C125,80 100,60 100,60 Z" fill="url(#lg1)" opacity="0.9"/>
  <line x1="100" y1="60" x2="100" y2="152" stroke="#00ff88" stroke-width="1.5" opacity="0.6"/>
  <line x1="100" y1="105" x2="130" y2="85" stroke="#00ff88" stroke-width="1" opacity="0.4"/>
  <line x1="100" y1="105" x2="70" y2="85" stroke="#00ff88" stroke-width="1" opacity="0.4"/>
</svg>'''

CLEAN_NAV = (
    '<a href="/" class="verdis-logo-wrap" aria-label="Verdis Home" '
    'style="display:inline-flex;align-items:center;gap:10px;text-decoration:none;cursor:pointer;">'
    + CLEAN_LOGO_SVG
    + '<span style="font-weight:700;font-size:1.05rem;color:#e0e0e0;letter-spacing:0.5px;">VERDIS</span></a>'
)

webdir = "/opt/verdis/app/dist/web"
fixed = 0

for fname in sorted(os.listdir(webdir)):
    if not fname.endswith(".html"):
        continue
    filepath = os.path.join(webdir, fname)
    with open(filepath, "r", errors="replace") as f:
        content = f.read()

    # Replace broken logo wrap (the SVG inside it may be mangled/nested)
    new_content = re.sub(
        r'<a href="/" class="verdis-logo-wrap"[^>]*>.*?</a>',
        CLEAN_NAV,
        content,
        flags=re.DOTALL
    )

    if new_content != content:
        with open(filepath, "w") as f:
            f.write(new_content)
        fixed += 1
        print("Fixed: " + fname)
    else:
        # Check if there is a broken svg leaking (no logo-wrap but raw SVG paths)
        if "stroke-linejoin" in content and "verdis-logo-wrap" not in content:
            print("Check: " + fname + " (no logo-wrap but has SVG attrs)")
        else:
            print("Skip:  " + fname)

print("\nTotal fixed: " + str(fixed) + " files")
