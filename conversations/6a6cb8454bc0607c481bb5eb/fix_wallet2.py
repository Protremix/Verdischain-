with open("/opt/verdis/app/dist/web/wallet.html", "r") as f:
    c = f.read()

fixes = []

# Fix BUG 5: Remove fake random price changes
old_price = "'<div class=\"token-value\"><div class=\"token-value-amount\">$' + val + '</div><div class=\"token-value-change\" style=\"color:var(--accent-green);\">+' + (Math.random() * 5).toFixed(1) + '%</div></div>' +"
new_price = "'<div class=\"token-value\"><div class=\"token-value-amount\">$' + val + '</div><div class=\"token-value-change\" style=\"color:var(--text-dim);\">--</div></div>' +"
if old_price in c:
    c = c.replace(old_price, new_price)
    fixes.append("BUG 5: Removed fake price changes")

# Fix BUG 6: Hardcoded vote amount (without comment)
old_vote = "        amount: 100,\n        privateKey: wallet.privateKey,"
new_vote = "        amount: parseFloat(document.getElementById('voteAmount') ? document.getElementById('voteAmount').value : 100),\n        privateKey: wallet.privateKey,"
if old_vote in c:
    c = c.replace(old_vote, new_vote)
    fixes.append("BUG 6: Fixed vote amount")

# Add backup helper functions
backup_fns = """
function revealBackupKey() {
    var el = document.getElementById('backupKeyDisplay');
    if (!el) return;
    if (el.textContent.startsWith('Click') || el.textContent.indexOf('\u2022') !== -1) {
        if (wallet && wallet.privateKey) {
            el.textContent = wallet.privateKey;
            el.style.color = 'var(--accent-green)';
        }
    } else {
        el.textContent = 'Click reveal to view key';
        el.style.color = 'var(--text-dim)';
    }
}
function copyBackupKey() {
    if (wallet && wallet.privateKey) {
        navigator.clipboard.writeText(wallet.privateKey);
        toast('Private key copied', 'success');
    }
}
"""
if 'function revealBackupKey' not in c:
    # Find the last </script> and insert before it
    idx = c.rfind('</script>')
    if idx > -1:
        c = c[:idx] + backup_fns + '\n' + c[idx:]
        fixes.append("Added backup helper functions")

# Add vote amount input near the vote button
if 'id="voteAmount"' not in c:
    # Find the staking/vote section and add input
    old_vote_btn = "onclick=\"voteValidator('"
    if old_vote_btn in c:
        c = c.replace(
            old_vote_btn,
            '<input type="number" id="voteAmount" value="100" min="1" style="width:70px;padding:5px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:12px;margin-right:6px;" onclick="event.stopPropagation()"> ' + old_vote_btn
        )
        fixes.append("Added vote amount input field")

with open("/opt/verdis/app/dist/web/wallet.html", "w") as f:
    f.write(c)

print("Applied " + str(len(fixes)) + " additional fixes:")
for fix in fixes:
    print("  + " + fix)
