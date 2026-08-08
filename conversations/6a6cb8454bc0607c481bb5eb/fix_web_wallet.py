import json

# Read BIP39 words
with open('/tmp/bip39_words.txt') as f:
    words = [w.strip() for w in f.readlines() if w.strip()]

# Read web wallet
with open('/opt/verdis-repo/dist/web/wallet/index.html', 'r') as f:
    content = f.read()

# 1. Add BIP39 word list after the imports
bip39_js = "const BIP39_WORDS = [" + ",".join([f'"{w}"' for w in words]) + "];\n"

# Find the import section and add BIP39 + mnemonic generation
old_imports = "const SS58_PREFIX = 909;"
new_imports = bip39_js + "\n" + old_imports

if old_imports in content:
    content = content.replace(old_imports, new_imports)
    print("Added BIP39 word list")
else:
    print("ERROR: Could not find SS58_PREFIX line")

# 2. Add BIP39 mnemonic generation function after SS58 encoding
mnemonic_func = """
// ===== BIP39 Mnemonic Generation =====
function generateMnemonic() {
  // 128 bits = 16 bytes of entropy
  const entropy = new Uint8Array(16);
  crypto.getRandomValues(entropy);

  // SHA256 checksum (first 4 bits)
  const hash = sha256(entropy);
  const checksumByte = hash[0];
  const checksumBits = checksumByte >> 4; // first 4 bits

  // Combine entropy (128 bits) + checksum (4 bits) = 132 bits = 12 * 11 bits
  let bits = '';
  for (let i = 0; i < 16; i++) {
    bits += entropy[i].toString(2).padStart(8, '0');
  }
  bits += checksumBits.toString(2).padStart(4, '0');

  // Map 11-bit groups to words
  const mnemonic = [];
  for (let i = 0; i < 12; i++) {
    const index = parseInt(bits.substring(i * 11, (i + 1) * 11), 2);
    mnemonic.push(BIP39_WORDS[index]);
  }
  return mnemonic.join(' ');
}

// Derive SS58 address from mnemonic via server
async function deriveAddressFromMnemonic(mnemonic) {
  const response = await fetch('/api/tx-relay', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'derive-address', mnemonic: mnemonic })
  });
  const data = await response.json();
  if (data.ok && data.address) {
    return { address: data.address, publicKey: data.public_key };
  }
  throw new Error(data.error || 'Address derivation failed');
}

"""

# Insert after the ss58Encode function
old_save = "// ===== Wallet Functions ====="
new_save = mnemonic_func + "// ===== Wallet Functions ====="

if old_save in content:
    content = content.replace(old_save, new_save)
    print("Added BIP39 mnemonic generation function")
else:
    print("ERROR: Could not find Wallet Functions section")

# 3. Replace generateWallet to use BIP39 + server derivation
old_generate = """window.generateWallet = async function() {
  try {
    const privateKey = secp.utils.randomPrivateKey();
    const publicKey = secp.getPublicKey(privateKey, true); // compressed
    const privHex = Array.from(privateKey).map(b => b.toString(16).padStart(2, '0')).join('');
    const pubHex = Array.from(publicKey).map(b => b.toString(16).padStart(2, '0')).join('');
    const address = ss58Encode(publicKey, SS58_PREFIX);

    document.getElementById('newAddress').textContent = address;
    document.getElementById('newPrivKey').textContent = privHex;

    saveWallet(privHex, pubHex, address);
    toast('Wallet created! Saving to browser...', 'success');

    setTimeout(() => {
      loadDashboard();
    }, 1000);
  } catch (e) {
    toast('Failed to generate wallet: ' + e.message, 'error');
  }
};"""

new_generate = """window.generateWallet = async function() {
  try {
    const mnemonic = generateMnemonic();
    const { address, publicKey } = await deriveAddressFromMnemonic(mnemonic);

    document.getElementById('newAddress').textContent = address;
    document.getElementById('newPrivKey').textContent = mnemonic;
    document.getElementById('newPrivKeyLabel').textContent = 'Your 12-Word Mnemonic (SAVE THIS!)';

    // Store mnemonic locally (non-custodial)
    localStorage.setItem('verdis_wallet', JSON.stringify({
      mnemonic: mnemonic,
      publicKey: publicKey,
      address: address
    }));
    toast('Wallet created! Saving to browser...', 'success');

    setTimeout(() => {
      loadDashboard();
    }, 1000);
  } catch (e) {
    toast('Failed to generate wallet: ' + e.message, 'error');
  }
};"""

