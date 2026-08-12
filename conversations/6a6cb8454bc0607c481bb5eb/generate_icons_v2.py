from PIL import Image
import os

ICON_SIZE = 512
BG_COLOR = (4, 8, 6, 255)  # #040806 - Verdis Dark

# Load the new icon (V-shape + blockchain nodes, transparent bg)
logo = Image.open('/tmp/new_app_icon.png').convert('RGBA')
px = logo.load()

# Find content bounds (trim transparent margins)
w, h = logo.size
min_x, max_x, min_y, max_y = w, 0, h, 0
for y in range(h):
    for x in range(w):
        if px[x, y][3] > 10:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

content = logo.crop((min_x, min_y, max_x + 1, max_y + 1))
content_w, content_h = content.size
print(f'Content bounds: {content_w}x{content_h}')

# Scale to fit 78% of icon (leave some padding, standard for adaptive icons)
scale = min((ICON_SIZE * 0.78) / content_w, (ICON_SIZE * 0.78) / content_h)
new_w = int(content_w * scale)
new_h = int(content_h * scale)
content_resized = content.resize((new_w, new_h), Image.LANCZOS)

offset_x = (ICON_SIZE - new_w) // 2
offset_y = (ICON_SIZE - new_h) // 2

# === 1. Play Store / master icon (512x512, opaque dark bg) ===
icon = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), BG_COLOR)
icon.paste(content_resized, (offset_x, offset_y), content_resized)
icon.save('/opt/verdis-wallet/mobile/assets/images/ic_launcher_playstore.png', 'PNG')
print(f'Playstore icon: {icon.size}')

# === 2. Foreground for adaptive icons (transparent bg, logo only, scaled smaller for safe zone) ===
# Adaptive icon foreground needs extra padding (icon is masked/cropped by shape) — use 65% scale
scale_fg = min((ICON_SIZE * 0.65) / content_w, (ICON_SIZE * 0.65) / content_h)
fg_w = int(content_w * scale_fg)
fg_h = int(content_h * scale_fg)
content_fg = content.resize((fg_w, fg_h), Image.LANCZOS)
fg_offset_x = (ICON_SIZE - fg_w) // 2
fg_offset_y = (ICON_SIZE - fg_h) // 2

fg = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
fg.paste(content_fg, (fg_offset_x, fg_offset_y), content_fg)
fg.save('/tmp/ic_launcher_foreground_master.png', 'PNG')
print(f'Foreground master: {fg.size}')

# === 3. Generate all mipmap densities ===
densities = {
    'mdpi': {'launcher': 48, 'foreground': 108},
    'hdpi': {'launcher': 72, 'foreground': 162},
    'xhdpi': {'launcher': 96, 'foreground': 216},
    'xxhdpi': {'launcher': 144, 'foreground': 324},
    'xxxhdpi': {'launcher': 192, 'foreground': 432},
}

res_base = '/opt/verdis-wallet/mobile/android/app/src/main/res'

for density, sizes in densities.items():
    ddir = os.path.join(res_base, f'mipmap-{density}')
    os.makedirs(ddir, exist_ok=True)

    launcher_size = sizes['launcher']
    launcher_icon = icon.resize((launcher_size, launcher_size), Image.LANCZOS)
    launcher_icon.save(os.path.join(ddir, 'ic_launcher.png'), 'PNG')
    launcher_icon.save(os.path.join(ddir, 'ic_launcher_round.png'), 'PNG')

    fg_size = sizes['foreground']
    fg_icon = fg.resize((fg_size, fg_size), Image.LANCZOS)
    fg_icon.save(os.path.join(ddir, 'ic_launcher_foreground.png'), 'PNG')

    print(f'  {density}: launcher={launcher_size}px, foreground={fg_size}px')

print('All icons generated from new V+nodes logo!')
