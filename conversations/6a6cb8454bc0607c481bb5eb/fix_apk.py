#!/usr/bin/env python3
"""
Fix APK version mismatch:
- verdis-wallet.apk is actually v2.5.1 (confirmed from AndroidManifest.xml)
- Download page says v2.3.3
- Server Content-Disposition says v2.3.2
- Need to sync everything to v2.5.1
"""

import os, shutil, re

BASE = "/opt/verdis/app/dist/web"
SERVER = "/opt/verdis/app/dist/api/server.js"
changes = []

# 1. Create properly named v2.5.1 APK
src = f"{BASE}/verdis-wallet.apk"
dst = f"{BASE}/verdis-wallet-v2.5.1.apk"
if not os.path.exists(dst):
    shutil.copy2(src, dst)
    changes.append("Created verdis-wallet-v2.5.1.apk (copy of latest build)")
else:
    changes.append("verdis-wallet-v2.5.1.apk already exists")

# 2. Update download.html to show v2.5.1
with open(f"{BASE}/download.html") as f:
    content = f.read()

# Fix version text
content = content.replace("v2.3.3", "v2.5.1")
# Fix download link version param
content = content.replace("/verdis-wallet.apk?v=250", "/verdis-wallet.apk?v=251")
# Also fix any reference to v2.3.2 in download page
content = content.replace("v2.3.2", "v2.5.1")

with open(f"{BASE}/download.html", "w") as f:
    f.write(content)
changes.append("Updated download.html: v2.3.3 -> v2.5.1")

# 3. Update server.js routes
with open(SERVER) as f:
    server = f.read()

# Update the main /verdis-wallet.apk route to serve v2.5.1 filename
server = server.replace(
    'filename="verdis-wallet-v2.3.2.apk"',
    'filename="verdis-wallet-v2.5.1.apk"'
)

# Update the versioned route from v2.3.2 to v2.5.1
old_route = """this.app.get('/verdis-wallet-v2.3.2.apk', (req, res) => {
            const apkPath = path_1.default.resolve(__dirname, '../web/verdis-wallet-v2.3.2.apk');"""
new_route = """this.app.get('/verdis-wallet-v2.5.1.apk', (req, res) => {
            const apkPath = path_1.default.resolve(__dirname, '../web/verdis-wallet-v2.5.1.apk');"""
server = server.replace(old_route, new_route)

with open(SERVER, "w") as f:
    f.write(server)
changes.append("Updated server.js: routes now serve v2.5.1 filename")

# 4. Clean up old APK files (keep only the canonical ones)
old_apks = [
    f"{BASE}/verdis-wallet-v2.3.2.apk",
    f"{BASE}/verdis-wallet-v2.4.0.apk",
    f"{BASE}/verdis-wallet-v2.5.0.apk",
]
for old in old_apks:
    if os.path.exists(old):
        os.remove(old)
        changes.append(f"Removed old APK: {os.path.basename(old)}")

# 5. Update landing.html if it references the old version
with open(f"{BASE}/landing.html") as f:
    content = f.read()
if "v2.3.2" in content or "v2.3.3" in content:
    content = content.replace("v2.3.2", "v2.5.1").replace("v2.3.3", "v2.5.1")
    with open(f"{BASE}/landing.html", "w") as f:
        f.write(content)
    changes.append("Updated landing.html: old version -> v2.5.1")

# 6. Update any other HTML pages referencing old APK versions
for fname in os.listdir(BASE):
    if not fname.endswith(".html"):
        continue
    filepath = f"{BASE}/{fname}"
    with open(filepath) as f:
        content = f.read()
    modified = False
    for old_ver in ["v2.3.2", "v2.3.3", "v2.4.0", "v2.5.0"]:
        if old_ver in content and "download" not in fname:  # download.html already handled
            content = content.replace(old_ver, "v2.5.1")
            modified = True
    if modified:
        with open(filepath, "w") as f:
            f.write(content)
        changes.append(f"Updated {fname}: version refs -> v2.5.1")

print(f"\n=== {len(changes)} fixes applied ===")
for c in changes:
    print(f"  ✓ {c}")

# Verify final state
print("\n=== FINAL APK STATE ===")
for f in sorted(os.listdir(BASE)):
    if f.endswith(".apk"):
        size = os.path.getsize(f"{BASE}/{f}")
        print(f"  {f} ({size:,} bytes)")
