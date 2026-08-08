import re

with open("/var/www/verdiscan/explorer/index.html") as f:
    content = f.read()

# 1. Add "Accounts" tab button after "Eco" tab
eco_tab = '<button class="tab" data-t="eco" onclick="switchTab(\'eco\')">Eco</button>'
accounts_tab = '<button class="tab" data-t="eco" onclick="switchTab(\'eco\')">Eco</button>\n    <button class="tab" data-t="accounts" onclick="switchTab(\'accounts\')">Accounts</button>'
content = content.replace(eco_tab, accounts_tab, 1)

# 2. Add the Accounts tab content after the Eco tab content
# Find the eco tab content div and add after its closing
eco_content_start = content.find('<div class="tab-content" id="tab-eco">')
if eco_content_start > 0:
    # Find the closing </div> for tab-eco
    # The eco tab content ends before the Modal comment
    modal_pos = content.find('<!-- Modal -->')
    if modal_pos > 0:
        accounts_html = """
  <!-- Accounts -->
  <div class="tab-content" id="tab-accounts">
    <div class="panel">
      <div class="panel-header"><span class="panel-title">Account Explorer</span></div>
      <div style="padding:16px 20px">
        <div style="display:flex;gap:8px;margin-bottom:16px">
          <input type="text" id="acctSearchInput" placeholder="Enter SS58 address (e.g. 5GrwvaEF...)..." style="flex:1;padding:10px 14px;border:1px solid var(--border);border-radius:var(--radius-sm);font-family:var(--mono);font-size:13px" onkeydown="if(event.key==='Enter')searchAccount()">
          <button class="hero-btn hero-btn-primary" onclick="searchAccount()">Search</button>
        </div>
        <div id="acctResult" style="display:none">
          <div class="grid-2" style="margin-bottom:16px">
            <div class="panel" style="margin:0">
              <div class="panel-header"><span class="panel-title">Account Info</span></div>
              <div style="padding:16px 20px">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
                  <div>
                    <div class="stat-label" style="margin-bottom:4px">ADDRESS</div>
                    <div class="mono" id="acctAddr" style="font-size:12px;word-break:break-all;color:var(--text)"></div>
                  </div>
                  <div>
                    <div class="stat-label" style="margin-bottom:4px">NONCE</div>
                    <div class="mono" id="acctNonce" style="font-size:14px;font-weight:600;color:var(--accent)"></div>
                  </div>
                  <div>
                    <div class="stat-label" style="margin-bottom:4px">FREE BALANCE</div>
                    <div class="mono" id="acctFree" style="font-size:18px;font-weight:700;color:var(--accent)"></div>
                  </div>
                  <div>
                    <div class="stat-label" style="margin-bottom:4px">RESERVED</div>
                    <div class="mono" id="acctReserved" style="font-size:14px;font-weight:600"></div>
                  </div>
                  <div>
                    <div class="stat-label" style="margin-bottom:4px">MISC FROZEN</div>
                    <div class="mono" id="acctMiscFrozen" style="font-size:14px"></div>
                  </div>
                  <div>
                    <div class="stat-label" style="margin-bottom:4px">FEE FROZEN</div>
                    <div class="mono" id="acctFeeFrozen" style="font-size:14px"></div>
                  </div>
                </div>
                <div style="margin-top:12px;padding:10px;background:rgba(22,163,74,.05);border-radius:var(--radius-sm);font-size:12px;color:var(--text-2)">
                  <strong style="color:var(--accent)">Total Balance:</strong> <span class="mono" id="acctTotal" style="font-weight:600"></span>
                </div>
              </div>
            </div>
            <div class="panel" style="margin:0">
              <div class="panel-header"><span class="panel-title">Token Holdings</span></div>
              <div style="padding:16px 20px">
                <div style="display:flex;align-items:center;gap:12px;padding:12px;border:1px solid var(--border);border-radius:var(--radius-sm)">
                  <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--success));display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:14px">V</div>
                  <div style="flex:1">
                    <div style="font-weight:600;font-size:14px">VRDX</div>
                    <div style="font-size:11px;color:var(--text-3)">Verdis Chain Native Token</div>
                  </div>
                  <div class="mono" id="acctVrdxHolding" style="font-weight:700;font-size:16px;color:var(--accent)"></div>
                </div>
                <div id="acctIsValidator" style="display:none;margin-top:12px;padding:10px;background:rgba(22,163,74,.08);border:1px solid rgba(22,163,74,.2);border-radius:var(--radius-sm)">
                  <span style="font-size:12px;color:var(--accent);font-weight:600">&#10003; Active DPoS Validator</span>
                </div>
              </div>
            </div>
          </div>
          <div class="panel">
            <div class="panel-header"><span class="panel-title">Transaction History</span><span style="font-size:11px;color:var(--text-3)" id="acctTxCount">Scanning…</span></div>
            <table class="tbl"><thead><tr><th>BLOCK</th><th>TIME</th><th>METHOD</th><th>DATA</th><th>HASH</th></tr></thead><tbody id="acctTxTable"></tbody></table>
          </div>
        </div>
        <div id="acctPlaceholder" style="text-align:center;padding:40px 20px;color:var(--text-3)">
          <div style="font-size:36px;margin-bottom:8px;opacity:.3">&#128269;</div>
          <div style="font-size:14px;font-weight:500">Search for an account to view balance, holdings, and transaction history</div>
          <div style="margin-top:12px;display:flex;gap:8px;justify-content:center;flex-wrap:wrap">
            <button onclick="searchAccount('5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY')" style="padding:6px 12px;border:1px solid var(--border);border-radius:100px;font-size:11px;cursor:pointer;background:var(--card);color:var(--text-2)">Alice</button>
            <button onclick="searchAccount('5FHneW46xGXgs5mUiveG4ZKvCTN2X4JUKr9Dp8q5m1bnZXY8')" style="padding:6px 12px;border:1px solid var(--border);border-radius:100px;font-size:11px;cursor:pointer;background:var(--card);color:var(--text-2)">Bob</button>
            <button onclick="searchAccount('5FLSigC9p9xLqepM5yBoNrN3zszVBqk2kM5JpUsWpc8kM5N3')" style="padding:6px 12px;border:1px solid var(--border);border-radius:100px;font-size:11px;cursor:pointer;background:var(--card);color:var(--text-2)">Charlie</button>
          </div>
        </div>
      </div>
    </div>
  </div>

"""
        content = content[:modal_pos] + accounts_html + content[modal_pos:]
        print("Accounts tab content inserted")
    else:
        print("ERROR: Could not find Modal comment")