if old_generate in content:
    content = content.replace(old_generate, new_generate)
    print("Updated generateWallet with BIP39")
else:
    print("ERROR: Could not find generateWallet")

# 4. Replace importWallet to use server derivation
old_import_func = """window.importWallet = async function() {
  const input = document.getElementById('importInput').value.trim();
  if (!input) { toast('Please enter a private key or mnemonic', 'error'); return; }

  try {
    let privateKey;
    let mnemonic = null;

    if (input.includes(' ')) {
      // Mnemonic - generate seed from 12 words using sha256
      const words = input.split(/\\s+/);
      if (words.length !== 12) { toast('Mnemonic must be exactly 12 words', 'error'); return; }
      const seed = sha256(new TextEncoder().encode(input));
      privateKey = seed.slice(0, 32);
      mnemonic = input;
    } else {
      // Hex private key
      const hex = input.startsWith('0x') ? input.slice(2) : input;
      if (hex.length !== 64) { toast('Private key must be 32 bytes (64 hex chars)', 'error'); return; }
      privateKey = new Uint8Array(hex.match(/.{2}/g).map(b => parseInt(b, 16)));
    }

    const publicKey = secp.getPublicKey(privateKey, true);
    const privHex = Array.from(privateKey).map(b => b.toString(16).padStart(2, '0')).join('');
    const pubHex = Array.from(publicKey).map(b => b.toString(16).padStart(2, '0')).join('');
    const address = ss58Encode(publicKey, SS58_PREFIX);

    saveWallet(privHex, pubHex, address);
    toast('Wallet imported successfully!', 'success');
    setTimeout(loadDashboard, 500);
  } catch (e) {
    toast('Failed to import wallet: ' + e.message, 'error');
  }
};"""

new_import_func = """window.importWallet = async function() {
  const input = document.getElementById('importInput').value.trim();
  if (!input) { toast('Please enter a 12-word mnemonic', 'error'); return; }

  try {
    const words = input.split(/\\s+/);
    if (words.length !== 12) { toast('Mnemonic must be exactly 12 words', 'error'); return; }

    const { address, publicKey } = await deriveAddressFromMnemonic(input);

    localStorage.setItem('verdis_wallet', JSON.stringify({
      mnemonic: input,
      publicKey: publicKey,
      address: address
    }));
    toast('Wallet imported successfully!', 'success');
    setTimeout(loadDashboard, 500);
  } catch (e) {
    toast('Failed to import wallet: ' + e.message, 'error');
  }
};"""

if old_import_func in content:
    content = content.replace(old_import_func, new_import_func)
    print("Updated importWallet with server derivation")
else:
    print("ERROR: Could not find importWallet")
    # Try a simpler match
    if "window.importWallet" in content:
        print("importWallet exists but pattern didn't match")

# 5. Update saveWallet to use new format
old_save_wallet = """function saveWallet(privateKeyHex, publicKeyHex, address) {
    localStorage.setItem('verdis_wallet', JSON.stringify({
      privateKey: privateKeyHex,
      publicKey: publicKeyHex,
      address: address
    }));
  }"""

new_save_wallet = """function saveWallet(mnemonic, publicKey, address) {
    localStorage.setItem('verdis_wallet', JSON.stringify({
      mnemonic: mnemonic,
      publicKey: publicKey,
      address: address
    }));
  }"""

if old_save_wallet in content:
    content = content.replace(old_save_wallet, new_save_wallet)
    print("Updated saveWallet")
else:
    print("saveWallet pattern not found (may already be updated)")

with open('/opt/verdis-repo/dist/web/wallet/index.html', 'w') as f:
    f.write(content)

print("Web wallet updated with BIP39 + sr25519")
