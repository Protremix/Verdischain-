from PIL import Image

# Check the verdis-logo-icon.png content
logo_icon = Image.open('/opt/verdis-wallet/mobile/assets/images/verdis-logo-icon.png')
print(f'verdis-logo-icon.png: {logo_icon.size} mode={logo_icon.mode}')
px = logo_icon.load()
print(f'  corner(0,0)={px[0,0]} center={px[logo_icon.size[0]//2, logo_icon.size[1]//2]}')

# Check logo-white
logo_white = Image.open('/opt/verdis-wallet/mobile/assets/images/verdis-logo-white.png')
print(f'verdis-logo-white.png: {logo_white.size} mode={logo_white.mode}')
px2 = logo_white.load()
print(f'  corner(0,0)={px2[0,0]} center={px2[logo_white.size[0]//2, logo_white.size[1]//2]}')

# Create a proper 512x512 app icon
# Background: #040806 (Verdis dark)
# Logo: verdis-logo-icon.png centered, scaled to fit

ICON_SIZE = 512
BG_COLOR = (4, 8, 6, 255)  # #040806

icon = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), BG_COLOR)

# Paste the logo icon centered, scaled to 75% width
logo = Image.open('/opt/verdis-wallet/mobile/assets/images/verdis-logo-icon.png')
logo_ratio = logo.size[1] / logo.size[0]  # height/width
target_w = int(ICON_SIZE * 0.75)
target_h = int(target_w * logo_ratio)
if target_h > ICON_SIZE * 0.75:
    target_h = int(ICON_SIZE * 0.75)
    target_w = int(target_h / logo_ratio)

logo_resized = logo.resize((target_w, target_h), Image.LANCZOS)

# If logo has transparency, composite it
offset_x = (ICON_SIZE - target_w) // 2
offset_y = (ICON_SIZE - target_h) // 2
icon.paste(logo_resized, (offset_x, offset_y), logo_resized)

# Save as the new playstore icon
icon.save('/opt/verdis-wallet/mobile/assets/images/ic_launcher_playstore.png', 'PNG')
print(f'Created new ic_launcher_playstore.png: {icon.size}')

# Verify
px3 = icon.load()
print(f'  corner(0,0)={px3[0,0]} center={px3[256,256]}')
# Check a few points in the logo area
for y in [100, 200, 256, 300, 400]:
    row = []
    for x in [100, 200, 256, 300, 400]:
        row.append(str(px3[x,y]))
    joined = ' '.join(row)
    print(f'  y={y}: {joined}')

# Also create foreground for adaptive icons (transparent bg, logo centered)
fg = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
logo_fg = logo.resize((target_w, target_h), Image.LANCZOS)
fg.paste(logo_fg, (offset_x, offset_y), logo_fg)
fg.save('/tmp/ic_launcher_foreground_master.png', 'PNG')
print(f'Created foreground master: {fg.size}')

print('Done!')
