#!/usr/bin/env python3
"""Add APK download link to wallet page."""

with open('/opt/verdis-repo/dist/web/wallet/index.html', 'r') as f:
    content = f.read()

# Add APK download section after the auth cards
old = """<p>Import an existing wallet using your private key or 12-word mnemonic.</p>
</div>
</div>

<div class="import-form" id="createForm" style="display:none">"""

new = """<p>Import an existing wallet using your private key or 12-word mnemonic.</p>
</div>
</div>

<!-- Mobile App Download -->
<div class="auth-cards" style="margin-top:20px">
<a href="/wallet/verdis-wallet.apk" download class="auth-card" style="text-decoration:none;cursor:pointer">
<div class="icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00a86b" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg></div>
<h3>Download Android App</h3>
<p>Get the Verdis Wallet APK (28.8MB). Same BIP39 mnemonic, same address — synced with web wallet.</p>
</a>
</div>

<div class="import-form" id="createForm" style="display:none">"""

if old in content:
    content = content.replace(old, new, 1)
    with open('/opt/verdis-repo/dist/web/wallet/index.html', 'w') as f:
        f.write(content)
    print("Added APK download section")
else:
    print("ERROR: insertion point not found")
