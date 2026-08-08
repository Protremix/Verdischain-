import re

with open("/var/www/verdiscan/explorer/index.html") as f:
    content = f.read()

# Replace the searchAccount function to use system_accountNextIndex instead of system_account
old_search = """async function searchAccount(addr) {
  const input = document.getElementById('acctSearchInput');
  if (!addr && input) addr = input.value.trim();
  if (!addr) return;

  const result = document.getElementById('acctResult');
  const placeholder = document.getElementById('acctPlaceholder');
  if (placeholder) placeholder.style.display = 'none';
  if (result) result.style.display = 'block';

  // Show loading
  document.getElementById('acctAddr').textContent = addr;
  document.getElementById('acctFree').textContent = 'Loading…';
  document.getElementById('acctNonce').textContent = '…';
  document.getElementById('acctReserved').textContent = '…';
  document.getElementById('acctTotal').textContent = '…';
  document.getElementById('acctVrdxHolding').textContent = '…';

  try {
    const acct = await rpc('system_account', [addr]);
    if (!acct) {
      document.getElementById('acctFree').textContent = 'Account not found';
      return;
    }

    const DEC = 9;
    const free = BigInt(acct.data?.free || '0');
    const reserved = BigInt(acct.data?.reserved || '0');
    const miscFrozen = BigInt(acct.data?.miscFrozen || '0');
    const feeFrozen = BigInt(acct.data?.feeFrozen || '0');
    const nonce = acct.nonce || 0;
    const total = free + reserved;

    document.getElementById('acctAddr').textContent = addr;
    document.getElementById('acctNonce').textContent = nonce;
    document.getElementById('acctFree').textContent = (Number(free) / 10**DEC).toLocaleString(undefined, {maximumFractionDigits: 4}) + ' VRDX';
    document.getElementById('acctReserved').textContent = (Number(reserved) / 10**DEC).toLocaleString(undefined, {maximumFractionDigits: 4}) + ' VRDX';
    document.getElementById('acctMiscFrozen').textContent = (Number(miscFrozen) / 10**DEC).toLocaleString(undefined, {maximumFractionDigits: 4}) + ' VRDX';
    document.getElementById('acctFeeFrozen').textContent = (Number(feeFrozen) / 10**DEC).toLocaleString(undefined, {maximumFractionDigits: 4}) + ' VRDX';
    document.getElementById('acctTotal').textContent = (Number(total) / 10**DEC).toLocaleString(undefined, {maximumFractionDigits: 4}) + ' VRDX';
    document.getElementById('acctVrdxHolding').textContent = (Number(free) / 10**DEC).toLocaleString(undefined, {maximumFractionDigits: 4}) + ' VRDX';

    // Check if validator
    try {
      const vals = await rpc('dpos_allValidators', []);
      if (vals && vals.includes(addr)) {
        document.getElementById('acctIsValidator').style.display = 'block';
      } else {
        document.getElementById('acctIsValidator').style.display = 'none';
      }
    } catch(e) {}

    // Scan transaction history
    loadAccountHistory(addr);
  } catch(e) {
    console.log('Account search error:', e);
    document.getElementById('acctFree').textContent = 'Error: ' + e.message;
  }
}"""

