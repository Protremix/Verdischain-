from PIL import Image, ImageDraw, ImageFont
import math

# Open the logo to find the symbol portion
logo = Image.open('/opt/verdis-wallet/mobile/assets/images/verdis-logo-icon.png')
print(f'Logo size: {logo.size}')

# The logo is 654x373. The symbol is on the left side.
# Let's crop the left 35% which should contain the eco/leaf symbol
# and analyze it
symbol_crop = logo.crop((0, 0, int(logo.size[0] * 0.35), logo.size[1]))
symbol_crop.save('/tmp/symbol_crop.png')
print(f'Symbol crop: {symbol_crop.size}')

# Check alpha values to find the actual content bounds
px = logo.load()
min_x, max_x, min_y, max_y = logo.size[0], 0, logo.size[1], 0
for y in range(logo.size[1]):
    for x in range(logo.size[0]):
        if px[x,y][3] > 10:  # alpha > 10
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
print(f'Content bounds: x={min_x}-{max_x}, y={min_y}-{max_y}')
print(f'Content size: {max_x-min_x}x{max_y-min_y}')

# Crop to content
content = logo.crop((min_x, min_y, max_x+1, max_y+1))
content.save('/tmp/logo_content.png')
print(f'Content crop: {content.size}')

# Now check: is there a symbol vs text split?
# Let's look at the leftmost 40% of content
content_w = content.size[0]
left_part = content.crop((0, 0, int(content_w * 0.35), content.size[1]))
left_part.save('/tmp/left_part.png')
print(f'Left part: {left_part.size}')

# Check alpha in left part
px2 = left_part.load()
has_content = False
for y in range(left_part.size[1]):
    for x in range(left_part.size[0]):
        if px2[x,y][3] > 10:
            has_content = True
            break
    if has_content:
        break
print(f'Left part has content: {has_content}')

# Find content bounds in left part
min_x2, max_x2, min_y2, max_y2 = left_part.size[0], 0, left_part.size[1], 0
for y in range(left_part.size[1]):
    for x in range(left_part.size[0]):
        if px2[x,y][3] > 10:
            min_x2 = min(min_x2, x)
            max_x2 = max(max_x2, x)
            min_y2 = min(min_y2, y)
            max_y2 = max(max_y2, y)
if has_content:
    print(f'Symbol bounds in left: x={min_x2}-{max_x2}, y={min_y2}-{max_y2}')
    symbol = left_part.crop((min_x2, min_y2, max_x2+1, max_y2+1))
    symbol.save('/tmp/symbol_only.png')
    print(f'Symbol only: {symbol.size}')

# Create the final icon: use the full content on dark background
ICON_SIZE = 512
BG_COLOR = (4, 8, 6, 255)  # #040806

# Method: Use the full logo content, scaled to fill 80% of the icon
icon = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), BG_COLOR)

content_w = content.size[0]
content_h = content.size[1]
# Scale to fit 80% of icon
scale = min((ICON_SIZE * 0.80) / content_w, (ICON_SIZE * 0.80) / content_h)
new_w = int(content_w * scale)
new_h = int(content_h * scale)
content_resized = content.resize((new_w, new_h), Image.LANCZOS)

# Center it
offset_x = (ICON_SIZE - new_w) // 2
offset_y = (ICON_SIZE - new_h) // 2
icon.paste(content_resized, (offset_x, offset_y), content_resized)

icon.save('/opt/verdis-wallet/mobile/assets/images/ic_launcher_playstore.png', 'PNG')
print(f'New playstore icon: {icon.size}')

# Create foreground (transparent bg, logo only)
fg = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
fg.paste(content_resized, (offset_x, offset_y), content_resized)
fg.save('/tmp/ic_launcher_foreground_master.png', 'PNG')
print(f'Foreground master: {fg.size}')

# Verify visibility
px3 = icon.load()
for y in [100, 200, 256, 300, 400]:
    row = []
    for x in [100, 200, 256, 300, 400]:
        row.append(str(px3[x,y]))
    joined = ' '.join(row)
    print(f'  y={y}: {joined}')

print('Done!')
