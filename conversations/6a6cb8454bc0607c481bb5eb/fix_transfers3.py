import subprocess

result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/explorer/index.html"],
    capture_output=True, text=True
)
content = result.stdout
lines = content.split('\n')

# Find the start of loadTransfers function (line 1657, 0-indexed = 1656)
# Find the end (next function or blank line after the closing brace)
start_idx = None
end_idx = None
brace_count = 0
for i, line in enumerate(lines):
    if line.strip() == 'async function loadTransfers() {':
        start_idx = i
        brace_count = 1
        continue
    if start_idx is not None:
        for ch in line:
            if ch == '{': brace_count += 1
            elif ch == '}': brace_count -= 1
        if brace_count == 0 and i > start_idx:
            end_idx = i
            break

print(f"Found loadTransfers at lines {start_idx+1}-{end_idx+1}")

new_func = '''async function loadTransfers() {
  var tbody = document.getElementById('transfersTable');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-3)">Scanning recent blocks...</td></tr>';
  try {
    var header = await rpc('chain_getHeader', []);
    if (!header) return;
    var current = parseInt(header.number, 16);
    var transfers = [];

    // Fetch last 50 blocks in parallel batches of 10
    for (var batch = 0; batch < 5; batch++) {
      var promises = [];
      for (var i = 0; i < 10; i++) {
        var blockNum = current - (batch * 10 + i);
        if (blockNum < 0) break;
        promises.push(scanBlockForTransfers(blockNum));
      }
      var results = await Promise.all(promises);
      for (var j = 0; j < results.length; j++) {
        if (results[j] && results[j].length > 0) {
          transfers = transfers.concat(results[j]);
        }
      }
      if (transfers.length >= 50) break;
    }

    transfers.sort(function(a, b) { return b.block - a.block; });
    transfers = transfers.slice(0, 50);

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

async function scanBlockForTransfers(blockNum) {
  try {
    var hash = await rpc('chain_getBlockHash', [blockNum]);
    if (!hash) return [];
    var block = await rpc('chain_getBlock', [hash]);
    if (!block || !block.block || !block.block.extrinsics) return [];
    var results = [];
    for (var i = 0; i < block.block.extrinsics.length; i++) {
      var ext = block.block.extrinsics[i];
      if (!ext.method) continue;
      var pallet = ext.method.pallet || '';
      var method = ext.method.method || '';

      var isTransfer = (pallet === 'balances' && (method === 'transfer' || method === 'transfer_allow_death' || method === 'force_transfer')) ||
                       (pallet === 'tokens' && method === 'transfer');
      if (isTransfer && ext.args) {
        var from = ext.signature && ext.signature.signedTransaction ? ext.signature.signedTransaction.signer : '—';
        var to = ext.args.dest || ext.args.to || '—';
        var amount = ext.args.value || ext.args.amount || 0;
        if (typeof amount === 'object' && amount.amount) amount = amount.amount;
        results.push({ hash: hash, block: blockNum, from: from, to: to, amount: amount, type: pallet + '.' + method });
      }

      if (pallet === 'system' && method === 'remark') {
        var signer = ext.signature && ext.signature.signedTransaction ? ext.signature.signedTransaction.signer : '—';
        results.push({ hash: hash, block: blockNum, from: signer, to: '—', amount: 0, type: 'system.remark' });
      }

      if (pallet === 'ammDex' || pallet === 'amm') {
        var signer2 = ext.signature && ext.signature.signedTransaction ? ext.signature.signedTransaction.signer : '—';
        results.push({ hash: hash, block: blockNum, from: signer2, to: 'AMM Pool', amount: 0, type: pallet + '.' + method });
      }
    }
    return results;
  } catch(e) { return []; }
}'''

# Replace the old function
new_lines = lines[:start_idx] + new_func.split('\n') + lines[end_idx+1:]
new_content = '\n'.join(new_lines)

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /var/www/verdiscan/explorer/index.html"],
    input=new_content,
    capture_output=True,
    text=True
)
print(f"Written: exit {proc.returncode}")
