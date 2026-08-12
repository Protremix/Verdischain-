import re

with open('/var/www/verdiscan/wallet/index.html', 'r') as f:
    content = f.read()

changes = []

# 1. unlockWithPin: add sessionStorage save after successful unlock
old = "    await unlockWallet(mnemonic);\n    toast('Wallet unlocked!', 'success');"
new = "    await unlockWallet(mnemonic);\n    sessionStorage.setItem('verdis_session_mnemonic', mnemonic);\n    toast('Wallet unlocked!', 'success');"
if old in content:
    content = content.replace(old, new)
    changes.append('unlockWithPin: sessionStorage save')
else:
    # Try alternate pattern
    old2 = "    await unlockWallet(mnemonic);\n    toast('Wallet unlocked"
    if old2 in content:
        content = content.replace(old2, "    await unlockWallet(mnemonic);\n    sessionStorage.setItem('verdis_session_mnemonic', mnemonic);\n    toast('Wallet unlocked", 1)
        changes.append('unlockWithPin: sessionStorage save (alt)')
    else:
        changes.append('ERROR: unlockWithPin pattern not found')

# 2. lockWallet: clear sessionStorage
old_lock = "function lockWallet() {\n  _sessionMnemonic = null;"
new_lock = "function lockWallet() {\n  _sessionMnemonic = null;\n  sessionStorage.removeItem('verdis_session_mnemonic');"
if old_lock in content:
    content = content.replace(old_lock, new_lock)
    changes.append('lockWallet: clear sessionStorage')
else:
    changes.append('ERROR: lockWallet pattern not found')

# 3. clearWallet: clear sessionStorage
old_clear = "clearWallet = function() {\n  localStorage.removeItem('verdis_wallet_encrypted');\n  localStorage.removeItem('verdis_wallet');\n  lockWallet();"
new_clear = "clearWallet = function() {\n  localStorage.removeItem('verdis_wallet_encrypted');\n  localStorage.removeItem('verdis_wallet');\n  sessionStorage.removeItem('verdis_session_mnemonic');\n  lockWallet();"
if old_clear in content:
    content = content.replace(old_clear, new_clear)
    changes.append('clearWallet: clear sessionStorage')
else:
    changes.append('ERROR: clearWallet pattern not found')

# 4. Page load init: add sessionStorage auto-unlock check
# Find the wallet init load handler
old_init = "window.addEventListener('load', () => {\n  // Check if wallet is encrypted (needs PIN to unlock)\n  const enc = loadEncryptedWallet();\n  if (enc) {"
if old_init in content:
    new_init = """window.addEventListener('load', async () => {
  // 1. Check sessionStorage for active session (survives refresh, cleared on tab close)
  const sessionMnemonic = sessionStorage.getItem('verdis_session_mnemonic');
  if (sessionMnemonic) {
    try {
      await unlockWallet(sessionMnemonic);
      document.getElementById('authCards').style.display = 'none';
      document.getElementById('pinUnlockForm').style.display = 'none';
      loadDashboard();
      console.log('[Wallet] Auto-unlocked from session');
      return;
    } catch (e) {
      console.error('[Wallet] Session unlock failed:', e);
      sessionStorage.removeItem('verdis_session_mnemonic');
    }
  }

  // 2. Check if wallet is encrypted (needs PIN to unlock)
  const enc = loadEncryptedWallet();
  if (enc) {"""
    content = content.replace(old_init, new_init)
    changes.append('page load: sessionStorage auto-unlock')
else:
    # Try alternate — maybe it uses function() instead of =>
    old_init2 = "window.addEventListener('load', function() {\n  // Check if wallet is encrypted (needs PIN to unlock)\n  const enc = loadEncryptedWallet();\n  if (enc) {"
    if old_init2 in content:
        new_init2 = """window.addEventListener('load', async function() {
  // 1. Check sessionStorage for active session (survives refresh, cleared on tab close)
  const sessionMnemonic = sessionStorage.getItem('verdis_session_mnemonic');
  if (sessionMnemonic) {
    try {
      await unlockWallet(sessionMnemonic);
      document.getElementById('authCards').style.display = 'none';
      document.getElementById('pinUnlockForm').style.display = 'none';
      loadDashboard();
      console.log('[Wallet] Auto-unlocked from session');
      return;
    } catch (e) {
      console.error('[Wallet] Session unlock failed:', e);
      sessionStorage.removeItem('verdis_session_mnemonic');
    }
  }

  // 2. Check if wallet is encrypted (needs PIN to unlock)
  const enc = loadEncryptedWallet();
  if (enc) {"""
        content = content.replace(old_init2, new_init2)
        changes.append('page load: sessionStorage auto-unlock (function)')
    else:
        changes.append('ERROR: page load init pattern not found')

# 5. enterWallet: add sessionStorage save after saveWalletWithPin
old_enter = "      toast('Wallet secured with PIN. It will persist across refreshes.', 'success');"
new_enter = "      toast('Wallet secured with PIN. It will persist across refreshes.', 'success');\n      if (_sessionMnemonic) { sessionStorage.setItem('verdis_session_mnemonic', _sessionMnemonic); }"
if old_enter in content:
    content = content.replace(old_enter, new_enter, 1)
    changes.append('enterWallet: sessionStorage save')
else:
    changes.append('ERROR: enterWallet pattern not found')

# 6. importWallet: add sessionStorage save after unlockWallet
old_import = "    await unlockWallet(input); // derives keypair again and sets _sessionMnemonic/_sessionKeypair correctly"
new_import = "    await unlockWallet(input); // derives keypair again and sets _sessionMnemonic/_sessionKeypair correctly\n    sessionStorage.setItem('verdis_session_mnemonic', input);"
if old_import in content:
    content = content.replace(old_import, new_import)
    changes.append('importWallet: sessionStorage save')
else:
    changes.append('ERROR: importWallet pattern not found')

# 7. logout: clear sessionStorage
old_logout = "    localStorage.removeItem('verdis_wallet_encrypted');\n    localStorage.removeItem('verdis_wallet');\n    lockWallet();\n    location.reload();"
new_logout = "    localStorage.removeItem('verdis_wallet_encrypted');\n    localStorage.removeItem('verdis_wallet');\n    sessionStorage.removeItem('verdis_session_mnemonic');\n    lockWallet();\n    location.reload();"
if old_logout in content:
    content = content.replace(old_logout, new_logout)
    changes.append('logout: clear sessionStorage')
else:
    changes.append('ERROR: logout pattern not found')

with open('/var/www/verdiscan/wallet/index.html', 'w') as f:
    f.write(content)

for c in changes:
    print(c)