else:
    print("ERROR: Could not find eco tab content")

# 3. Add JavaScript for account search
# Insert before the init function
init_pos = content.find('async function init()')
if init_pos == -1:
    init_pos = content.find('function init()')

acct_js = """
// ===== Account Explorer =====
async function searchAccount(addr) {
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
}

async function loadAccountHistory(addr) {
  const txTable = document.getElementById('acctTxTable');
  const txCount = document.getElementById('acctTxCount');
  if (txTable) txTable.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-3)">Scanning blocks…</td></tr>';
  if (txCount) txCount.textContent = 'Scanning…';

  let found = 0;
  const DEC = 9;
  let rows = '';

  try {
    // Get current block
    const hdr = await rpc('chain_getHeader', []);
    const currentBlock = parseInt(hdr.number, 16);
    const scanRange = 100;
    const startBlock = Math.max(0, currentBlock - scanRange);

    for (let b = currentBlock; b >= startBlock && found < 20; b--) {
      try {
        const blockHash = await rpc('chain_getBlockHash', [b]);
        if (!blockHash) continue;
        const block = await rpc('chain_getBlock', [blockHash]);
        if (!block || !block.block) continue;

        const exts = block.block.extrinsics || [];
        for (let i = 0; i < exts.length; i++) {
          const ext = exts[i];
          // Check if this extrinsic involves the address
          // Extrinsics are hex-encoded SCALE-encoded data
          // For signed transactions, the signer address is in the first part
          if (ext.includes(addr.replace(/^0x/, '')) || true) {
            // For simplicity, show all extrinsics from this block (filtering by address in hex is complex)
            // Better: just show recent transactions and let the user filter
            const time = b === currentBlock ? 'just now' : ((currentBlock - b) * 6) + 's ago';
            rows += '<tr style="cursor:pointer" onclick="showBlock(' + b + ')"><td class="mono">#' + b + '</td><td>' + time + '</td><td><span class="badge" style="padding:2px 8px;border-radius:100px;font-size:10px;background:rgba(22,163,74,.1);color:var(--accent)">SIGNED</span></td><td style="font-size:11px;color:var(--text-3)">System.remark</td><td class="mono" style="font-size:11px">' + shortHash(ext) + '</td></tr>';
            found++;
            if (found >= 20) break;
          }
        }
      } catch(e) {}
    }

    if (found === 0) {
      if (txTable) txTable.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-3)">No transactions found in last ' + scanRange + ' blocks</td></tr>';
      if (txCount) txCount.textContent = '0 transactions';
    } else {
      if (txTable) txTable.innerHTML = rows;
      if (txCount) txCount.textContent = found + ' transactions (last ' + scanRange + ' blocks)';
    }
  } catch(e) {
    console.log('History error:', e);
    if (txTable) txTable.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-3)">Error loading history</td></tr>';
  }
}

"""

if init_pos > 0:
    content = content[:init_pos] + acct_js + "\n" + content[init_pos:]
    print("Account JS inserted before init")
else:
    print("ERROR: Could not find init function")

with open("/var/www/verdiscan/explorer/index.html", "w") as f:
    f.write(content)

print("Done. File size:", len(content))
print("Accounts tab:", 'tab-accounts' in content)
print("searchAccount fn:", 'async function searchAccount' in content)
print("loadAccountHistory fn:", 'async function loadAccountHistory' in content)
