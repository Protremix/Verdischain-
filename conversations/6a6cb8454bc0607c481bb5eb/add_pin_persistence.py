#!/usr/bin/env python3
"""
Add PIN-based wallet persistence so the wallet survives page refreshes.

Flow:
1. User creates/imports wallet → asked to set a PIN (4-6 digits)
2. Mnemonic is encrypted with PIN using AES-GCM → stored in localStorage
3. On page refresh → detect encrypted wallet → show PIN unlock screen
4. User enters PIN → mnemonic decrypted in memory → wallet restored
5. Auto-lock after 15 min inactivity (already implemented)
"""

PATH = "/var/www/verdiscan/wallet/index.html"

with open(PATH, "r") as f:
    html = f.read()

# 1. Add PIN unlock screen HTML (after the recover email form, before </script>)
# Find the auth section and add the PIN unlock card
pin_unlock_html = '''
<!-- PIN Unlock Screen (shown on page refresh if wallet is encrypted) -->
<div id="pinUnlockForm" style="display:none" class="auth-card">
  <div style="text-align:center;margin-bottom:20px">
    <div style="width:56px;height:56px;background:rgba(34,197,94,.1);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;margin-bottom:12px">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
    </div>
    <h3 style="font-size:20px;font-weight:700;color:var(--text-1);margin-bottom:6px">Unlock Wallet</h3>
    <p style="font-size:14px;color:var(--text-3);margin-bottom:20px">Enter your PIN to access your wallet</p>
    <div id="pinUnlockAddress" style="font-size:13px;color:var(--text-3);margin-bottom:16px;font-family:monospace"></div>
  </div>
  <div class="form-group">
    <label>PIN</label>
    <input type="password" id="pinUnlockInput" placeholder="Enter your PIN" maxlength="6"
      style="text-align:center;font-size:24px;letter-spacing:8px;font-weight:600"
      onkeydown="if(event.key==='Enter') unlockWithPin()">
  </div>
  <button onclick="unlockWithPin()" class="btn-primary" style="width:100%;margin-top:16px">Unlock →</button>
  <div id="pinUnlockError" style="display:none;color:#ef4444;font-size:13px;text-align:center;margin-top:12px"></div>
  <div style="text-align:center;margin-top:20px;padding-top:16px;border-top:1px solid #e2e8f0">
    <a href="/wallet/" onclick="forgetWalletOnDevice(event)" style="color:#ef4444;font-size:13px">Forgot PIN? Remove wallet from this device</a>
  </div>
</div>
'''

# Insert the PIN unlock form before the closing of auth section
# Find the backToAuth function which marks the end of auth-related HTML
insert_marker = "// ===== CLIENT-SIDE CRYPTO"
if "pinUnlockForm" not in html:
    html = html.replace(insert_marker, pin_unlock_html + "\n" + insert_marker)
    print("Added PIN unlock screen HTML")

# 2. Modify saveWallet to encrypt mnemonic with PIN and store in localStorage
old_save = """function saveWallet(mnemonic, publicKeyHex, address) {
  // Store ONLY public info in localStorage — NO mnemonic
  localStorage.setItem('verdis_wallet', JSON.stringify({
    publicKey: publicKeyHex,
    address: address,
    created: Date.now()
  }));
  // Keep mnemonic in memory only (lost on page refresh)
  _sessionMnemonic = mnemonic;
  _lastActivity = Date.now();
}"""

