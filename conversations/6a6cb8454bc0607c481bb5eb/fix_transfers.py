import subprocess

result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/explorer/index.html"],
    capture_output=True, text=True
)
content = result.stdout

# 1. Add Transfers tab button after Analytics
old_tab = '''    <button class="tab" data-t="analytics" onclick="switchTab('analytics')">Analytics</button>'''
new_tab = '''    <button class="tab" data-t="analytics" onclick="switchTab('analytics')">Analytics</button>
    <button class="tab" data-t="transfers" onclick="switchTab('transfers')">Transfers</button>'''
content = content.replace(old_tab, new_tab)

# 2. Add tab content section after Analytics section (before <!-- Modal -->)
# Find the end of the analytics section
old_modal = '''  </div>

<!-- Modal -->'''
new_content = '''  </div>

  <!-- Token Transfers -->
  <div class="tab-content" id="tab-transfers">
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">VRDX Token Transfers</span>
        <span class="panel-link" id="transfersCount">Loading...</span>
      </div>
      <table class="tbl">
        <thead><tr><th>TX HASH</th><th>BLOCK</th><th>FROM</th><th>TO</th><th>AMOUNT (VRDX)</th><th>TYPE</th></tr></thead>
        <tbody id="transfersTable">
          <tr><td colspan="6" style="text-align:center;padding:20px"><span class="skel" style="width:100%"></span></td></tr>
        </tbody>
      </table>
    </div>
  </div>

<!-- Modal -->'''
content = content.replace(old_modal, new_content, 1)

# 3. Add switchTab case
old_switch = '''  if (t==='analytics') loadAnalytics();
}'''
new_switch = '''  if (t==='analytics') loadAnalytics();
  if (t==='transfers') loadTransfers();
}'''
content = content.replace(old_switch, new_switch)

# 4. Add loadTransfers function before init()
old_init_marker = '''// Analytics data collectors
window._tpsHistory = [];'''
new_init_with_transfers = '''// ===== Token Transfers =====
async function loadTransfers() {
  var tbody = document.getElementById('transfersTable');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-3)">Scanning recent blocks for transfers...</td></tr>';
  try {
    var header = await rpc('chain_getHeader', []);
    if (!header) return;
    var current = parseInt(header.number, 16);
    var transfers = [];

    // Scan last 100 blocks for transfer events
    for (var blockNum = current; blockNum >= Math.max(0, current - 100); blockNum--) {
      try {
        var hash = await rpc('chain_getBlockHash', [blockNum]);
        if (!hash) continue;
        var block = await rpc('chain_getBlock', [hash]);
        if (!block || !block.block || !block.block.extrinsics) continue;

        for (var i = 0; i < block.block.extrinsics.length; i++) {
          var ext = block.block.extrinsics[i];
          // Check if this is a balance transfer (method.pallet === 'balances' and method.method === 'transfer')
          if (ext.method) {
            var pallet = ext.method.pallet || '';
            var method = ext.method.method || '';
            var isTransfer = (pallet === 'balances' && method === 'transfer') ||
                             (pallet === 'balances' && method === 'transfer_allow_death') ||
                             (pallet === 'balances' && method === 'force_transfer') ||
                             (pallet === 'tokens' && method === 'transfer');

            // Also check for utility.batch with transfers
            if (isTransfer && ext.args) {
              var from = ext.signature && ext.signature.signedTransaction ? ext.signature.signedTransaction.signer : '—';
              var to = ext.args.dest || ext.args.to || '—';
              var amount = ext.args.value || ext.args.amount || 0;
              if (typeof amount === 'object' && amount.amount) amount = amount.amount;

              transfers.push({
                hash: hash,
                block: blockNum,
                from: from,
                to: to,
                amount: amount,
                type: pallet + '.' + method
              });
            }

            // Check system.remark as a "memo" type
            if (pallet === 'system' && method === 'remark') {
              transfers.push({
                hash: hash,
                block: blockNum,
                from: ext.signature && ext.signature.signedTransaction ? ext.signature.signedTransaction.signer : '—',
                to: '—',
                amount: 0,
                type: 'system.remark'
              });
            }
          }
        }
      } catch(e) { continue; }
      if (transfers.length >= 50) break;
    }

    document.getElementById('transfersCount').textContent = transfers.length + ' transfers found';

    if (transfers.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-3)">No token transfers found in recent blocks</td></tr>';
      return;
    }

    tbody.innerHTML = transfers.map(function(t) {
      var hashShort = t.hash.slice(0, 10) + '...' + t.hash.slice(-6);
      var fromShort = t.from && t.from.length > 15 ? t.from.slice(0, 8) + '...' + t.from.slice(-6) : t.from;
      var toShort = t.to && t.to.length > 15 ? t.to.slice(0, 8) + '...' + t.to.slice(-6) : t.to;
      var amountDisplay = t.amount > 0 ? (Number(t.amount) / 10**9).toLocaleString(undefined, {maximumFractionDigits: 4}) : '—';
      var typeBadge;
      if (t.type === 'system.remark') {
        typeBadge = '<span style="background:#f1f5f9;color:#475569;padding:2px 8px;border-radius:4px;font-size:11px">Remark</span>';
      } else {
        typeBadge = '<span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px">Transfer</span>';
      }
      return '<tr style="cursor:pointer" onclick="showBlockDetail(' + t.block + ')">' +
        '<td style="font-family:var(--mono);font-size:12px">' + hashShort + '</td>' +
        '<td style="font-weight:600">#' + t.block + '</td>' +
        '<td style="font-family:var(--mono);font-size:12px">' + fromShort + '</td>' +
        '<td style="font-family:var(--mono);font-size:12px">' + toShort + '</td>' +
        '<td style="font-family:var(--mono);font-weight:600">' + amountDisplay + '</td>' +
        '<td>' + typeBadge + '</td>' +
        '</tr>';
    }).join('');
  } catch(e) {
    console.error('Transfers error:', e);
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:#dc2626">Error loading transfers</td></tr>';
  }
}

// Analytics data collectors
window._tpsHistory = [];'''
content = content.replace(old_init_marker, new_init_with_transfers)

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /var/www/verdiscan/explorer/index.html"],
    input=content,
    capture_output=True,
    text=True
)
print(f"Written: exit {proc.returncode}")
