import subprocess

result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/wallet/index.html"],
    capture_output=True, text=True
)
content = result.stdout

# Replace getBalance function
old_get_balance = '''async function getBalance(address) {
  try {
    // Try RPC: system_account
    const account = await rpcCall('system_account', [address]);
    if (account && account.data) {
      const free = BigInt(account.data.free || 0);
      const reserved = BigInt(account.data.reserved || 0);
      return free + reserved;
    }
    // Fallback: try state_getStorage
    const storage = await rpcCall('state_getStorage', [address]);
    if (storage) {
      try { return BigInt(storage); } catch { return 0n; }
    }
    return 0n;
  } catch {
    return 0n;
  }
}'''

new_get_balance = '''async function getBalance(address) {
  try {
    // Use Verdiscan REST API which queries state_getStorage with proper Blake2_128Concat key
    const resp = await fetch(`/api/v1/account/${address}`);
    if (!resp.ok) return 0n;
    const json = await resp.json();
    if (json.success && json.data) {
      const free = BigInt(json.data.free_balance || 0);
      const reserved = BigInt(json.data.reserved_balance || 0);
      // Cache additional info for UI
      window._accountInfo = json.data;
      return free + reserved;
    }
    return 0n;
  } catch (e) {
    console.error('Balance query error:', e);
    return 0n;
  }
}

async function getAccountInfo(address) {
  try {
    const resp = await fetch(`/api/v1/account/${address}`);
    if (!resp.ok) return null;
    const json = await resp.json();
    if (json.success) return json.data;
    return null;
  } catch (e) {
    return null;
  }
}'''

if old_get_balance in content:
    content = content.replace(old_get_balance, new_get_balance)
    print("Replaced getBalance function")
else:
    print("ERROR: old getBalance not found")
    # Try to find it with different whitespace
    import re
    match = re.search(r'async function getBalance\(address\).*?^}', content, re.DOTALL | re.MULTILINE)
    if match:
        print(f"Found at: {match.start()}-{match.end()}")
        print(match.group()[:200])

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /var/www/verdiscan/wallet/index.html"],
    input=content,
    capture_output=True,
    text=True
)
print(f"Written: exit {proc.returncode}")
if proc.stderr:
    print(f"Stderr: {proc.stderr[:200]}")
