from PIL import Image
import os

ICON_SIZE = 512
BG_COLOR = (4, 8, 6, 255)  # #040806

# Use the white logo (654x603) — user chose "Full logo (white)"
logo_white = Image.open('/opt/verdis-wallet/mobile/assets/images/verdis-logo-white.png')

# Find content bounds (trim transparent margins)
px = logo_white.load()
min_x, max_x, min_y, max_y = logo_white.size[0], 0, logo_white.size[1], 0
for y in range(logo_white.size[1]):
    for x in range(logo_white.size[0]):
        if px[x, y][3] > 10:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

content = logo_white.crop((min_x, min_y, max_x + 1, max_y + 1))
content_w, content_h = content.size
print(f'Content: {content_w}x{content_h}')

# Scale to 80% of icon
scale = min((ICON_SIZE * 0.80) / content_w, (ICON_SIZE * 0.80) / content_h)
new_w = int(content_w * scale)
new_h = int(content_h * scale)
content_resized = content.resize((new_w, new_h), Image.LANCZOS)

offset_x = (ICON_SIZE - new_w) // 2
offset_y = (ICON_SIZE - new_h) // 2

# === 1. Play Store icon (512x512, opaque) ===
icon = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), BG_COLOR)
icon.paste(content_resized, (offset_x, offset_y), content_resized)
icon.save('/opt/verdis-wallet/mobile/assets/images/ic_launcher_playstore.png', 'PNG')
print(f'Playstore icon: {icon.size}')

# === 2. Foreground for adaptive icons (transparent bg, logo only) ===
fg = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
fg.paste(content_resized, (offset_x, offset_y), content_resized)
fg.save('/tmp/ic_launcher_foreground_master.png', 'PNG')
print(f'Foreground master: {fg.size}')

# === 3. Generate all mipmap densities ===
# Android mipmap sizes (for ic_launcher.png and ic_launcher_round.png):
# mdpi: 48x48, hdpi: 72x72, xhdpi: 96x96, xxhdpi: 144x144, xxxhdpi: 192x192
# Foreground sizes (for adaptive icon foreground):
# mdpi: 108x108, hdpi: 162x162, xhdpi: 216x216, xxhdpi: 324x324, xxxhdpi: 432x432

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

    # ic_launcher.png (square, with background)
    launcher_size = sizes['launcher']
    launcher_icon = icon.resize((launcher_size, launcher_size), Image.LANCZOS)
    launcher_icon.save(os.path.join(ddir, 'ic_launcher.png'), 'PNG')
    launcher_icon.save(os.path.join(ddir, 'ic_launcher_round.png'), 'PNG')

    # ic_launcher_foreground.png (transparent bg, logo only)
    fg_size = sizes['foreground']
    fg_icon = fg.resize((fg_size, fg_size), Image.LANCZOS)
    fg_icon.save(os.path.join(ddir, 'ic_launcher_foreground.png'), 'PNG')

    print(f'  {density}: launcher={launcher_size}px, foreground={fg_size}px')

# === 4. Verify visibility ===
final_px = icon.load()
visible_count = 0
for y in range(0, ICON_SIZE, 16):
    for x in range(0, ICON_SIZE, 16):
        if final_px[x, y][3] > 100 and final_px[x, y] != BG_COLOR:
            visible_count += 1
print(f'Visible content pixels (sampled): {visible_count}/{(ICON_SIZE//16)**2}')

print('All icons generated!')
