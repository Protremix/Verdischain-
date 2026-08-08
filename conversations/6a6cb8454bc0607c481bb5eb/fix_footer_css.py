#!/usr/bin/env python3
"""Fix footer CSS: add complete footer CSS classes to all pages that have footer HTML but are missing the CSS."""
import re, os

WEB_DIR = "/var/www/verdiscan"

# The complete footer CSS from the homepage (with fallback values for CSS vars)
FOOTER_CSS = """
/* === Footer (from homepage) === */
.footer { background: var(--hero-bg, #1a1a1a); padding: 28px 24px 32px; max-width: none; margin: 0; border-top: none; margin-top: 0; }
.footer-inner { max-width: 1000px; margin: 0 auto; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 48px; }
.footer-brand h3 { font-size: 13px; font-weight: 800; color: #fff; margin-bottom: 12px; }
.footer-brand p { font-size: 14px; color: #94a3b8; max-width: 280px; }
.footer-col h4 { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; margin-bottom: 16px; }
.footer-col a { display: block; font-size: 14px; color: #cbd5e1; margin-bottom: 10px; transition: color .2s; text-decoration: none; }
.footer-col a:hover { color: #16a34a; }
.footer-bottom { max-width: 1000px; margin: 32px auto 0; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; font-size: 13px; color: #64748b; }
.footer-links { display: none; }
.footer-copy { display: none; }
@media (max-width: 768px) { .footer-inner { grid-template-columns: 1fr 1fr; } }
@media (max-width: 480px) { .footer-inner { grid-template-columns: 1fr; gap: 24px; } .footer-bottom { flex-direction: column; gap: 8px; text-align: center; } }
/* === End Footer === */
"""

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
    
    # Check if this page has the footer HTML structure (footer-inner, footer-brand, footer-col)
    has_footer_html = ("footer-inner" in content and "footer-brand" in content and "footer-col" in content)
    if not has_footer_html:
        print(f"  SKIP: {name} (no footer HTML structure)")
        continue
    
    # Check if this page is missing the footer-inner CSS class
    has_footer_inner_css = bool(re.search(r'\.footer-inner\s*\{', content))
    
    if not has_footer_inner_css:
        # This page has the footer HTML but is missing the CSS classes
        # Insert the footer CSS before </style>
        content = content.replace("</style>", FOOTER_CSS + "\n</style>", 1)
        open(path, "w").write(content)
        fixed_count += 1
        print(f"  FIXED: {name} (added complete footer CSS)")
    else:
        # Has footer-inner CSS - check if it has all the needed classes
        has_footer_col_css = bool(re.search(r'\.footer-col\s*[ha]\s*\{', content))
        has_footer_bottom_css = bool(re.search(r'\.footer-bottom\s*\{', content))
        
        if not has_footer_col_css or not has_footer_bottom_css:
            # Add missing CSS classes
            content = content.replace("</style>", FOOTER_CSS + "\n</style>", 1)
            open(path, "w").write(content)
            fixed_count += 1
            print(f"  FIXED: {name} (added missing footer CSS classes)")
        else:
            print(f"  OK: {name} (footer CSS complete)")

print(f"\nFixed {fixed_count} pages")
