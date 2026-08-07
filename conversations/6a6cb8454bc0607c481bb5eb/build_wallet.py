import sys

def build():
    # Build complete wallet HTML
    lines = []
    
    # Head
    lines.append('<!DOCTYPE html>')
    lines.append('<html lang="en">')
    lines.append('<head>')
    lines.append('  <meta charset="UTF-8" />')
    lines.append('  <meta name="viewport" content="width=device-width, initial-scale=1.0" />')
    lines.append('  <title>Verdis Chain — Web3 Non-Custodial Wallet</title>')
    lines.append('  <meta name="description" content="Non-custodial Web3 Wallet for Verdis Chain. Create, import, send, and receive VRDX tokens secured by local secp256k1 cryptography and AES-256 encryption." />')
    lines.append('  <meta property="og:type" content="website" />')
    lines.append('  <meta property="og:title" content="Verdis Chain — Non-Custodial Web3 Wallet" />')
    lines.append('  <meta property="og:description" content="Manage your VRDX tokens locally with secp256k1 & Substrate JS. Your keys, your tokens." />')
    lines.append('  <meta property="og:url" content="https://verdischain.com/wallet" />')
    lines.append('  <link rel="icon" type="image/png" href="/favicon-32.png" sizes="32x32" />')
    lines.append('')
    lines.append('  <!-- Fonts: Inter for Body, Space Grotesk for Headings, JetBrains Mono for Addresses & Numbers -->')
    lines.append('  <link rel="preconnect" href="https://fonts.googleapis.com" />')
    lines.append('  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />')
    lines.append('  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />')
    lines.append('')
    lines.append('  <!-- Crypto & QR Libraries -->')
    lines.append('  <script src="https://cdn.jsdelivr.net/npm/@noble/secp256k1@2.0.0/index.js"></script>')
    lines.append('  <script src="https://cdn.jsdelivr.net/npm/@noble/hashes@1.3.1/sha256.js"></script>')
    lines.append('  <script src="https://cdn.jsdelivr.net/npm/@noble/hashes@1.3.1/ripemd160.js"></script>')
    lines.append('  <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>')
    lines.append('  ')
    lines.append('  <!-- Polkadot JS Bundles -->')
    lines.append('  <script src="https://unpkg.com/@polkadot/util@12.5.1/bundle-polkadot-util.js"></script>')
    lines.append('  <script src="https://unpkg.com/@polkadot/util-crypto@12.5.1/bundle-polkadot-util-crypto.js"></script>')
    lines.append('  <script src="https://unpkg.com/@polkadot/keyring@12.5.1/bundle-polkadot-keyring.js"></script>')
    lines.append('  <script src="https://unpkg.com/@polkadot/types@10.9.1/bundle-polkadot-types.js"></script>')
    lines.append('  <script src="https://unpkg.com/@polkadot/api@10.9.1/bundle-polkadot-api.js"></script>')

    return "\n".join(lines)

print("Builder ready")
