from PIL import Image, ImageDraw

ICON_SIZE = 512
BG_COLOR = (4, 8, 6, 255)  # #040806

# Load the symbol-only crop
symbol = Image.open('/tmp/symbol_only.png')
print(f'Symbol: {symbol.size}')

# Create icon with just the symbol, scaled to 70% of the icon
icon = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), BG_COLOR)

sym_w, sym_h = symbol.size
scale = (ICON_SIZE * 0.70) / max(sym_w, sym_h)
new_w = int(sym_w * scale)
new_h = int(sym_h * scale)
sym_resized = symbol.resize((new_w, new_h), Image.LANCZOS)

offset_x = (ICON_SIZE - new_w) // 2
offset_y = (ICON_SIZE - new_h) // 2
icon.paste(sym_resized, (offset_x, offset_y), sym_resized)

icon.save('/tmp/icon_symbol_only.png')
print(f'Symbol icon: {icon.size}')

# Also try: logo-white.png which is more square (654x603)
logo_white = Image.open('/opt/verdis-wallet/mobile/assets/images/verdis-logo-white.png')
print(f'Logo white: {logo_white.size}')

# Find content bounds
px = logo_white.load()
min_x, max_x, min_y, max_y = logo_white.size[0], 0, logo_white.size[1], 0
for y in range(logo_white.size[1]):
    for x in range(logo_white.size[0]):
        if px[x,y][3] > 10:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
print(f'White logo content: x={min_x}-{max_x}, y={min_y}-{max_y}, size={max_x-min_x}x{max_y-min_y}')

content = logo_white.crop((min_x, min_y, max_x+1, max_y+1))
content_w, content_h = content.size
scale2 = min((ICON_SIZE * 0.80) / content_w, (ICON_SIZE * 0.80) / content_h)
new_w2 = int(content_w * scale2)
new_h2 = int(content_h * scale2)
content_resized = content.resize((new_w2, new_h2), Image.LANCZOS)

icon2 = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), BG_COLOR)
offset_x2 = (ICON_SIZE - new_w2) // 2
offset_y2 = (ICON_SIZE - new_h2) // 2
icon2.paste(content_resized, (offset_x2, offset_y2), content_resized)
icon2.save('/tmp/icon_white_logo.png')
print(f'White logo icon: {icon2.size}')

print('Done!')
