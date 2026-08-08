import subprocess, re

result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/wallet/index.html"],
    capture_output=True, text=True
)
content = result.stdout

# Replace refreshBalance to show nonce and account info
old_refresh = '''async function refreshBalance() {
  const wallet = loadWallet();
  if (!wallet) return;
  const balanceEl = document.getElementById('balanceDisplay');
  const subEl = document.getElementById('balanceSub');
  subEl.textContent = 'Loading balance from chain...';

  const balance = await getBalance(wallet.address);
  const formatted = formatBalance(balance);
  balanceEl.innerHTML = formatted + '<span class="unit">VRDX</span>';
  subEl.textContent = `≈ $${(Number(formatted) * 0.05).toFixed(2)} USD · Block #${await getBlockHeight()}`;
}'''

new_refresh = '''async function refreshBalance() {
  const wallet = loadWallet();
  if (!wallet) return;
  const balanceEl = document.getElementById('balanceDisplay');
  const subEl = document.getElementById('balanceSub');
  subEl.textContent = 'Loading balance from chain...';

  const [balance, info, blockHeight] = await Promise.all([
    getBalance(wallet.address),
    getAccountInfo(wallet.address),
    getBlockHeight()
  ]);
  const formatted = formatBalance(balance);
  balanceEl.innerHTML = formatted + '<span class="unit">VRDX</span>';

  let subText = `≈ $${(Number(formatted) * 0.05).toFixed(2)} USD · Block #${blockHeight}`;
  if (info && info.nonce !== undefined) {
    subText += ` · Nonce: ${info.nonce}`;
  }
  if (info && info.is_validator) {
    subText += ` · Validator: ${info.validator_name || 'Yes'}`;
    if (info.green_score > 0) {
      subText += ` · Green Score: ${info.green_score}`;
    }
  }
  subEl.textContent = subText;
}'''

if old_refresh in content:
    content = content.replace(old_refresh, new_refresh)
    print("Replaced refreshBalance function")
else:
    print("ERROR: old refreshBalance not found")
    # Try with regex
    match = re.search(r'async function refreshBalance\(\).*?\n\}', content, re.DOTALL)
    if match:
        print(f"Found match: {match.group()[:200]}")

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /var/www/verdiscan/wallet/index.html"],
    input=content,
    capture_output=True,
    text=True
)
print(f"Written: exit {proc.returncode}")
