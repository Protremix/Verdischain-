from PIL import Image, ImageDraw, ImageFont
import os

# Create Twitter/X banner (1500x500)
banner = Image.new('RGB', (1500, 500), '#0d1117')
draw = ImageDraw.Draw(banner)

# Load the logo
logo = Image.open('/app/conversations/6a6cb8454bc0607c481bb5eb/verdis-logo-ai2.png')
logo.thumbnail((120, 120), Image.LANCZOS)
banner.paste(logo, (60, 190))

# Try to find a font
font_paths = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
]
font_large = None
font_small = None
for fp in font_paths:
    if os.path.exists(fp):
        font_large = ImageFont.truetype(fp, 48)
        font_small = ImageFont.truetype(fp, 24)
        break

if not font_large:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Title
draw.text((200, 180), "VERDIS", font=font_large, fill='#3fb950')
draw.text((200, 240), "The First Fully Green Blockchain Ecosystem", font=font_small, fill='#2dd4bf')

# Stats line
draw.text((200, 290), "Carbon-Negative Layer-1  •  On-Chain Carbon Credits  •  Native AMM DEX  •  DPoS", font=font_small, fill='#8b949e')

# URL
draw.text((200, 340), "verdischain.com", font=font_small, fill='#58a6ff')

banner.save('/app/conversations/6a6cb8454bc0607c481bb5eb/verdis-banner.png')
print('Banner created: 1500x500')

# Also create a square social profile pic (400x400) from the logo
pfp = Image.open('/app/conversations/6a6cb8454bc0607c481bb5eb/verdis-logo-ai2.png')
pfp.thumbnail((400, 400), Image.LANCZOS)
pfp.save('/app/conversations/6a6cb8454bc0607c481bb5eb/verdis-pfp.png')
print('Profile pic created: 400x400')
