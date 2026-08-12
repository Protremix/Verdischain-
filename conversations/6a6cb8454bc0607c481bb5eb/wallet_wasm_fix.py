#!/usr/bin/env python3
"""Fix two web wallet bugs:
1. generateMnemonic() calls PolkadotCrypto.mnemonicGenerate() without awaiting cryptoWaitReady() first
   -> 'WASM interface has not been initialized' error on fresh/slow page loads.
2. importWallet() references undefined `kp` variable -> ReferenceError, breaks every import.
"""

f = '/opt/verdis-chain-rust/web/wallet/index.html'
with open(f, 'r') as fh:
    content = fh.read()

changes = []

# Fix 1: generateMnemonic must wait for WASM before calling mnemonicGenerate()
old_gen = """async function generateMnemonic() {
  // Use Polkadot's built-in BIP39 mnemonic generator (guaranteed compatible with Keyring)
  if (window.PolkadotCrypto && PolkadotCrypto.mnemonicGenerate) {
    return PolkadotCrypto.mnemonicGenerate();
  }"""

new_gen = """async function generateMnemonic() {
  // Use Polkadot's built-in BIP39 mnemonic generator (guaranteed compatible with Keyring)
  if (window.PolkadotCrypto && PolkadotCrypto.mnemonicGenerate) {
    await PolkadotCrypto.cryptoWaitReady();
    return PolkadotCrypto.mnemonicGenerate();
  }"""

if old_gen in content:
    content = content.replace(old_gen, new_gen)
    changes.append('Fixed generateMnemonic(): now awaits cryptoWaitReady() before mnemonicGenerate()')
else:
    changes.append('ERROR: could not find generateMnemonic() pattern')

# Fix 2: importWallet references undefined `kp` - use unlockWallet() helper instead
old_import = """window.importWallet = async function() {
  const input = document.getElementById('importInput').value.trim();
  if (!input) { toast('Please enter a 12-word mnemonic', 'error'); return; }

  try {
    const words = input.split(/\\s+/);
    if (words.length !== 12) { toast('Mnemonic must be exactly 12 words', 'error'); return; }

    const { address, publicKey } = await deriveAddressFromMnemonic(input);

    saveWallet(input, publicKey, address);
    _sessionKeypair = kp;
    toast('Wallet imported successfully!', 'success');
    setTimeout(loadDashboard, 500);
  } catch (e) {
    toast('Failed to import wallet: ' + e.message, 'error');
  }
};"""

new_import = """window.importWallet = async function() {
  const input = document.getElementById('importInput').value.trim();
  if (!input) { toast('Please enter a 12-word mnemonic', 'error'); return; }

  try {
    const words = input.split(/\\s+/);
    if (words.length !== 12) { toast('Mnemonic must be exactly 12 words', 'error'); return; }

    const { address, publicKey } = await deriveAddressFromMnemonic(input);

    saveWallet(input, publicKey, address);
    await unlockWallet(input); // derives keypair again and sets _sessionMnemonic/_sessionKeypair correctly
    toast('Wallet imported successfully!', 'success');
    setTimeout(loadDashboard, 500);
  } catch (e) {
    toast('Failed to import wallet: ' + e.message, 'error');
  }
};"""

if old_import in content:
    content = content.replace(old_import, new_import)
    changes.append('Fixed importWallet(): replaced undefined `kp` reference with unlockWallet(input) call')
else:
    changes.append('ERROR: could not find importWallet() pattern')

with open(f, 'w') as fh:
    fh.write(content)

for c in changes:
    print(c)