new_save = """function saveWallet(mnemonic, publicKeyHex, address) {
  // Store ONLY public info in localStorage — NO mnemonic
  localStorage.setItem('verdis_wallet', JSON.stringify({
    publicKey: publicKeyHex,
    address: address,
    created: Date.now()
  }));
  // Keep mnemonic in memory only (lost on page refresh)
  _sessionMnemonic = mnemonic;
  _lastActivity = Date.now();
}

// Save encrypted mnemonic with PIN for persistence across refreshes
async function saveWalletWithPin(mnemonic, publicKeyHex, address, pin) {
  const encrypted = await encryptMnemonic(mnemonic, pin);
  localStorage.setItem('verdis_wallet_encrypted', JSON.stringify({
    ciphertext: encrypted.ciphertext,
    salt: encrypted.salt,
    iv: encrypted.iv,
    publicKey: publicKeyHex,
    address: address,
    created: Date.now()
  }));
  // Also store public info for quick access
  localStorage.setItem('verdis_wallet', JSON.stringify({
    publicKey: publicKeyHex,
    address: address,
    created: Date.now()
  }));
  _sessionMnemonic = mnemonic;
  _lastActivity = Date.now();
}

// Load encrypted wallet metadata (without decrypting)
function loadEncryptedWallet() {
  try {
    const data = localStorage.getItem('verdis_wallet_encrypted');
    if (!data) return null;
    return JSON.parse(data);
  } catch { return null; }
}

// Unlock wallet with PIN (called on page refresh)
async function unlockWithPin() {
  const pin = document.getElementById('pinUnlockInput').value.trim();
  const errEl = document.getElementById('pinUnlockError');
  errEl.style.display = 'none';

  if (!pin || pin.length < 4) {
    errEl.textContent = 'PIN must be at least 4 digits';
    errEl.style.display = 'block';
    return;
  }

  try {
    const enc = loadEncryptedWallet();
    if (!enc) { errEl.textContent = 'No encrypted wallet found'; errEl.style.display = 'block'; return; }

    const mnemonic = await decryptMnemonic(enc.ciphertext, enc.salt, enc.iv, pin);
    await unlockWallet(mnemonic);
    toast('Wallet unlocked!', 'success');

    // Hide PIN screen, show dashboard
    document.getElementById('pinUnlockForm').style.display = 'none';
    document.getElementById('authCards').style.display = 'none';
    setTimeout(loadDashboard, 300);
  } catch (e) {
    errEl.textContent = 'Wrong PIN. Try again.';
    errEl.style.display = 'block';
    document.getElementById('pinUnlockInput').value = '';
    document.getElementById('pinUnlockInput').focus();
  }
}
window.unlockWithPin = unlockWithPin;

// Show PIN unlock screen on refresh
function showPinUnlock() {
  const enc = loadEncryptedWallet();
  if (!enc) return false;

  document.getElementById('authCards').style.display = 'none';
  document.getElementById('createForm').style.display = 'none';
  document.getElementById('importForm').style.display = 'none';
  document.getElementById('pinUnlockForm').style.display = 'block';

  const addrEl = document.getElementById('pinUnlockAddress');
  if (addrEl && enc.address) {
    addrEl.textContent = enc.address.substring(0, 10) + '...' + enc.address.substring(enc.address.length - 8);
  }

  setTimeout(() => document.getElementById('pinUnlockInput').focus(), 100);
  return true;
}

// Forget wallet on this device (clears encrypted mnemonic)
function forgetWalletOnDevice(e) {
  if (e) e.preventDefault();
  if (confirm('This will remove your wallet from this browser. Make sure you have your 12-word mnemonic saved!')) {
    localStorage.removeItem('verdis_wallet_encrypted');
    localStorage.removeItem('verdis_wallet');
    lockWallet();
    location.reload();
  }
}
window.forgetWalletOnDevice = forgetWalletOnDevice;

// Clear encrypted wallet too
const _originalClearWallet = clearWallet;
clearWallet = function() {
  localStorage.removeItem('verdis_wallet_encrypted');
  localStorage.removeItem('verdis_wallet');
  lockWallet();
};"""

if "saveWalletWithPin" not in html:
    html = html.replace(old_save, new_save)
    print("Added saveWalletWithPin, unlockWithPin, showPinUnlock, forgetWalletOnDevice")

# 3. Add PIN input to create wallet form
# Find the create form and add a PIN field before the Enter Wallet button
old_create_btn = 'enterWalletBtn'
# Let's find the create form section
# Look for the "Enter Wallet" button area
pin_create_field = '''
    <div class="form-group" id="createPinGroup" style="margin-top:16px">
      <label>Set a PIN (4-6 digits) — needed to unlock after refresh</label>
      <input type="password" id="createPinInput" placeholder="e.g. 1234" maxlength="6"
        style="text-align:center;font-size:20px;letter-spacing:6px;font-weight:600"
        oninput="this.value=this.value.replace(/[^0-9]/g,'')">
      <p style="font-size:12px;color:#6b7280;margin-top:4px">This PIN encrypts your wallet locally. Without it, your wallet can't be restored on this device.</p>
    </div>
'''

# Find where to insert - before the Enter Wallet button in the create form
# Look for the enterWalletBtn
if "createPinInput" not in html:
    # Find the create form area - look for the Enter Wallet button
    enter_marker = 'id="enterWalletBtn"'
    if enter_marker in html:
        # Insert PIN field before the button
        idx = html.find(enter_marker)
        # Go back to find the start of the line
        line_start = html.rfind('\n', 0, idx)
        html = html[:line_start+1] + pin_create_field + html[line_start+1:]
        print("Added PIN input to create wallet form")
    else:
        print("WARNING: Could not find enterWalletBtn to add PIN field")

# 4. Modify enterWallet() to require PIN
old_enter = "function enterWallet() { loadDashboard(); }"
new_enter = """async function enterWallet() {
  const pinEl = document.getElementById('createPinInput');
  if (pinEl) {
    const pin = pinEl.value.trim();
    if (!pin || pin.length < 4) {
      toast('Please set a PIN (4-6 digits) to protect your wallet', 'error');
      pinEl.focus();
      return;
    }
    // Encrypt mnemonic with PIN and store for persistence
    try {
      await saveWalletWithPin(_sessionMnemonic,
        Array.from(_sessionKeypair.publicKey).map(b => b.toString(16).padStart(2,'0')).join(''),
        _sessionKeypair.address, pin);
      toast('Wallet secured with PIN. It will persist across refreshes.', 'success');
    } catch (e) {
      toast('PIN encryption failed: ' + e.message, 'error');
      return;
    }
  }
  loadDashboard();
}"""

