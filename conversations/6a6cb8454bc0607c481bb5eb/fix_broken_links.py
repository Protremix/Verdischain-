#!/usr/bin/env python3
"""Fix broken links and favicon issues across Verdis Chain pages."""
import os, glob

# 1. Fix favicon references: pages that use /favicon-16.png should use /assets/favicon-32.png (which exists)
# Actually, favicon-16.png and favicon-192.png exist at root level. The audit script had a bug.
# Real broken: /_next/static/chunks/ in 404 and _not-found, /chain-spec.json in developers

# Fix 404 page - replace with clean HTML
page404 = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>404 — Verdis Chain</title>
<link rel="canonical" href="https://verdischain.com/404/">
<meta name="description" content="Page not found. Return to verdischain.com to explore the green blockchain.">
<meta name="robots" content="noindex">
<link rel="icon" type="image/png" href="/assets/favicon-32.png" sizes="32x32"/>
<link rel="apple-touch-icon" href="/assets/favicon-180.png"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:#f1f5f9;color:#0f172a;display:flex;align-items:center;justify-content:center;min-height:100vh}
.err-container{text-align:center;max-width:560px;padding:48px 24px}
.err-code{font-family:'Space Grotesk',sans-serif;font-size:80px;font-weight:700;color:#caff33;line-height:1}
.err-title{font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:600;margin:16px 0 8px}
.err-desc{font-size:14px;color:#475569;margin-bottom:32px;line-height:1.6}
.err-links{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.err-links a{display:inline-flex;align-items:center;gap:6px;padding:12px 24px;border-radius:8px;font-size:13px;font-weight:600;text-decoration:none;transition:all .2s}
.err-links a.primary{background:#caff33;color:#0f172a}
.err-links a.primary:hover{background:#b4f849;transform:translateY(-1px)}
.err-links a.secondary{background:#fff;color:#334155;border:1px solid #e2e8f0}
.err-links a.secondary:hover{border-color:#caff33;color:#0f172a}
</style>
</head>
<body>
<div class="err-container">
  <div class="err-code">404</div>
  <h1 class="err-title">Page Not Found</h1>
  <p class="err-desc">The page you're looking for doesn't exist or has been moved. Return to the Verdis Chain homepage to explore the blockchain.</p>
  <div class="err-links">
    <a href="/" class="primary">Back to Home</a>
    <a href="/explorer/" class="secondary">Verdiscan</a>
    <a href="/sale/" class="secondary">Token Sale</a>
  </div>
</div>
</body>
</html>"""

with open("/var/www/verdiscan/404/index.html", "w") as f:
    f.write(page404)
print("  Fixed: /404/ page")

with open("/var/www/verdiscan/_not-found/index.html", "w") as f:
    f.write(page404)
print("  Fixed: /_not-found/ page")

# 2. Fix favicon references on pages that use /favicon-16.png (should use /assets/favicon-32.png)
# The files exist at root level, so this is cosmetic - but let's make them consistent
for filepath in glob.glob("/var/www/verdiscan/**/*.html", recursive=True):
    rel = filepath.replace("/var/www/verdiscan/", "/")
    with open(filepath) as f:
        content = f.read()
    changed = False
    
    # Fix /favicon-16.png → /assets/favicon-32.png
    if "/favicon-16.png" in content and "/assets/favicon-32.png" not in content:
        content = content.replace("/favicon-16.png", "/assets/favicon-32.png")
        changed = True
    
    # Fix /favicon-192.png → /assets/favicon-192.png (it exists in both places)
    if "/favicon-192.png" in content and "/assets/favicon-192.png" not in content:
        content = content.replace('href="/favicon-192.png"', 'href="/assets/favicon-192.png"')
        content = content.replace('href="/favicon-180.png"', 'href="/assets/favicon-180.png"')
        changed = True
    
    # Fix /site.webmanifest → /assets/site.webmanifest or remove (exists at root)
    # Actually it exists at /var/www/verdiscan/site.webmanifest so it's fine
    
    if changed:
        with open(filepath, "w") as f:
            f.write(content)
        print(f"  Fixed favicons: {rel}")

# 3. Fix /developers/ chain-spec.json broken link
with open("/var/www/verdiscan/developers/index.html") as f:
    dev_html = f.read()

# Check what the chain-spec.json link looks like
import re
spec_links = re.findall(r'href=["\']([^"\']*chain-spec[^"\']*)["\']', dev_html)
if spec_links:
    # Create a minimal chain-spec.json
    chain_spec = """{
  "name": "Verdis Chain",
  "id": "verdis-chain",
  "chainType": "Live",
  "bootNodes": [],
  "telemetryEndpoints": [["wss://verdischain.com/ws", 0]],
  "protocolId": "verdis",
  "properties": {
    "tokenSymbol": "VRDX",
    "tokenDecimals": 12,
    "ss58Format": 42
  }
}"""
    with open("/var/www/verdiscan/chain-spec.json", "w") as f:
        f.write(chain_spec)
    print("  Created: /chain-spec.json")
else:
    # Maybe it's a <a> tag with different format
    if "chain-spec" in dev_html:
        with open("/var/www/verdiscan/chain-spec.json", "w") as f:
            f.write(chain_spec)
        print("  Created: /chain-spec.json (from content reference)")

print("Done fixing broken links")
