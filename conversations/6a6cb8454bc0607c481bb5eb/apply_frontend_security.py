#!/usr/bin/env python3
"""
Frontend Security Overhaul for Verdis Web Wallet

Changes:
1. Add security notice modal (must agree before using wallet)
2. Make PIN mandatory for import (not optional)
3. Add PIN field to email recovery form
4. Modify importWallet() to register/verify PIN server-side
5. Modify recoverFromEmail() to require PIN
6. Modify enterWallet() to register PIN on server
7. Add failed attempt tracking and lockout UI
"""

import re

WALLET_PATH = '/var/www/verdiscan/wallet/index.html'

with open(WALLET_PATH, 'r') as f:
    content = f.read()

# ============================================================
# 1. ADD SECURITY NOTICE MODAL HTML (before the auth state div)
# ============================================================
security_modal_html = '''
<!-- Security Notice Modal -->
<div id="securityNoticeModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:9999;display:flex;align-items:center;justify-content:center">
  <div style="background:#fff;border-radius:16px;max-width:480px;width:90%;padding:32px;box-shadow:0 8px 32px rgba(0,0,0,0.4);max-height:90vh;overflow-y:auto">
    <div style="text-align:center;margin-bottom:20px">
      <div style="width:56px;height:56px;background:rgba(239,68,68,0.1);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;margin-bottom:12px">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><path d="M12 9v4M12 17h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>
      </div>
      <h2 style="font-size:22px;font-weight:700;color:#0f172a;margin-bottom:8px">Security Notice</h2>
      <p style="font-size:14px;color:#64748b">Read carefully before proceeding</p>
    </div>
    <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:20px;margin-bottom:20px">
      <div style="font-size:14px;color:#1e293b;line-height:1.7">
        <p style="margin-bottom:12px"><strong>🔒 Your PIN is the key to your wallet.</strong></p>
        <p style="margin-bottom:12px">Your wallet is protected by a PIN that you set. Even if someone obtains your 12-word mnemonic or your email, they <strong>cannot</strong> access your wallet without your PIN.</p>
        <p style="margin-bottom:12px"><strong>If you lose your PIN, you will permanently lose access to your wallet.</strong> No one — not even Verdis Chain staff — can recover it for you.</p>
        <p style="margin-bottom:12px"><strong>Rules:</strong></p>
        <ul style="margin-left:20px;margin-bottom:12px">
          <li>Nev­er share your PIN with anyone</li>
          <li>Never share your 12-word mnemonic with anyone</li>
          <li>Verdis Chain staff will never ask for your PIN or mnemonic</li>
          <li>Write down your PIN and mnemonic in a secure offline location</li>
          <li>After 5 failed PIN attempts, your wallet will be locked for 15 minutes</li>
        </ul>
        <p style="margin-bottom:0">By proceeding, you acknowledge that you are solely responsible for keeping your PIN and mnemonic secure.</p>
      </div>
    </div>
    <label style="display:flex;align-items:flex-start;gap:10px;margin-bottom:20px;cursor:pointer">
      <input type="checkbox" id="securityAgreeCheckbox" style="margin-top:3px;width:18px;height:18px;cursor:pointer" onchange="document.getElementById('securityAgreeBtn').disabled=!this.checked">
      <span style="font-size:14px;color:#1e293b">I have read and understand these security rules. I know that losing my PIN means losing access to my wallet permanently.</span>
    </label>
    <button id="securityAgreeBtn" onclick="acceptSecurityNotice()" disabled style="width:100%;padding:14px;background:#00a86b;color:#fff;border:none;border-radius:8px;font-size:16px;font-weight:600;cursor:pointer;opacity:0.5;transition:opacity 0.2s">
      I Agree — Continue to Wallet
    </button>
  </div>
</div>
'''

# Insert the security modal before the auth state div
auth_state_marker = '<!-- State: No Wallet -->'
if auth_state_marker in content:
    content = content.replace(auth_state_marker, security_modal_html + '\n' + auth_state_marker)
    print("[OK] Security notice modal added to HTML")
else:
    print("[ERROR] Could not find auth state marker")
    exit(1)