if "async function enterWallet" not in html:
    html = html.replace(old_enter, new_enter)
    print("Modified enterWallet to require PIN")

# 5. Add PIN input to import wallet form
pin_import_field = '''
    <div class="form-group" style="margin-top:16px">
      <label>Set a PIN (4-6 digits) — needed to unlock after refresh</label>
      <input type="password" id="importPinInput" placeholder="e.g. 1234" maxlength="6"
        style="text-align:center;font-size:20px;letter-spacing:6px;font-weight:600"
        oninput="this.value=this.value.replace(/[^0-9]/g,'')">
      <p style="font-size:12px;color:#6b7280;margin-top:4px">This PIN encrypts your wallet locally for persistence across page refreshes.</p>
    </div>
'''

# Find the import form - look for the import button
if "importPinInput" not in html:
    # Find the import button onclick
    import_marker = 'onclick="importWallet()"'
    if import_marker in html:
        idx = html.find(import_marker)
        line_start = html.rfind('\n', 0, idx)
        html = html[:line_start+1] + pin_import_field + html[line_start+1:]
        print("Added PIN input to import wallet form")

# 6. Modify importWallet to use PIN
old_import = """    saveWallet(input, publicKey, address);
    await unlockWallet(input); // derives keypair again and sets _sessionMnemonic/_sessionKeypair correctly
    toast('Wallet imported successfully!', 'success');
    setTimeout(loadDashboard, 500);"""

new_import = """    saveWallet(input, publicKey, address);
    await unlockWallet(input); // derives keypair again and sets _sessionMnemonic/_sessionKeypair correctly

    // Check if user set a PIN
    const pinEl = document.getElementById('importPinInput');
    if (pinEl) {
      const pin = pinEl.value.trim();
      if (pin && pin.length >= 4) {
        try {
          await saveWalletWithPin(input, publicKey, address, pin);
          toast('Wallet imported and secured with PIN!', 'success');
        } catch (e) {
          toast('Wallet imported, but PIN encryption failed: ' + e.message, 'error');
        }
      } else {
        toast('Wallet imported. Set a PIN next time to persist across refreshes.', 'info');
      }
    } else {
      toast('Wallet imported successfully!', 'success');
    }
    setTimeout(loadDashboard, 500);"""

if "importPinInput" not in html or old_import in html:
    html = html.replace(old_import, new_import)
    print("Modified importWallet to use PIN")

# 7. Modify the page load handler to check for encrypted wallet
old_load = """window.addEventListener('load', () => {
  const wallet = loadWallet();
  if (wallet) {
    loadDashboard();
  }

  // Fetch block height for nav
  rpcCall('chain_getHeader', []).then(header => {
    if (header && header.number) {
      document.getElementById('navStatus').textContent = `Block #${parseInt(header.number, 16)}`;
    }
  });
});"""

new_load = """window.addEventListener('load', () => {
  // Check if wallet is encrypted (needs PIN to unlock)
  const enc = loadEncryptedWallet();
  if (enc) {
    // Wallet exists but needs PIN to unlock
    showPinUnlock();
  } else {
    // No encrypted wallet, check if wallet is in memory (fresh create)
    const wallet = loadWallet();
    if (wallet) {
      loadDashboard();
    }
  }

  // Fetch block height for nav
  rpcCall('chain_getHeader', []).then(header => {
    if (header && header.number) {
      document.getElementById('navStatus').textContent = `Block #${parseInt(header.number, 16)}`;
    }
  });
});"""

if "loadEncryptedWallet()" not in html.split("window.addEventListener('load'")[1][:500] if "window.addEventListener('load'" in html else "":
    html = html.replace(old_load, new_load)
    print("Modified page load handler to check for encrypted wallet")

# 8. Modify logout to also clear encrypted wallet
old_logout = """window.logout = function() {
  if (confirm('Remove wallet from this browser? Make sure you have your private key saved!')) {
    clearWallet();
    location.reload();
  }
};"""

new_logout = """window.logout = function() {
  if (confirm('Remove wallet from this browser? Make sure you have your 12-word mnemonic saved!')) {
    localStorage.removeItem('verdis_wallet_encrypted');
    localStorage.removeItem('verdis_wallet');
    lockWallet();
    location.reload();
  }
};"""

if old_logout in html:
    html = html.replace(old_logout, new_logout)
    print("Modified logout to clear encrypted wallet")

with open(PATH, "w") as f:
    f.write(html)

print("\nDone! PIN-based wallet persistence added.")
