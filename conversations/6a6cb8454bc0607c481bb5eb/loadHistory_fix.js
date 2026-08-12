// Improved loadHistory - detects both sent AND received transactions
async function loadHistory() {
  const wallet = loadWallet();
  if (!wallet) return;
  const container = document.getElementById('txHistory');
  if (!container) return;
  container.textContent = 'Loading transactions...';

  try {
    // First try the API endpoint for sent transactions
    let txs = [];
    try {
      const resp = await fetch(`${API_URL}/account/${wallet.address}/transactions?limit=50`);
      const data = await resp.json();
      if (data.success && data.data) {
        for (const tx of data.data) {
          txs.push({
            hash: tx.hash || '',
            block: tx.block || 0,
            type: 'sent',
            signer: tx.signer || wallet.address,
            method: tx.method || 'Transfer',
            value: tx.value || '',
            dest: tx.dest || ''
          });
        }
      }
    } catch {}

    // Also scan recent blocks for received transactions (Balances.transfer_allow_death where dest = wallet)
    const header = await rpcCall('chain_getHeader', []);
    if (!header) {
      if (txs.length === 0) { container.textContent = 'Cannot connect to node.'; return; }
    } else {
      const currentBlock = parseInt(header.number, 16);
      const myAddr = wallet.address;

      for (let i = 0; i < 100 && currentBlock - i > 0; i++) {
        if (txs.length >= 30) break;
        const bn = currentBlock - i;
        const blockHash = await rpcCall('chain_getBlockHash', [bn]);
        if (!blockHash) continue;
        const blockData = await rpcCall('chain_getBlock', [blockHash]);
        if (!blockData || !blockData.block || !blockData.block.extrinsics) continue;

        for (const ext of blockData.block.extrinsics) {
          if (!ext.signature || !ext.signature.signer) continue;
          const signer = ext.signature.signer.id || ext.signature.signer || '';
          const callHex = ext.method || ext.call || '';

          // Check if this is a Balances.transfer_allow_death (pallet 5, call 3)
          // Call hex format: 0x + pallet_index(1 byte) + call_index(1 byte) + params
          if (callHex && callHex.length > 10) {
            const callBytes = callHex.replace('0x', '');
            const palletIdx = callBytes.slice(0, 2);
            const callIdx = callBytes.slice(2, 4);

            // Balances.transfer_allow_death = 0503 or similar
            // Also check transfer (0500) and transfer_keep_alive (0505)
            // The dest is SCALE-encoded: 00 + 32 bytes AccountId
            // The value is SCALE compact-encoded u128

            // Try to detect any Balances transfer call
            if (callBytes.length >= 72) {
              // Check for AccountId32 encoding (0x00 + 32 bytes)
              const destPrefix = callBytes.slice(4, 6);
              if (destPrefix === '00') {
                // Extract 32-byte destination address
                const destHex = callBytes.slice(6, 70); // 32 bytes = 64 hex chars
                // Convert hex to SS58 address
                try {
                  // SS58 encode the 32-byte public key
                  const destBytes = new Uint8Array(32);
                  for (let j = 0; j < 32; j++) {
                    destBytes[j] = parseInt(destHex.slice(j*2, j*2+2), 16);
                  }
                  const destAddr = ss58Encode(destBytes, 909);

                  // Extract compact-encoded value (after the 32-byte dest)
                  // Compact u128: first 2 bits of next byte determine encoding
                  const valueStart = 70; // after 0x + pallet(2) + call(2) + 00(2) + 32bytes(64)
                  let value = '';
                  try {
                    const valueBytes = callBytes.slice(valueStart);
                    // Simple compact decoding for small values
                    const firstByte = parseInt(valueBytes.slice(0, 2), 16);
                    const mode = firstByte & 0x03;
                    if (mode === 0) {
                      // Single byte
                      value = (firstByte >> 2).toString();
                    } else if (mode === 1) {
                      // Two bytes
                      const secondByte = parseInt(valueBytes.slice(2, 4), 16);
                      value = ((firstByte >> 2) + secondByte * 64).toString();
                    } else if (mode === 2) {
                      // Four bytes
                      let v = firstByte >> 2;
                      for (let b = 1; b < 4; b++) {
                        v += parseInt(valueBytes.slice(b*2, b*2+2), 16) * Math.pow(256, b) / 4;
                      }
                      value = Math.floor(v).toString();
                    } else {
                      // Big integer mode
                      value = '(large)';
                    }
                    // Format as VRDX
                    if (value !== '(large)') {
                      const vrdx = parseInt(value) / 10**9;
                      value = vrdx.toFixed(4) + ' VRDX';
                    }
                  } catch {}

                  // Check if this involves our wallet
                  const isSent = signer === myAddr || (myAddr && signer && signer === myAddr);
                  const isReceived = destAddr === myAddr;

                  if (isSent || isReceived) {
                    // Check if we already have this tx
                    const existing = txs.find(t => t.block === bn && t.signer === signer);
                    if (!existing) {
                      txs.push({
                        hash: ext.hash || blockHash,
                        block: bn,
                        type: isSent ? 'sent' : 'received',
                        signer: signer,
                        dest: destAddr,
                        method: 'Transfer',
                        value: value
                      });
                    }
                  }
                } catch {}
              }
            }

            // Also detect system.remark (0x0001)
            if (callHex.startsWith('0x0001') && signer === myAddr) {
              let remark = 'System.remark';
              try {
                const bytes = callHex.slice(6);
                const len = parseInt(bytes.slice(0, 4), 16);
                if (len > 0 && len < 256) {
                  const remarkHex = bytes.slice(4, 4 + len * 2);
                  remark = decodeURIComponent(remarkHex.replace(/../g, '%$&'));
                }
              } catch {}
              const existing = txs.find(t => t.block === bn && t.signer === signer);
              if (!existing) {
                txs.push({
                  hash: ext.hash || blockHash,
                  block: bn,
                  type: 'remark',
                  signer: signer,
                  method: 'System.remark',
                  value: remark
                });
              }
            }
          }
        }
      }
    }

    // Sort by block number descending
    txs.sort((a, b) => b.block - a.block);

    if (txs.length === 0) {
      container.textContent = 'No transactions found in recent blocks.';
      return;
    }

    // Safe DOM construction (no innerHTML) to prevent XSS
    container.replaceChildren();
    txs.forEach(tx => {
      const div = document.createElement('div');
      div.className = 'tx-item';

      const iconEl = document.createElement('span');
      iconEl.className = 'tx-icon';
      if (tx.type === 'received') {
        iconEl.textContent = '↓';
        iconEl.style.color = '#16a34a';
      } else if (tx.type === 'sent') {
        iconEl.textContent = '↑';
        iconEl.style.color = '#ef4444';
      } else {
        iconEl.textContent = '◆';
        iconEl.style.color = '#64748b';
      }

      const fromEl = document.createElement('span');
      fromEl.className = 'tx-from';
      fromEl.textContent = tx.type === 'received' ? 'From: ' + (tx.signer || 'Unknown').slice(0, 12) + '...' : 'To: ' + (tx.dest || tx.signer || 'Unknown').slice(0, 12) + '...';

      const blockEl = document.createElement('span');
      blockEl.className = 'tx-block';
      blockEl.textContent = '#' + tx.block;

      const amtEl = document.createElement('span');
      amtEl.className = 'tx-amount';
      amtEl.textContent = tx.value || tx.method || '';

      div.appendChild(iconEl);
      div.appendChild(fromEl);
      div.appendChild(blockEl);
      div.appendChild(amtEl);
      container.appendChild(div);
    });

  } catch(e) {
    container.textContent = 'Failed to load: ' + (e.message || 'error');
  }
}