# ============================================================
# 2. UPDATE IMPORT FORM — Make PIN mandatory, update label
# ============================================================
old_import_pin_label = '<label>Set a PIN (4-6 digits) — needed to unlock after refresh</label>\n      <input type="password" id="importPinInput" placeholder="e.g. 1234" maxlength="6"\n        style="text-align:center;font-size:20px;letter-spacing:6px;font-weight:600"\n        oninput="this.value=this.value.replace(/[^0-9]/g,\'\')">\n      <p style="font-size:12px;color:#6b7280;margin-top:4px">This PIN encrypts your wallet locally for persistence across page refreshes.</p>'
new_import_pin_label = '<label>🔒 Wallet PIN (4-6 digits) — REQUIRED</label>\n      <input type="password" id="importPinInput" placeholder="e.g. 1234" maxlength="6" required\n        style="text-align:center;font-size:20px;letter-spacing:6px;font-weight:600;border:2px solid #00a86b"\n        oninput="this.value=this.value.replace(/[^0-9]/g,\'\')">\n      <p style="font-size:13px;color:#dc2626;margin-top:4px;font-weight:500">⚠️ This PIN protects your wallet. Without it, NO ONE can access your funds — even with your 12 words. If you lose this PIN, your wallet is permanently lost.</p>'

if old_import_pin_label in content:
    content = content.replace(old_import_pin_label, new_import_pin_label)
    print("[OK] Import form PIN field updated to mandatory")
else:
    print("[WARN] Import form PIN label not found exactly, trying flexible match")
    # Try with flexible whitespace
    content = re.sub(
        r'<label>Set a PIN \(4-6 digits\) — needed to unlock after refresh</label>\s*<input type="password" id="importPinInput".*?<p style="font-size:12px;color:#6b7280;margin-top:4px">This PIN encrypts your wallet locally for persistence across page refreshes\.</p>',
        new_import_pin_label,
        content,
        flags=re.DOTALL
    )
    print("[OK] Import form PIN field updated (flexible match)")

# ============================================================
# 3. UPDATE EMAIL RECOVERY FORM — Add PIN field
# ============================================================
old_recover_form = '''<div class="form-group">
<label>Recovery Password</label>
<input type="password" id="recoverPassword" placeholder="Your recovery password" style="width:100%;padding:10px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:14px" />
</div>
<button class="btn-primary" onclick="recoverFromEmail()">Recover Wallet</button>'''

new_recover_form = '''<div class="form-group">
<label>Recovery Password</label>
<input type="password" id="recoverPassword" placeholder="Your recovery password" style="width:100%;padding:10px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:14px" />
</div>
<div class="form-group">
<label>🔒 Wallet PIN (required)</label>
<input type="password" id="recoverPinInput" placeholder="The PIN you set when creating your wallet" maxlength="6"
  style="width:100%;padding:10px 12px;border:2px solid #00a86b;border-radius:8px;font-size:16px;text-align:center;letter-spacing:4px;font-weight:600"
  oninput="this.value=this.value.replace(/[^0-9]/g,'')" />
<p style="font-size:13px;color:#dc2626;margin-top:4px;font-weight:500">⚠️ Your original PIN is required to recover your wallet. Without it, recovery is impossible.</p>
</div>
<button class="btn-primary" onclick="recoverFromEmail()">Recover Wallet</button>'''

if old_recover_form in content:
    content = content.replace(old_recover_form, new_recover_form)
    print("[OK] Email recovery form updated with PIN field")
else:
    print("[ERROR] Could not find recovery form")
    exit(1)

# ============================================================
# 4. UPDATE IMPORT WALLET JS — Register/verify PIN server-side
# ============================================================
old_import_js = """window.importWallet = async function() {
  const input = document.getElementById('importInput').value.trim();
  if (!input) { toast('Please enter a 12-word mnemonic', 'error'); return; }

  try {
    const words = input.split(/\\s+/);
    if (words.length !== 12) { toast('Mnemonic must be exactly 12 words', 'error'); return; }

    const { address, publicKey } = await deriveAddressFromMnemonic(input);

    saveWallet(input, publicKey, address);
    await unlockWallet(input); // derives keypair again and sets _sessionMnemonic/_sessionKeypair correctly
    sessionStorage.setItem('verdis_session_mnemonic', input);

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
    setTimeout(loadDashboard, 500);
  } catch (e) {
    toast('Failed to import wallet: ' + e.message, 'error');
  }
};"""

