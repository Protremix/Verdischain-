import re, sys

with open("/var/www/verdiscan/explorer/index.html") as f:
    h = f.read()

# 1. Replace loadLatestExtrinsics function to use new decodeExtrinsic format
# The old function uses ext.type, ext.badge, ext.hash, ext.signerFull which don't exist in new format

old_ext_start = "// Load latest extrinsics (SIGNED only - real transactions)"
old_ext_end = "// Load latest transactions into overview"

# Extract and replace the block between the two markers
idx1 = h.find(old_ext_start)
idx2 = h.find(old_ext_end)

if idx1 > 0 and idx2 > idx1:
    new_ext_fn = """// Load latest extrinsics (SIGNED only - real transactions)
function loadLatestExtrinsics() {
  const tbody = document.getElementById('latestExts');
  if (!tbody) return;
  let html = '';
  let count = 0;
  for (let i = 0; i < blocksData.length && count < 8; i++) {
    const b = blocksData[i];
    const exts = b.exts || [];
    for (let j = 0; j < exts.length && count < 8; j++) {
      const ext = decodeExtrinsic(exts[j]);
      if (!ext || !ext.signer) continue;
      const signerDisplay = accountIdToSS58(ext.signer);
      const safeMethod = (ext.method || 'unknown').replace(/'/g, '');
      let remarkText = '';
      if (ext.remark && ext.remark.length) {
        for (var ri = 0; ri < Math.min(ext.remark.length, 35); ri++) {
          if (ext.remark[ri] >= 32 && ext.remark[ri] <= 126) remarkText += String.fromCharCode(ext.remark[ri]);
        }
      }
      const safeRemark = remarkText.replace(/'/g, '').replace(/"/g, '&quot;');
      html += '<tr onclick="showExtrinsic(\\''+safeMethod+'\\', '+b.num+', \\''+signerDisplay+'\\', \\''+safeRemark+'\\')" style="cursor:pointer">' +
        '<td><span class="badge badge-signed">Signed</span></td>' +
        '<td>' + (ext.method || 'unknown') + (remarkText ? '<br><span style="font-size:11px;color:var(--text-3)">'+remarkText+'</span>' : '') + '</td>' +
        '<td class="hash">'+shortHash(b.hash)+'</td>' +
        '<td class="hash hash-accent">#'+b.num+'</td>' +
        '</tr>';
      count++;
    }
  }
  if (count === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-3);padding:24px">Waiting for signed transactions...</td></tr>';
  } else {
    tbody.innerHTML = html;
  }
}

"""
    h = h[:idx1] + new_ext_fn + h[idx2:]
    print("Fixed: loadLatestExtrinsics updated")
else:
    print("Could not find loadLatestExtrinsics markers")

# 2. Replace loadLatestTxs function
tx_start = "// Load latest transactions into overview"
tx_end = "// Show transaction detail modal"
idx3 = h.find(tx_start)
idx4 = h.find(tx_end)

if idx3 > 0 and idx4 > idx3:
    new_tx_fn = """// Load latest transactions into overview
function loadLatestTxs() {
  const tbody = document.getElementById('latestTxs');
  if (!tbody) return;
  let html = '';
  let count = 0;
  for (let i = 0; i < blocksData.length && count < 10; i++) {
    const b = blocksData[i];
    const exts = b.exts || [];
    for (let j = 0; j < exts.length && count < 10; j++) {
      const ext = decodeExtrinsic(exts[j]);
      if (!ext || !ext.signer) continue;
      const signerDisplay = accountIdToSS58(ext.signer);
      const valStr = ext.value ? (ext.value / 1e9).toFixed(4) : '0';
      const safeMethod = (ext.method || 'unknown').replace(/'/g, '');
      html += '<tr style="cursor:pointer" onclick="showExtrinsic(\\''+safeMethod+'\\', '+b.num+', \\''+signerDisplay+'\\', \\''+'\\')">' +
        '<td class="hash hash-accent">#' + b.num + '</td>' +
        '<td class="hash">' + shortHash(b.hash) + '</td>' +
        '<td><span class="badge badge-signed">' + (ext.method || 'unknown') + '</span></td>' +
        '<td class="hash">' + signerDisplay + '</td>' +
        '<td>' + valStr + '</td>' +
        '</tr>';
      count++;
    }
  }
  if (count === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-3);padding:24px">Waiting for signed transactions...</td></tr>';
  } else {
    tbody.innerHTML = html;
  }
}

"""
    h = h[:idx3] + new_tx_fn + h[idx4:]
    print("Fixed: loadLatestTxs updated")
else:
    print("Could not find loadLatestTxs markers")

# 3. Fix showExtrinsic signature and body
old_show_sig = "function showExtrinsic(hash, blockNum, type, method, signer, remark) {"
new_show_sig = "function showExtrinsic(method, blockNum, signer, remark) {"
if old_show_sig in h:
    h = h.replace(old_show_sig, new_show_sig)
    print("Fixed: showExtrinsic signature updated")

old_body = """  document.getElementById('modalTitle').textContent = 'Transaction Detail';
  let html = '<dl>';
  html += '<dt>Extrinsic Hash</dt><dd>' + (hash || '\u2014') + '</dd>';
  html += '<dt>Block Number</dt><dd>' + (blockNum ? '#' + blockNum : '\u2014') + '</dd>';
  html += '<dt>Type</dt><dd><span class="badge ' + (type === 'Signed' ? 'badge-signed' : 'badge-inherent') + '">' + (type || 'Signed') + '</span></dd>';
  html += '<dt>Method</dt><dd>' + (method || 'System.remark') + '</dd>';
  html += '<dt>Signer Address</dt><dd>' + (signer || '\u2014') + '</dd>';
  html += '<dt>Remark Text</dt><dd>' + (remark || '\u2014') + '</dd>';
  html += '</dl>';"""

new_body = """  document.getElementById('modalTitle').textContent = 'Transaction Detail';
  let html = '<dl>';
  html += '<dt>Block Number</dt><dd>' + (blockNum ? '#' + blockNum : '\u2014') + '</dd>';
  html += '<dt>Method</dt><dd>' + (method || 'unknown') + '</dd>';
  html += '<dt>Signer Address</dt><dd>' + (signer || '\u2014') + '</dd>';
  html += '<dt>Remark Text</dt><dd>' + (remark || '\u2014') + '</dd>';
  html += '</dl>';"""

if old_body in h:
    h = h.replace(old_body, new_body)
    print("Fixed: showExtrinsic body updated")
else:
    print("showExtrinsic body not found (may use em-dash differently)")

with open("/var/www/verdiscan/explorer/index.html", "w") as f:
    f.write(h)
print(f"File saved: {len(h)} bytes")