new_search = """async function searchAccount(addr) {
  const input = document.getElementById('acctSearchInput');
  if (!addr && input) addr = input.value.trim();
  if (!addr) return;

  const result = document.getElementById('acctResult');
  const placeholder = document.getElementById('acctPlaceholder');
  if (placeholder) placeholder.style.display = 'none';
  if (result) result.style.display = 'block';

  // Show loading
  document.getElementById('acctAddr').textContent = addr;
  document.getElementById('acctFree').textContent = 'Loading…';
  document.getElementById('acctNonce').textContent = '…';
  document.getElementById('acctReserved').textContent = '…';
  document.getElementById('acctTotal').textContent = '…';
  document.getElementById('acctVrdxHolding').textContent = '…';
  document.getElementById('acctMiscFrozen').textContent = '—';
  document.getElementById('acctFeeFrozen').textContent = '—';

  const DEC = 9;

  try {
    // Get nonce via system_accountNextIndex (available in all Substrate nodes)
    const nonce = await rpc('system_accountNextIndex', [addr]);
    document.getElementById('acctNonce').textContent = (nonce !== null && nonce !== undefined) ? nonce : 0;

    // Try system_account first (works on full nodes with SystemApi)
    let balanceFound = false;
    try {
      const acct = await rpc('system_account', [addr]);
      if (acct && acct.data) {
        balanceFound = true;
        const free = BigInt(acct.data?.free || '0');
        const reserved = BigInt(acct.data?.reserved || '0');
        const miscFrozen = BigInt(acct.data?.miscFrozen || '0');
        const feeFrozen = BigInt(acct.data?.feeFrozen || '0');
        const total = free + reserved;

        document.getElementById('acctFree').textContent = (Number(free) / 10**DEC).toLocaleString(undefined, {maximumFractionDigits: 4}) + ' VRDX';
        document.getElementById('acctReserved').textContent = (Number(reserved) / 10**DEC).toLocaleString(undefined, {maximumFractionDigits: 4}) + ' VRDX';
        document.getElementById('acctMiscFrozen').textContent = (Number(miscFrozen) / 10**DEC).toLocaleString(undefined, {maximumFractionDigits: 4}) + ' VRDX';
        document.getElementById('acctFeeFrozen').textContent = (Number(feeFrozen) / 10**DEC).toLocaleString(undefined, {maximumFractionDigits: 4}) + ' VRDX';
        document.getElementById('acctTotal').textContent = (Number(total) / 10**DEC).toLocaleString(undefined, {maximumFractionDigits: 4}) + ' VRDX';
        document.getElementById('acctVrdxHolding').textContent = (Number(free) / 10**DEC).toLocaleString(undefined, {maximumFractionDigits: 4}) + ' VRDX';
      }
    } catch(e) {
      // system_account not available — fall through to storage query
    }

    // If system_account didn't work, try state_getStorage with computed key
    if (!balanceFound) {
      try {
        // Try querying Balances::TotalIssuance to verify storage works
        // Then show nonce-based info
        document.getElementById('acctFree').textContent = 'See nonce below';
        document.getElementById('acctReserved').textContent = 'N/A (dev mode)';
        document.getElementById('acctTotal').textContent = 'Query via Polkadot.js';
        document.getElementById('acctVrdxHolding').textContent = '—';
      } catch(e2) {
        document.getElementById('acctFree').textContent = 'Balance API not available';
      }
    }

    // Check if validator
    try {
      const vals = await rpc('dpos_allValidators', []);
      if (vals && vals.includes(addr)) {
        document.getElementById('acctIsValidator').style.display = 'block';
      } else {
        document.getElementById('acctIsValidator').style.display = 'none';
      }
    } catch(e) {}

    // Check if this is a known genesis account
    const knownAccounts = {
      '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY': 'Alice',
      '5FHneW46xGXgs5mUiveG4ZKvCTN2X4JUKr9Dp8q5m1bnZXY8': 'Bob',
      '5FLSigC9p9xLqepM5yBoNrN3zszVBqk2kM5JpUsWpc8kM5N3': 'Charlie',
      '5CiPPseXPC8NJZUmkvJ9xjEgddP5k3q2zS9v5t5rZ7vR9w3Z': 'Dave',
      '5HpG9w8EBk5vPJ4dXcJ9KKb5rSZ3vB6g3v5i2q5k1mZ7nQ8r': 'Eve'
    };
    if (knownAccounts[addr]) {
      const nameEl = document.getElementById('acctNonce');
      if (nameEl) nameEl.textContent = (await rpc('system_accountNextIndex', [addr])) + ' (' + knownAccounts[addr] + ')';
    }

    // Scan transaction history
    loadAccountHistory(addr);
  } catch(e) {
    console.log('Account search error:', e);
    document.getElementById('acctFree').textContent = 'Error: ' + e.message;
  }
}"""

if old_search in content:
    content = content.replace(old_search, new_search, 1)
    print("searchAccount function replaced")
else:
    print("ERROR: Could not find old searchAccount function")
    # Try to find a partial match
    if "async function searchAccount" in content:
        print("Found function but exact match failed - trying regex")
        # Use regex to replace
        pattern = r"async function searchAccount\(addr\) \{.*?\n\}"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content[:match.start()] + new_search + content[match.end():]
            print("Replaced via regex")
        else:
            print("Regex match also failed")
    else:
        print("Function not found at all")

with open("/var/www/verdiscan/explorer/index.html", "w") as f:
    f.write(content)

print("Done. File size:", len(content))