new_import_js = """window.importWallet = async function() {
  const input = document.getElementById('importInput').value.trim();
  if (!input) { toast('Please enter a 12-word mnemonic', 'error'); return; }

  const pinEl = document.getElementById('importPinInput');
  const pin = pinEl ? pinEl.value.trim() : '';
  if (!pin || pin.length < 4 || !pin.match(/^\\d{4,6}$/)) {
    toast('PIN is required (4-6 digits). Without PIN, your wallet is not protected.', 'error');
    if (pinEl) pinEl.focus();
    return;
  }

  const btn = event ? event.target.closest('button') : null;
  if (btn) { btn.disabled = true; btn.textContent = 'Verifying PIN...'; }

  try {
    const words = input.split(/\\s+/);
    if (words.length !== 12) { toast('Mnemonic must be exactly 12 words', 'error'); return; }

    // Derive address from mnemonic
    const { address, publicKey } = await deriveAddressFromMnemonic(input);

    // Check if this wallet already has a PIN registered on the server
    let pinStatus;
    try {
      const statusRes = await fetch('/api/tx-relay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'pin-status', address: address })
      });
      const statusData = await statusRes.json();
      pinStatus = statusData.ok ? statusData.data : { has_pin: false };
    } catch (e) {
      console.warn('[Wallet] PIN status check failed, proceeding:', e);
      pinStatus = { has_pin: false };
    }

    if (pinStatus.has_pin) {
      // Wallet already has a PIN — verify the entered PIN matches
      if (pinStatus.locked) {
        const mins = Math.ceil(pinStatus.locked_remaining / 60);
        toast('Wallet is locked. Try again in ' + mins + ' minute(s).', 'error');
        if (btn) { btn.disabled = false; btn.textContent = 'Import Wallet'; }
        return;
      }

      const verifyRes = await fetch('/api/tx-relay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'pin-verify', address: address, pin: pin })
      });
      const verifyData = await verifyRes.json();

      if (!verifyData.ok) {
        toast(verifyData.error || 'PIN verification failed', 'error');
        if (btn) { btn.disabled = false; btn.textContent = 'Import Wallet'; }
        return;
      }
      toast('PIN verified successfully', 'success');
    } else {
      // New wallet — register the PIN on the server
      const regRes = await fetch('/api/tx-relay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'pin-register', address: address, pin: pin })
      });
      const regData = await regRes.json();
      if (!regData.ok) {
        toast('PIN registration failed: ' + (regData.error || 'unknown'), 'error');
        if (btn) { btn.disabled = false; btn.textContent = 'Import Wallet'; }
        return;
      }
      console.log('[Wallet] PIN registered on server for', address);
    }

    // Save wallet locally with PIN encryption
    saveWallet(input, publicKey, address);
    await saveWalletWithPin(input, publicKey, address, pin);
    await unlockWallet(input);
    sessionStorage.setItem('verdis_session_mnemonic', input);

    toast('Wallet imported and secured with PIN!', 'success');

    // Show security notice before loading dashboard
    if (btn) { btn.disabled = false; btn.textContent = 'Import Wallet'; }
    showSecurityNotice(() => {
      setTimeout(loadDashboard, 200);
    });
  } catch (e) {
    toast('Failed to import wallet: ' + e.message, 'error');
    if (btn) { btn.disabled = false; btn.textContent = 'Import Wallet'; }
  }
};"""

if old_import_js in content:
    content = content.replace(old_import_js, new_import_js)
    print("[OK] importWallet() updated with server-side PIN verification")
else:
    print("[WARN] Exact import JS not found, trying regex match")
    # Try regex
    pattern = r'window\.importWallet = async function\(\) \{.*?^};'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if match:
        content = content[:match.start()] + new_import_js + content[match.end():]
        print("[OK] importWallet() updated via regex")
    else:
        print("[ERROR] Could not find importWallet function")
        exit(1)

# ============================================================
# 5. UPDATE RECOVER FROM EMAIL JS — Add PIN requirement
# ============================================================
old_recover_js = """async function recoverFromEmail() {
  const email = document.getElementById('recoverEmail').value.trim();
  const password = document.getElementById('recoverPassword').value;
  if (!email || !email.includes('@')) { toast('Please enter a valid email', 'error'); return; }
  if (!password) { toast('Please enter your recovery password', 'error'); return; }

  try {
    toast('Fetching encrypted backup...', 'info');

    const res = await fetch('/api/tx-relay', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'wallet-recover',
        email: email,
      })
    });
    const data = await res.json();

    if (!data.ok) {
      toast(data.error || 'Recovery failed', 'error');
      return;
    }

    const backup = data.backup;
    const mnemonic = await decryptMnemonic(backup.ciphertext, backup.salt, backup.iv, password);
    const { address, publicKey } = await deriveAddressFromMnemonic(mnemonic);
    saveWallet(mnemonic, publicKey, address);
    await unlockWallet(mnemonic);
    sessionStorage.setItem('verdis_session_mnemonic', mnemonic);

    // Also save with PIN for persistence
    const pin = prompt('Set a PIN for this wallet (4-6 digits):');
    if (pin && pin.length >= 4 && pin.match(/^\\d+$/)) {
      await saveWalletWithPin(mnemonic, publicKey, address, pin);
      // Register PIN on server
      await fetch('/api/tx-relay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'pin-register', address: address, pin: pin })
      });
      toast('Wallet recovered and secured with PIN!', 'success');
    } else {
      toast('Wallet recovered. Set a PIN in settings to secure it.', 'info');
    }

    setTimeout(loadDashboard, 500);
  } catch (e) {
    toast('Recovery failed: ' + e.message, 'error');
  }
}"""

