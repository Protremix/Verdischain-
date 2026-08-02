import re

with open("/opt/verdis/app/dist/web/wallet.html", "r") as f:
    c = f.read()

fixes = []

# BUG 1: Add missing backupModal
backup_modal = '''<div class="modal-overlay" id="backupModal" onclick="if(event.target===this)closeModal('backupModal')">
    <div class="modal" style="max-width:420px;">
        <div style="text-align:center;margin-bottom:16px;">
            <div style="width:56px;height:56px;margin:0 auto 12px;border-radius:50%;background:rgba(229,57,53,0.15);display:flex;align-items:center;justify-content:center;">
                <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#e53935" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
            </div>
            <h3 style="font-size:18px;font-weight:700;margin:0 0 4px;">Back Up Your Wallet</h3>
            <p style="font-size:13px;color:var(--text-dim);margin:0 0 16px;">Save your private key securely. You will need it to recover your wallet.</p>
        </div>
        <div id="backupKeyDisplay" style="background:var(--bg-input);border:1px solid var(--border);border-radius:12px;padding:16px;font-family:var(--font-mono);font-size:11px;word-break:break-all;color:var(--text-dim);margin-bottom:16px;text-align:center;">Click reveal to view key</div>
        <button onclick="revealBackupKey()" style="width:100%;padding:12px;background:transparent;border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:13px;cursor:pointer;margin-bottom:8px;">Reveal Private Key</button>
        <button onclick="copyBackupKey()" style="width:100%;padding:12px;background:transparent;border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:13px;cursor:pointer;margin-bottom:16px;">Copy Private Key</button>
        <label style="display:flex;align-items:center;gap:8px;margin-bottom:16px;cursor:pointer;font-size:13px;color:var(--text-dim);">
            <input type="checkbox" id="backupConfirm" onchange="document.getElementById('backupDoneBtn').disabled=!this.checked" style="accent-color:var(--accent-green);width:18px;height:18px;">
            I have safely stored my private key
        </label>
        <button id="backupDoneBtn" disabled onclick="closeModal('backupModal')" style="width:100%;padding:14px;background:var(--accent-green);border:none;border-radius:12px;color:#000;font-weight:600;font-size:14px;cursor:pointer;opacity:0.5;">Done</button>
    </div>
</div>
        '''

if 'id="backupModal"' not in c:
    c = c.replace('<div class="modal-overlay" id="settingsModal"', backup_modal + '<div class="modal-overlay" id="settingsModal"')
    fixes.append("BUG 1: Added backupModal")

# BUG 2: Fix securitySettingsContent
if 'id="settingsContent"' in c and 'id="securitySettingsContent"' not in c:
    c = c.replace('<div id="settingsContent"></div>', '<div id="securitySettingsContent"></div>')
    fixes.append("BUG 2: Fixed securitySettingsContent ID")

# BUG 4: Fix hardcoded zero token balances
old_bal = "const amount = t.symbol === 'VRDX' ? bal : 0;"
new_bal = "const amount = t.symbol === 'VRDX' ? bal : (wallet.tokenBalances && wallet.tokenBalances[t.symbol] ? wallet.tokenBalances[t.symbol] : 0);"
if old_bal in c:
    c = c.replace(old_bal, new_bal)
    fixes.append("BUG 4: Fixed token balances")

# BUG 5: Remove fake random price changes
old_price = "Math.random() * 5).toFixed(1) + '%</div>'"
if old_price in c:
    c = c.replace(old_price, "--</div>'")
    fixes.append("BUG 5: Removed fake price changes")

# BUG 6: Fix hardcoded vote amount
old_vote = "amount: 100, // <--- Hardcoded 100 VRDX"
new_vote = "amount: parseFloat(document.getElementById('voteAmount') ? document.getElementById('voteAmount').value : 100),"
if old_vote in c:
    c = c.replace(old_vote, new_vote)
    fixes.append("BUG 6: Fixed vote amount")

# BUG 7: Fix poolId construction in executeSwap
old_poolid = "poolId: swapFromToken + '_' + swapToToken,"
new_poolid = "poolId: (DEX_POOLS_CACHE.find(function(p) { return (p.tokenA === swapFromToken && p.tokenB === swapToToken) || (p.tokenB === swapFromToken && p.tokenA === swapToToken); }) || {}).id || (swapFromToken + '_' + swapToToken),"
if old_poolid in c:
    c = c.replace(old_poolid, new_poolid)
    fixes.append("BUG 7: Fixed poolId lookup")

# BUG 8: Fix WebAuthn biometric array conversion
old_webauthn = "id: new Uint8Array(securityConfig.biometricCredential.id),"
new_webauthn = "id: Uint8Array.from(atob(securityConfig.biometricCredential.id.replace(/-/g,'+').replace(/_/g,'/')), function(c) { return c.charCodeAt(0); }),"
if old_webauthn in c:
    c = c.replace(old_webauthn, new_webauthn)
    fixes.append("BUG 8: Fixed WebAuthn credential conversion")

# BUG 10: Add input validation for send amount
old_val = "if (!to || !amount) { toast('Enter address and amount', 'error'); return; }"
new_val = "if (!to || !amount) { toast('Enter address and amount', 'error'); return; } if (amount < 0) { toast('Amount must be positive', 'error'); return; } if (amount > balance) { toast('Insufficient balance', 'error'); return; } if (to === wallet.address) { toast('Cannot send to yourself', 'error'); return; }"
if old_val in c:
    c = c.replace(old_val, new_val)
    fixes.append("BUG 10: Added input validation")

# Add backup helper functions before closing script tag
backup_fns = """
function revealBackupKey() {
    var el = document.getElementById('backupKeyDisplay');
    if (el && el.textContent.indexOf('•') === -1 && !el.textContent.startsWith('Click')) {
        el.textContent = 'Click reveal to view key';
        el.style.color = 'var(--text-dim)';
    } else if (wallet && wallet.privateKey) {
        el.textContent = wallet.privateKey;
        el.style.color = 'var(--accent-green)';
    }
}
function copyBackupKey() {
    if (wallet && wallet.privateKey) {
        navigator.clipboard.writeText(wallet.privateKey);
        toast('Private key copied', 'success');
    }
}
"""
if 'revealBackupKey' not in c:
    c = c.replace("</script>", backup_fns + "\n</script>")
    fixes.append("Added backup helper functions")

# Add vote amount input to staking section if missing
if 'voteAmount' not in c:
    # Find the vote section and add an input
    old_vote_btn = "onclick=\"voteValidator('"
    if old_vote_btn in c:
        # Add a vote amount input before the vote buttons
        c = c.replace(
            old_vote_btn,
            '<input type="number" id="voteAmount" placeholder="Amount" value="100" min="1" style="width:80px;padding:6px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:12px;margin-right:8px;" onclick="event.stopPropagation()"> ' + old_vote_btn
        )
        fixes.append("Added vote amount input")

with open("/opt/verdis/app/dist/web/wallet.html", "w") as f:
    f.write(c)

print("Applied " + str(len(fixes)) + " fixes:")
for fix in fixes:
    print("  + " + fix)
