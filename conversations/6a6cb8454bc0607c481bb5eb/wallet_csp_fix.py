#!/usr/bin/env python3
"""Fix three issues in the Verdis web wallet:
1. CSP blocks WebAssembly — add 'wasm-unsafe-eval' to script-src
2. Remove leftover debug diagnostic status bar from production
3. Add WASM warmup on page load so crypto is ready before user clicks
"""

import re

# Fix 1: nginx CSP — add wasm-unsafe-eval to /wallet location
nginx_conf = '/etc/nginx/sites-enabled/verdischain-com.conf'
with open(nginx_conf, 'r') as f:
    conf = f.read()

old_csp = "script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com"
new_csp = "script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com"

if old_csp in conf:
    conf = conf.replace(old_csp, new_csp)
    with open(nginx_conf, 'w') as f:
        f.write(conf)
    print("Fixed CSP: added 'wasm-unsafe-eval' to script-src for /wallet location")
else:
    print("WARNING: CSP pattern not found — may already be fixed or different format")

# Fix 2 & 3: wallet HTML — remove debug bar and add WASM warmup
wallet_file = '/var/www/verdiscan/wallet/index.html'
with open(wallet_file, 'r') as f:
    html = f.read()

# Also fix in git repo
git_wallet = '/opt/verdis-chain-rust/web/wallet/index.html'
with open(git_wallet, 'r') as f:
    git_html = f.read()

# Remove the diagnostic status bar block
debug_block_start = """// Diagnostic: check if functions are defined
window.addEventListener('load', function() {
  setTimeout(function() {
    var status = document.createElement('div');
    status.id = 'diag-status';
    status.style.cssText = 'position:fixed;bottom:10px;left:10px;background:#1a1a1a;color:#0f0;padding:12px;border-radius:8px;font-family:monospace;font-size:12px;z-index:99999;max-width:400px';
    var checks = [];
    checks.push('PolkadotCrypto: ' + (typeof window.PolkadotCrypto));
    checks.push('showCreate: ' + (typeof window.showCreate));
    checks.push('generateWallet: ' + (typeof window.generateWallet));
    checks.push('importWallet: ' + (typeof window.importWallet));
    status.textContent = checks.join(' | ');
    document.body.appendChild(status);
  }, 2000);
});"""

# Add WASM warmup right after the bundle script tag
warmup_code = """// Pre-warm WASM crypto on page load so it's ready before user clicks
window.addEventListener('load', function() {
  if (window.PolkadotCrypto && PolkadotCrypto.cryptoWaitReady) {
    PolkadotCrypto.cryptoWaitReady().then(function() {
      console.log('[Wallet] WASM crypto pre-warmed');
    }).catch(function(e) {
      console.error('[Wallet] WASM init failed:', e);
    });
  }
});"""

for label, content_dict in [("deployed", {"path": wallet_file, "content": html}),
                             ("git", {"path": git_wallet, "content": git_html})]:
    content = content_dict["content"]
    path = content_dict["path"]
    changes = []

    # Remove debug bar
    if debug_block_start in content:
        # Find the full script block containing this
        idx = content.index(debug_block_start)
        # Find the <script> tag before it
        script_open = content.rfind('<script>', 0, idx)
        # Find the </script> tag after it
        script_close = content.index('</script>', idx)
        content = content[:script_open] + content[script_close + len('</script>'):]
        changes.append("Removed debug diagnostic status bar")
    else:
        changes.append("Debug bar not found (may already be removed)")

    # Add WASM warmup after the bundle script tag
    bundle_tag = 'crossorigin="anonymous"></script>'
    if bundle_tag in content and warmup_code not in content:
        idx = content.index(bundle_tag) + len(bundle_tag)
        content = content[:idx] + '\n<script>\n' + warmup_code + '\n</script>' + content[idx:]
        changes.append("Added WASM pre-warmup on page load")
    else:
        changes.append("WASM warmup already present or bundle tag not found")

    with open(path, 'w') as f:
        f.write(content)
    print(f"[{label}] " + "; ".join(changes))