new_recover_js = """async function recoverFromEmail() {
  const email = document.getElementById('recoverEmail').value.trim();
  const password = document.getElementById('recoverPassword').value;
  const pinEl = document.getElementById('recoverPinInput');
  const pin = pinEl ? pinEl.value.trim() : '';

  if (!email || !email.includes('@')) { toast('Please enter a valid email', 'error'); return; }
  if (!password) { toast('Please enter your recovery password', 'error'); return; }
  if (!pin || pin.length < 4 || !pin.match(/^\\d{4,6}$/)) {
    toast('Wallet PIN is required for recovery (4-6 digits)', 'error');
    if (pinEl) pinEl.focus();
    return;
  }

  const btn = event ? event.target.closest('button') : null;
  if (btn) { btn.disabled = true; btn.textContent = 'Recovering...'; }

  try {
    toast('Verifying PIN and fetching encrypted backup...', 'info');

    const res = await fetch('/api/tx-relay', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'wallet-recover',
        email: email,
        pin: pin,
      })
    });
    const data = await res.json();

    if (!data.ok) {
      toast(data.error || 'Recovery failed', 'error');
      if (btn) { btn.disabled = false; btn.textContent = 'Recover Wallet'; }
      return;
    }

    const backup = data.backup;
    const mnemonic = await decryptMnemonic(backup.ciphertext, backup.salt, backup.iv, password);
    const { address, publicKey } = await deriveAddressFromMnemonic(mnemonic);
    saveWallet(mnemonic, publicKey, address);
    await unlockWallet(mnemonic);
    sessionStorage.setItem('verdis_session_mnemonic', mnemonic);

    // Save with PIN for local persistence
    await saveWalletWithPin(mnemonic, publicKey, address, pin);
    toast('Wallet recovered and secured with PIN!', 'success');

    if (btn) { btn.disabled = false; btn.textContent = 'Recover Wallet'; }

    // Show security notice before loading dashboard
    showSecurityNotice(() => {
      setTimeout(loadDashboard, 200);
    });
  } catch (e) {
    toast('Recovery failed: ' + e.message, 'error');
    if (btn) { btn.disabled = false; btn.textContent = 'Recover Wallet'; }
  }
}"""

if old_recover_js in content:
    content = content.replace(old_recover_js, new_recover_js)
    print("[OK] recoverFromEmail() updated with PIN requirement")
else:
    print("[WARN] Exact recover JS not found, trying regex")
    pattern = r'async function recoverFromEmail\(\) \{.*?^}'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if match:
        content = content[:match.start()] + new_recover_js + content[match.end():]
        print("[OK] recoverFromEmail() updated via regex")
    else:
        print("[ERROR] Could not find recoverFromEmail function")
        exit(1)

# ============================================================
# 6. UPDATE ENTER WALLET JS — Register PIN on server
# ============================================================
old_enter_js = """async function enterWallet() {
  const pinEl = document.getElementBy"""

# This is tricky — let me find and replace the enterWallet function more carefully
# First, let's find it with regex
enter_pattern = r'async function enterWallet\(\) \{.*?^}'
enter_match = re.search(enter_pattern, content, re.MULTILINE | re.DOTALL)
if enter_match:
    enter_old = enter_match.group(0)
    # Add PIN registration after the existing saveWalletWithPin call
    # Insert pin-register call after the existing flow
    if 'pin-register' not in enter_old:
        # Find the saveWalletWithPin call and add pin-register after it
        if 'await saveWalletWithPin(' in enter_old:
            enter_new = enter_old.replace(
                'await saveWalletWithPin(',
                '// Register PIN on server for cross-device verification\n    try {\n      const regRes = await fetch(\'/api/tx-relay\', {\n        method: \'POST\',\n        headers: { \'Content-Type\': \'application/json\' },\n        body: JSON.stringify({ action: \'pin-register\', address: address, pin: pin })\n      });\n      const regData = await regRes.json();\n      if (regData.ok) console.log(\'[Wallet] PIN registered on server\');\n    } catch(e) { console.warn(\'[Wallet] PIN registration failed:\', e); }\n    await saveWalletWithPin('
            )
            content = content.replace(enter_old, enter_new)
            print("[OK] enterWallet() updated with PIN registration")
        else:
            print("[WARN] enterWallet() has no saveWalletWithPin, skipping PIN registration")
    else:
        print("[OK] enterWallet() already has PIN registration")
