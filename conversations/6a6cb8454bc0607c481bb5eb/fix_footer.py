#!/usr/bin/env python3
"""Fix footer across all Verdis Chain pages:
1. Add footer-social CSS to pages that don't have it
2. Add X/Twitter icon with link
3. Fix footer background on light pages
"""
import re, os, glob

WEB_DIR = "/var/www/verdiscan"

# X/Twitter SVG icon (simplified X logo)
X_ICON = '<a href="https://x.com/Verdischain" target="_blank" aria-label="X (Twitter)"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg></a>'

# The footer-social CSS to add
FOOTER_SOCIAL_CSS = ".footer-social{display:flex;gap:10px;margin-top:16px}.footer-social a{display:flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:6px;color:var(--text-muted,#94a3b8);transition:all .2s}.footer-social a:hover{color:#fff;background:rgba(255,255,255,0.1)}"

# Pages to process
pages = []
for item in sorted(os.listdir(WEB_DIR)):
    idx = os.path.join(WEB_DIR, item, "index.html")
    if os.path.exists(idx):
        pages.append((item, idx))
    elif item.endswith(".html") and os.path.exists(os.path.join(WEB_DIR, item)):
        pages.append((item, os.path.join(WEB_DIR, item)))

fixed_count = 0
for name, path in pages:
    content = open(path).read()
    modified = False
    
    # 1. Add footer-social CSS if not present
    if ".footer-social" not in content:
        # Find the last CSS rule before </style> and add after it
        # Try to find .footer-bottom CSS and add after it
        footer_bottom_css = re.search(r'\.footer-bottom\s*\{[^}]+\}', content)
        if footer_bottom_css:
            insert_pos = footer_bottom_css.end()
            content = content[:insert_pos] + "\n" + FOOTER_SOCIAL_CSS + content[insert_pos:]
            modified = True
        else:
            # Try to find any .footer CSS and add after it
            footer_css = re.search(r'\.footer\s*\{[^}]+\}', content)
            if footer_css:
                insert_pos = footer_css.end()
                content = content[:insert_pos] + "\n" + FOOTER_SOCIAL_CSS + content[insert_pos:]
                modified = True
            else:
                # Add before </style>
                content = content.replace("</style>", FOOTER_SOCIAL_CSS + "\n</style>", 1)
                modified = True
    
    # 2. Add X icon to footer-social if not present
    if "x.com/Verdischain" not in content and "footer-social" in content:
        # Find the footer-social div and add X icon as first link
        # Pattern: <div class="footer-social">\n<a ...GitHub...>
        old_social_start = '<div class="footer-social">'
        if old_social_start in content:
            content = content.replace(
                old_social_start,
                old_social_start + "\n" + X_ICON
            )
            modified = True
    
    # 3. Fix footer background on light pages - ensure --hero-bg is defined
    # Check if --hero-bg is defined in :root or body
    if "--hero-bg" not in content:
        # Add it to :root or the CSS variables section
        root_match = re.search(r':root\s*\{([^}]+)\}', content)
        if root_match:
            root_content = root_match.group(1)
            # Add --hero-bg: #1a1a1a to the :root
            new_root = root_content.rstrip() + "\n--hero-bg: #1a1a1a;"
            content = content.replace(root_match.group(0), ":root{" + new_root + "}")
            modified = True
        else:
            # Try body or * CSS
            body_match = re.search(r'body\s*\{([^}]+)\}', content)
            if body_match:
                body_content = body_match.group(1)
                new_body = body_content.rstrip() + "\n--hero-bg: #1a1a1a;"
                content = content.replace(body_match.group(0), "body{" + new_body + "}")
                modified = True
    
    if modified:
        open(path, "w").write(content)
        fixed_count += 1
        print(f"  FIXED: {name}")
    else:
        print(f"  OK: {name}")

print(f"\nFixed {fixed_count} pages")
