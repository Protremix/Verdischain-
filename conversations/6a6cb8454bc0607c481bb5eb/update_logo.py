import re, os

WEB_DIR = "/opt/verdis/app/dist/web"
files = [f for f in os.listdir(WEB_DIR) if f.endswith(".html")]

for fname in files:
    fpath = os.path.join(WEB_DIR, fname)
    with open(fpath, "r") as f:
        content = f.read()
    
    changed = False
    
    # Replace favicon links
    new_favicon = '<link rel="icon" type="image/png" href="/img/verdis-logo.png">'
    if 'rel="icon"' in content or "rel='icon'" in content:
        content = re.sub(r'<link rel=["\']icon["\'][^>]*>', new_favicon, content)
        changed = True
    if 'rel="shortcut icon"' in content or "rel='shortcut icon'" in content:
        content = re.sub(r'<link rel=["\']shortcut icon["\'][^>]*>', new_favicon, content)
        changed = True
    
    # Replace apple-touch-icon
    if "apple-touch-icon" in content:
        content = re.sub(r'<link rel=["\']apple-touch-icon["\'][^>]*>',
                        '<link rel="apple-touch-icon" href="/img/icon-192.png">', content)
        changed = True
    
    # Replace inline SVG logo in nav with img tag
    svg_pattern = r'(<a[^>]*class=["\'][^"\']*\blogo\b[^"\']*["\'][^>]*>)\s*<svg[^>]*>[\s\S]*?</svg>'
    replacement = r'\1\n            <img src="/img/verdis-logo.png" alt="Verdis" style="width:36px;height:36px;object-fit:contain;border-radius:6px;">'
    new_content = re.sub(svg_pattern, replacement, content)
    if new_content != content:
        content = new_content
        changed = True
    
    if changed:
        with open(fpath, "w") as f:
            f.write(content)
        print(f"Updated {fname}")
    else:
        print(f"  No changes needed: {fname}")

print("\nAll files processed")