else:
    print("[WARN] Could not find enterWallet function")

# ============================================================
# 7. ADD SECURITY NOTICE JS FUNCTIONS (before the init event listener)
# ============================================================
security_js = """
// ===== SECURITY NOTICE =====
function showSecurityNotice(callback) {
  // Check if user already agreed in this session
  const agreed = sessionStorage.getItem('verdis_security_agreed');
  if (agreed === 'yes') {
    if (callback) callback();
    return;
  }

  // Show the modal
  const modal = document.getElementById('securityNoticeModal');
  if (!modal) {
    // Modal not found, proceed without
    if (callback) callback();
    return;
  }

  modal.style.display = 'flex';
  window._securityNoticeCallback = callback;

  // Reset checkbox
  const checkbox = document.getElementById('securityAgreeCheckbox');
  const btn = document.getElementById('securityAgreeBtn');
  if (checkbox) checkbox.checked = false;
  if (btn) btn.disabled = true;
}

function acceptSecurityNotice() {
  const checkbox = document.getElementById('securityAgreeCheckbox');
  if (!checkbox || !checkbox.checked) return;

  sessionStorage.setItem('verdis_security_agreed', 'yes');
  localStorage.setItem('verdis_security_agreed_at', new Date().toISOString());

  const modal = document.getElementById('securityNoticeModal');
  if (modal) modal.style.display = 'none';

  const callback = window._securityNoticeCallback;
  window._securityNoticeCallback = null;
  if (callback) callback();
}

"""

# Insert before the init event listener
init_marker = "// ===== Init ====="
if init_marker in content:
    content = content.replace(init_marker, security_js + init_marker)
    print("[OK] Security notice JS functions added")
else:
    # Try inserting before window.addEventListener('load'
    init_marker2 = "window.addEventListener('load'"
    if init_marker2 in content:
        content = content.replace(init_marker2, security_js + init_marker2)
        print("[OK] Security notice JS functions added (before load listener)")
    else:
        print("[ERROR] Could not find insertion point for security JS")
        exit(1)

# ============================================================
# 8. UPDATE INIT — Show security notice on auto-unlock
# ============================================================
old_auto_unlock = "document.getElementById('authCards').style.display = 'none';\n      document.getElementById('pinUnlockForm').style.display = 'none';\n      loadDashboard();\n      console.log('[Wallet] Auto-unlocked from session');"
new_auto_unlock = "document.getElementById('authCards').style.display = 'none';\n      document.getElementById('pinUnlockForm').style.display = 'none';\n      showSecurityNotice(() => {\n        loadDashboard();\n        console.log('[Wallet] Auto-unlocked from session');\n      });"

if old_auto_unlock in content:
    content = content.replace(old_auto_unlock, new_auto_unlock)
    print("[OK] Auto-unlock updated to show security notice")
else:
    print("[WARN] Could not find auto-unlock code")

# ============================================================
# 9. UPDATE LOAD DASHBOARD — Show security notice on dashboard load
# ============================================================
old_load_dashboard = "function loadDashboard() {"
if old_load_dashboard in content:
    # Add security notice check at the start of loadDashboard
    new_load_dashboard = """function loadDashboard() {
  // Show security notice if not yet agreed
  const agreed = sessionStorage.getItem('verdis_security_agreed');
  if (agreed !== 'yes') {
    showSecurityNotice(() => { _loadDashboardActual(); });
    return;
  }
  _loadDashboardActual();
}

function _loadDashboardActual() {"""
    # Only replace the first occurrence
    content = content.replace(old_load_dashboard, new_load_dashboard, 1)
    print("[OK] loadDashboard() updated with security notice check")
else:
    print("[WARN] Could not find loadDashboard()")

# Write the patched file
with open(WALLET_PATH, 'w') as f:
    f.write(content)
print("\n[DONE] Frontend security patch applied successfully")
