#!/usr/bin/env python3
"""Patch wallet loadHistory to use localStorage + API instead of only block scanning."""

with open('/var/www/verdiscan/wallet/index.html', 'r') as f:
    content = f.read()

# Replace the entire loadHistory function
old_start = 'async function loadHistory() {'
old_end = 'async function loadValidators() {'

si = content.find(old_start)
ei = content.find(old_end)
if si < 0 or ei < 0:
    print("ERROR: Could not find loadHistory boundaries")
    exit(1)

# Extract the showTxDetail and closeTxModal functions that are between loadHistory and loadValidators
# to preserve them
between = content[content.find('function showTxDetail'):ei]

new_func = '''async function loadHistory() {
  const wallet = loadWallet();
  if (!wallet) return;
  const container = document.getElementById('txHistory');
  if (!container) return;
  container.textContent = 'Loading transactions...';

  const myAddr = wallet.address;

  // === Helper: hex to bytes ===
  function hexToBytes(hex) {
    hex = hex.replace('0x', '');
    const bytes = [];
    for (let i = 0; i < hex.length; i += 2) {
      bytes.push(parseInt(hex.substr(i, 2), 16));
    }
    return bytes;
  }

  // === Helper: SCALE compact integer ===
  function readCompact(bytes, offset) {
    if (offset >= bytes.length) return { value: 0, nextOffset: offset };
    const first = bytes[offset];
    const mode = first & 0x03;
    if (mode === 0) {
      return { value: first >> 2, nextOffset: offset + 1 };
    } else if (mode === 1) {
      if (offset + 1 >= bytes.length) return { value: 0, nextOffset: offset + 1 };
      return { value: ((first | (bytes[offset + 1] << 8)) >> 2), nextOffset: offset + 2 };
    } else if (mode === 2) {
      if (offset + 3 >= bytes.length) return { value: 0, nextOffset: offset + 3 };
      let v = (first | (bytes[offset+1] << 8) | (bytes[offset+2] << 16) | (bytes[offset+3] << 24)) >> 2;
      return { value: v, nextOffset: offset + 4 };
    } else {
      if (offset + 5 >= bytes.length) return { value: 0, nextOffset: offset + 5 };
      let v = 0;
      const nBytes = (first >> 2) + 4;
      for (let b = 0; b < nBytes && offset + 1 + b < bytes.length; b++) {
        v += bytes[offset + 1 + b] * Math.pow(256, b);
      }
      return { value: v, nextOffset: offset + 1 + nBytes };
    }
  }

  // === Decode hex extrinsic ===
  function decodeExtrinsicTx(hexStr, blockNum, blockHash) {
    const bytes = hexToBytes(hexStr);
    if (bytes.length < 4) return null;
    let offset = 0;
    const lenResult = readCompact(bytes, offset);
    offset = lenResult.nextOffset;
    if (offset >= bytes.length) return null;
    const versionByte = bytes[offset];
    const isSigned = (versionByte & 0x80) !== 0;
    if (!isSigned) return null;
    offset++;
    if (offset >= bytes.length) return null;
    const sigType = bytes[offset];
    const sigLen = (sigType === 2) ? 65 : 64;
    offset += 1 + sigLen;
    if (offset + 33 > bytes.length) return null;
    offset += 1;
    let signerBytes = [];
    for (let s = offset; s < offset + 32; s++) signerBytes.push(bytes[s]);
    offset += 32;
    let signer = '';
    try { signer = ss58Encode(new Uint8Array(signerBytes), 909); } catch(e) {
      signer = '0x' + signerBytes.map(b => ('0' + b.toString(16)).slice(-2)).join('');
    }
    if (offset >= bytes.length) return null;
    if (bytes[offset] === 0) { offset += 1; } else { offset += 2; }
    const nonceResult = readCompact(bytes, offset);
    offset = nonceResult.nextOffset;
    const tipResult = readCompact(bytes, offset);
    offset = tipResult.nextOffset;
    if (offset + 1 >= bytes.length) return null;
    const palletIdx = bytes[offset];
    const funcIdx = bytes[offset + 1];
    offset += 2;
    if (palletIdx === 4 && (funcIdx === 0 || funcIdx === 3)) {
      if (offset >= bytes.length) return null;
      const destType = bytes[offset];
      offset += 1;
      if (destType === 0 && offset + 32 <= bytes.length) {
        let destBytes = [];
        for (let d = offset; d < offset + 32; d++) destBytes.push(bytes[d]);
        offset += 32;
        const valueResult = readCompact(bytes, offset);
        const valueRaw = valueResult.value;
        let destAddr = '';
        try { destAddr = ss58Encode(new Uint8Array(destBytes), 909); } catch(e) {
          destAddr = '0x' + destBytes.map(b => ('0' + b.toString(16)).slice(-2)).join('');
        }
        const vrdx = valueRaw / 1e9;
        return {
          signer: signer, dest: destAddr,
          value: vrdx.toFixed(4) + ' VRDX',
          method: funcIdx === 0 ? 'Transfer' : 'TransferKeepAlive',
          block: blockNum, blockHash: blockHash,
          hash: '0x' + bytes.slice(0, 8).map(b => ('0' + b.toString(16)).slice(-2)).join('')
        };
      }
    }
    if (palletIdx === 0 && funcIdx === 1) {
      return { signer: signer, dest: '', value: '', method: 'System.remark',
        block: blockNum, blockHash: blockHash,
        hash: '0x' + bytes.slice(0, 8).map(b => ('0' + b.toString(16)).slice(-2)).join('') };
    }
    return { signer: signer, dest: '', value: '', method: 'pallet_' + palletIdx + '_call_' + funcIdx,
      block: blockNum, blockHash: blockHash,
      hash: '0x' + bytes.slice(0, 8).map(b => ('0' + b.toString(16)).slice(-2)).join('') };
  }

  // === Load local tx history from localStorage ===
  function getLocalTxHistory() {
    try {
      const stored = JSON.parse(localStorage.getItem('verdis_tx_history') || '[]');
      return Array.isArray(stored) ? stored : [];
    } catch { return []; }
  }

  function saveLocalTx(tx) {
    const history = getLocalTxHistory();
    // Deduplicate by block + signer + dest
    const exists = history.find(t => t.block === tx.block && t.signer === tx.signer && t.dest === tx.dest);
    if (!exists) {
      history.push(tx);
      history.sort((a, b) => b.block - a.block);
      // Keep max 100
      if (history.length > 100) history.length = 100;
      localStorage.setItem('verdis_tx_history', JSON.stringify(history));
    }
  }

  // === Start with local history (instant) ===
  const localTxs = getLocalTxHistory().filter(t => t.signer === myAddr || t.dest === myAddr);

  // Render immediately from localStorage
  function renderTxs(txs) {
    txs.sort((a, b) => b.block - a.block);
    if (txs.length === 0) {
      container.textContent = 'No transactions found in recent blocks.';
      return;
    }
    // Deduplicate by block + signer
    const seen = new Set();
    const unique = [];
    for (const tx of txs) {
      const key = tx.block + ':' + tx.signer + ':' + (tx.dest || '');
      if (!seen.has(key)) { seen.add(key); unique.push(tx); }
    }

    container.replaceChildren();
    unique.slice(0, 30).forEach((tx, idx) => {
      const div = document.createElement('div');
      div.className = 'tx-item';
      div.style.cursor = 'pointer';
      div.onclick = () => showTxDetail(tx);

      const iconEl = document.createElement('span');
      iconEl.className = 'tx-icon';
      if (tx.type === 'received') {
        iconEl.textContent = '\\u2193';
        iconEl.style.color = '#16a34a';
      } else if (tx.type === 'sent') {
        iconEl.textContent = '\\u2191';
        iconEl.style.color = '#ef4444';
      } else {
        iconEl.textContent = '\\u25C6';
        iconEl.style.color = '#64748b';
      }
      const fromEl = document.createElement('span');
      fromEl.className = 'tx-from';
      if (tx.type === 'received') {
        fromEl.textContent = 'From: ' + (tx.signer || '?').slice(0, 12) + '...';
      } else if (tx.type === 'sent') {
        fromEl.textContent = 'To: ' + (tx.dest || '?').slice(0, 12) + '...';
      } else {
        fromEl.textContent = 'Remark: ' + (tx.value || '').slice(0, 30);
      }
      const blockEl = document.createElement('span');
      blockEl.className = 'tx-block';
      blockEl.textContent = '#' + tx.block;
      const amtEl = document.createElement('span');
      amtEl.className = 'tx-amount';
      if (tx.type === 'received') {
        amtEl.textContent = '+ ' + (tx.value || '');
        amtEl.style.color = '#16a34a';
      } else if (tx.type === 'sent') {
        amtEl.textContent = '- ' + (tx.value || '');
        amtEl.style.color = '#ef4444';
      } else {
        amtEl.textContent = '';
      }
      div.appendChild(iconEl);
      div.appendChild(fromEl);
      div.appendChild(blockEl);
      div.appendChild(amtEl);
      container.appendChild(div);
    });
  }

  // Show local txs right away
  if (localTxs.length > 0) {
    renderTxs(localTxs);
  }

  // === Then scan recent blocks for new txs (async, merge with local) ===
  try {
    const header = await rpcCall('chain_getHeader', []);
    if (!header) {
      if (localTxs.length === 0) container.textContent = 'Cannot connect to node.';
      return;
    }
    const currentBlock = parseInt(header.number, 16);

    // Also try the API endpoint for broader coverage
    let apiTxs = [];
    try {
      const resp = await fetch('/api/v1/account/' + myAddr + '/transactions?limit=100');
      if (resp.ok) {
        const data = await resp.json();
        if (data.success && data.data) {
          apiTxs = data.data.map(t => ({
            hash: t.hash || '',
            block: t.block || 0,
            type: 'sent',
            signer: t.signer || '',
            dest: t.dest || '',
            method: t.method || 'Transfer',
            value: t.value || ''
          }));
        }
      }
    } catch {}

    // Scan blocks in parallel batches
    const SCAN_RANGE = 50;
    const BATCH_SIZE = 10;
    const scannedTxs = [];
    for (let batchStart = 0; batchStart < SCAN_RANGE && currentBlock - batchStart > 0 && scannedTxs.length < 30; batchStart += BATCH_SIZE) {
      const batchEnd = Math.min(batchStart + BATCH_SIZE, SCAN_RANGE, currentBlock);
      const blockNums = [];
      for (let i = batchStart; i < batchEnd; i++) blockNums.push(currentBlock - i);

      const blocks = await Promise.all(blockNums.map(async (bn) => {
        const hash = await rpcCall('chain_getBlockHash', [bn]);
        if (!hash) return null;
        const block = await rpcCall('chain_getBlock', [hash]);
        if (!block || !block.block || !block.block.extrinsics) return null;
        return { bn, hash, extrinsics: block.block.extrinsics };
      }));

      for (const blk of blocks) {
        if (!blk || scannedTxs.length >= 30) continue;
        for (const ext of blk.extrinsics) {
          const extHex = typeof ext === 'string' ? ext : '0x' + ext.map(b => ('0' + b.toString(16)).slice(-2)).join('');
          const decoded = decodeExtrinsicTx(extHex, blk.bn, blk.hash);
          if (!decoded) continue;

          const isSent = decoded.signer === myAddr;
          const isReceived = decoded.dest === myAddr;

          if (isSent || isReceived) {
            const tx = {
              hash: decoded.hash,
              block: blk.bn,
              type: isSent ? 'sent' : 'received',
              signer: decoded.signer,
              dest: decoded.dest,
              method: decoded.method,
              value: decoded.value
            };
            scannedTxs.push(tx);
            // Save to localStorage for future
            saveLocalTx(tx);
          }
        }
      }
    }

    // Merge local + scanned + API, deduplicate
    const allTxs = [...localTxs, ...scannedTxs, ...apiTxs];
    renderTxs(allTxs);

  } catch(e) {
    if (localTxs.length === 0) {
      container.textContent = 'Failed to load: ' + (e.message || 'error');
    } else {
      // Keep showing local txs even if scan fails
      renderTxs(localTxs);
    }
  }
}

'''

# Replace from old_start to old_end, preserving the showTxDetail/closeTxModal functions
new_content = content[:si] + new_func + between + content[ei:]

with open('/var/www/verdiscan/wallet/index.html', 'w') as f:
    f.write(new_content)
print("PATCHED: localStorage tx history + API + block scan merge")
