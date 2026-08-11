import os
from PIL import Image

base = "/opt/verdis-wallet/mobile/android/app/src/main/res"

# 1. Add roundIcon to AndroidManifest
manifest_path = f"{base}/../AndroidManifest.xml"
with open(manifest_path) as f:
    content = f.read()

if "android:roundIcon" not in content:
    content = content.replace(
        'android:icon="@mipmap/ic_launcher"',
        'android:icon="@mipmap/ic_launcher"\n        android:roundIcon="@mipmap/ic_launcher_round"'
    )
    with open(manifest_path, "w") as f:
        f.write(content)
    print("Added android:roundIcon to manifest")
else:
    print("roundIcon already present")

# 2. Create adaptive icon XML for API 26+
anydpi = f"{base}/mipmap-anydpi-v26"
os.makedirs(anydpi, exist_ok=True)

adaptive_xml = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
"""

with open(f"{anydpi}/ic_launcher.xml", "w") as f:
    f.write(adaptive_xml)
with open(f"{anydpi}/ic_launcher_round.xml", "w") as f:
    f.write(adaptive_xml)

# 3. Create foreground (the logo with padding for adaptive icon safe zone)
src = Image.open("/var/www/verdiscan/assets/favicon-512.png").convert("RGBA")
fg = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
logo_size = 285
logo_resized = src.resize((logo_size, logo_size), Image.LANCZOS)
offset = ((432 - logo_size) // 2, (432 - logo_size) // 2)
fg.paste(logo_resized, offset, logo_resized)

fg_sizes = {"mipmap-mdpi": 108, "mipmap-hdpi": 162, "mipmap-xhdpi": 216, "mipmap-xxhdpi": 324, "mipmap-xxxhdpi": 432}
for folder, size in fg_sizes.items():
    fg_resized = fg.resize((size, size), Image.LANCZOS)
    fg_resized.save(f"{base}/{folder}/ic_launcher_foreground.png", "PNG")
    print(f"  Foreground {folder}: {size}x{size} OK")

# 4. Create background color resource
colors_dir = f"{base}/values"
os.makedirs(colors_dir, exist_ok=True)
colors_path = f"{colors_dir}/colors.xml"

new_color_line = '    <color name="ic_launcher_background">#040806</color>\n'

if os.path.exists(colors_path):
    with open(colors_path) as f:
        colors_content = f.read()
    if "ic_launcher_background" not in colors_content:
        colors_content = colors_content.replace("</resources>", new_color_line + "</resources>")
        with open(colors_path, "w") as f:
            f.write(colors_content)
        print("Added ic_launcher_background to existing colors.xml")
    else:
        print("ic_launcher_background already in colors.xml")
else:
    with open(colors_path, "w") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n' + new_color_line + '</resources>\n')
    print("Created colors.xml with ic_launcher_background")

print("\nAll icon setup complete")
