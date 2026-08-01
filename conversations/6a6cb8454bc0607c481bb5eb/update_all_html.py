import os
import re

WEB_DIR = '/opt/verdis/app/dist/web'
files = [f for f in os.listdir(WEB_DIR) if f.endswith('.html')]

favicon_img = '<link rel="icon" type="image/png" href="/img/verdis-logo.png">'
apple_touch_img = '<link rel="apple-touch-icon" href="/img/icon-192.png">'
shortcut_icon_img = '<link rel="shortcut icon" href="/img/verdis-logo.png">'
logo_img_tag = '<img src="/img/verdis-logo.png" alt="Verdis" style="width:36px;height:36px;object-fit:contain;border-radius:6px;">'

for fname in files:
    fpath = os.path.join(WEB_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Favicons
    if re.search(r'<link rel=["\']icon["\'][^>]*>', content):
        content = re.sub(
            r'<link rel=["\']icon["\'][^>]*>',
            favicon_img,
            content
        )
    else:
        # insert before </head>
        content = re.sub(r'</head>', f'  {favicon_img}\n</head>', content, count=1, flags=re.IGNORECASE)

    if re.search(r'<link rel=["\']shortcut icon["\'][^>]*>', content):
        content = re.sub(
            r'<link rel=["\']shortcut icon["\'][^>]*>',
            shortcut_icon_img,
            content
        )

    if re.search(r'<link rel=["\']apple-touch-icon["\'][^>]*>', content):
        content = re.sub(
            r'<link rel=["\']apple-touch-icon["\'][^>]*>',
            apple_touch_img,
            content
        )
    else:
        # insert before </head>
        content = re.sub(r'</head>', f'  {apple_touch_img}\n</head>', content, count=1, flags=re.IGNORECASE)

    # 2. Replace logo SVGs and divs/emojis in header/nav logo links

    # Handle landing/markets pattern with <div class="logo-icon"><svg>...</svg></div> or direct <svg>
    content = re.sub(
        r'(<a[^>]*class=["\'][^"\']*(logo|brand-logo|nav-logo|nav-brand)[^"\']*["\'][^>]*>)\s*<div class=["\'](logo-icon|brand-icon|brand-logo-icon|nav-brand-logo)["\']>\s*<svg[^>]*>[\s\S]*?</svg>\s*</div>',
        r'\1\n  ' + logo_img_tag,
        content
    )

    content = re.sub(
        r'(<a[^>]*class=["\'][^"\']*(logo|brand-logo|nav-logo|nav-brand)[^"\']*["\'][^>]*>)\s*<svg[^>]*>[\s\S]*?</svg>',
        r'\1\n  ' + logo_img_tag,
        content
    )

    # Handle emoji in logo icons: <div class="logo-icon">🌿</div>, <div class="brand-logo-icon">🌿</div>, <div class="nav-brand-logo">🌿</div>
    content = re.sub(
        r'<div class=["\'](logo-icon|brand-logo-icon|nav-brand-logo)["\']>🌿</div>',
        logo_img_tag,
        content
    )

    # Handle <span>🌿 VERDIS</span>
    content = re.sub(
        r'<span>🌿\s*VERDIS</span>',
        f'<img src="/img/verdis-logo.png" alt="Verdis" style="width:36px;height:36px;object-fit:contain;border-radius:6px;vertical-align:middle;margin-right:6px;"><span>VERDIS</span>',
        content
    )

    # Handle dashboard h1: <h1><span>🌿</span> Verdis Blockchain
    content = re.sub(
        r'<h1><span>🌿</span>\s*Verdis Blockchain',
        f'<h1><img src="/img/verdis-logo.png" alt="Verdis" style="width:36px;height:36px;object-fit:contain;border-radius:6px;vertical-align:middle;margin-right:8px;display:inline-block;"> Verdis Blockchain',
        content
    )

    # Handle explorer nav-brand: <div class="nav-brand">🌿 <span>VERDIS</span> EXPLORER</div>
    content = re.sub(
        r'<div class="nav-brand">🌿\s*<span>VERDIS</span>',
        f'<div class="nav-brand"><img src="/img/verdis-logo.png" alt="Verdis" style="width:36px;height:36px;object-fit:contain;border-radius:6px;vertical-align:middle;margin-right:8px;display:inline-block;"> <span>VERDIS</span>',
        content
    )

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Updated {fname}')

print('All files updated')
