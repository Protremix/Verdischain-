// === VERDISCAN v2 — Solscan-inspired Transaction & Block Detail System ===

// --- Decoding helpers ---
function bytesToHex(bytes) {
  return '0x' + Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

function hexToBytes(hex) {
  hex = hex.replace('0x', '');
  const bytes = [];
  for (let i = 0; i < hex.length; i += 2) bytes.push(parseInt(hex.substr(i, 2), 16));
  return bytes;
}

function decodeCompact(bytes, offset) {
  const first = bytes[offset];
  const mode = first & 0b11;
  if (mode === 0b00) return { val: first >> 2, next: offset + 1 };
  if (mode === 0b01) return { val: ((first >> 2) | (bytes[offset + 1] << 6)) >>> 0, next: offset + 2 };
  if (mode === 0b10) return { val: ((first >> 2) | (bytes[offset+1] << 6) | (bytes[offset+2] << 14) | (bytes[offset+3] << 22)) >>> 0, next: offset + 4 };
  const byteCount = (first >> 2) + 4;
  let val = BigInt(0);
  for (let i = 0; i < byteCount; i++) val += BigInt(bytes[offset + 1 + i]) << BigInt(8 * i);
  return { val, next: offset + 1 + byteCount };
}

// --- Pallet/Call name maps ---
const PALLETS = {
  0: 'System', 1: 'Timestamp', 2: 'Balances', 3: 'Authorship',
  4: 'Staking', 5: 'Session', 6: 'Grandpa', 7: 'DPOS',
  8: 'AMMDex', 9: 'Eco', 10: 'Tokenomics', 11: 'Vesting',
  12: 'EVM', 13: 'Storage', 14: 'Utility', 15: 'TransactionPayment',
  16: 'Sudo', 17: 'Treasury', 18: 'Council',
};
const CALLS = {
  0: { 0: 'remark', 1: 'set_heap_pages', 2: 'set_code', 3: 'set_code_without_checks', 4: 'set_storage', 5: 'kill_storage', 6: 'kill_prefix' },
  1: { 0: 'set' },
  2: { 0: 'transfer', 1: 'set_balance', 2: 'force_transfer', 3: 'keep_alive', 4: 'transfer_all', 5: 'force_unreserve' },
  7: { 0: 'register_validator', 1: 'unregister_validator', 2: 'vote', 3: 'update_green_score', 4: 'slash_validator', 5: 'set_epoch_duration' },
  8: { 0: 'create_pool', 1: 'add_liquidity', 2: 'remove_liquidity', 3: 'swap', 4: 'set_fee' },
  9: { 0: 'mint_carbon_credit', 1: 'log_reforestation', 2: 'update_green_score', 3: 'retire_carbon_credit' },
  10: { 0: 'mint', 1: 'burn', 2: 'set_allocation', 3: 'enforce_vesting' },
  11: { 0: 'create_vesting_schedule', 1: 'claim_vested', 2: 'cancel_vesting_schedule' },
  14: { 0: 'batch', 1: 'as_derivative', 2: 'batch_all', 3: 'dispatch_as' },
};

// --- Decode extrinsic ---
function decodeExtrinsic(bytes, blockHash, blockNum) {
  if (!bytes || !bytes.length) return null;
  let offset = 0;
  const isSigned = (bytes[0] & 0b10000000) !== 0;
  let signer = null, signature = null, era = null, nonce = null, tip = null;
  let callPallet = null, callIndex = null, argsStart = 0;

  if (isSigned) {
    const eraByte = bytes[0] & 0b01111111;
    if (eraByte === 0) { era = bytesToHex([bytes[0]]); offset = 1; }
    else { era = bytesToHex([bytes[0], bytes[1]]); offset = 2; }
    if (offset + 64 <= bytes.length) { signature = bytesToHex(bytes.slice(offset, offset + 64)); offset += 64; }
    if (offset < bytes.length) {
      const prefix = bytes[offset];
      if (prefix === 0x00 && offset + 33 <= bytes.length) { signer = bytesToHex(bytes.slice(offset + 1, offset + 33)); offset += 33; }
      else if (offset + 32 <= bytes.length) { signer = bytesToHex(bytes.slice(offset, offset + 32)); offset += 32; }
    }
    if (offset < bytes.length) { const d = decodeCompact(bytes, offset); nonce = d.val !== undefined ? Number(d.val) : null; offset = d.next; }
    if (offset < bytes.length) { const d = decodeCompact(bytes, offset); tip = d.val !== undefined ? d.val.toString() : null; offset = d.next; }
  } else { offset = 1; }

  if (offset + 1 < bytes.length) { callPallet = bytes[offset]; callIndex = bytes[offset + 1]; argsStart = offset + 2; }

  const palletName = PALLETS[callPallet] || `Pallet(${callPallet})`;
  const callName = (CALLS[callPallet] && CALLS[callPallet][callIndex]) || `call_${callIndex}`;
  const argsHex = argsStart < bytes.length ? bytesToHex(bytes.slice(argsStart)) : '0x';

  // Decode common args
  let decodedArgs = {};
  let fromAddr = null, toAddr = null, amount = null, remarkText = null;

  if (callPallet === 2 && callIndex === 0) {
    // Balances.transfer(dest, value)
    try {
      let ao = argsStart;
      if (bytes[ao] === 0x00) { toAddr = bytesToHex(bytes.slice(ao + 1, ao + 33)); ao += 33; }
      else { toAddr = bytesToHex(bytes.slice(ao, ao + 32)); ao += 32; }
      const vd = decodeCompact(bytes, ao);
      amount = vd.val !== undefined ? Number(vd.val) : null;
      decodedArgs = { dest: toAddr, value: amount };
      fromAddr = signer; // from signer
    } catch (e) {}
  } else if (callPallet === 0 && callIndex === 0) {
    // System.remark
    try {
      const ld = decodeCompact(bytes, argsStart);
      const rl = Number(ld.val || 0);
      remarkText = new TextDecoder().decode(bytes.slice(ld.next, ld.next + rl));
      decodedArgs = { remark: remarkText };
    } catch (e) {}
  } else if (callPallet === 1 && callIndex === 0) {
    try { const td = decodeCompact(bytes, argsStart); decodedArgs = { timestamp: td.val !== undefined ? new Date(Number(td.val)).toISOString() : null }; } catch (e) {}
  } else if (callPallet === 9 && callIndex === 0) {
    // Eco.mint_carbon_credit
    try { decodedArgs = { raw: argsHex }; } catch (e) {}
  }

  return {
    hash: null, rawHex: bytesToHex(bytes), isSigned, signer, signature, era, nonce, tip,
    palletIndex: callPallet, callIndex, palletName, callName, callPath: `${palletName}.${callName}`,
    argsHex, decodedArgs, fromAddr, toAddr, amount, remarkText, blockNum, blockHash, size: bytes.length
  };
}

// --- SHA-256 based tx hash ---
async function generateTxHash(extrinsicBytes, blockHash, txIndex) {
  try {
    const idxBytes = new TextEncoder().encode(':' + blockHash + ':' + txIndex);
    const combined = new Uint8Array(extrinsicBytes.length + idxBytes.length);
    combined.set(extrinsicBytes, 0); combined.set(idxBytes, extrinsicBytes.length);
    const digest = await crypto.subtle.digest('SHA-256', combined);
    return '0x' + Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, '0')).join('');
  } catch (e) { return '0x' + bytesToHex(extrinsicBytes).slice(2, 66).padEnd(64, '0'); }
}

// --- Helpers ---
function shortHash(h) { if (!h || h.length < 20) return h || '—'; return h.slice(0, 10) + '…' + h.slice(-8); }
function shortAddr(a) { if (!a || a.length < 20) return a || '—'; return a.slice(0, 10) + '…' + a.slice(-8); }
function timeAgo(ts) { const d = Math.floor(Date.now()/1000) - ts; if (d < 60) return d + 's ago'; if (d < 3600) return Math.floor(d/60) + 'm ago'; if (d < 86400) return Math.floor(d/3600) + 'h ago'; return Math.floor(d/86400) + 'd ago'; }
function formatAmount(raw) { if (raw === null || raw === undefined) return '—'; return (raw / 1e12).toFixed(4) + ' VRDX'; }

// --- Plain English description ---
function describeTx(tx) {
  if (tx.palletName === 'Balances' && tx.callName === 'transfer') return `Transfer ${formatAmount(tx.amount)} from ${shortAddr(tx.fromAddr)} to ${shortAddr(tx.toAddr)}`;
  if (tx.palletName === 'System' && tx.callName === 'remark') return `Remark: "${tx.remarkText || ''}"`;
  if (tx.palletName === 'Timestamp') return 'Set block timestamp';
  if (tx.palletName === 'AMMDex' && tx.callName === 'swap') return 'AMM token swap';
  if (tx.palletName === 'AMMDex' && tx.callName === 'add_liquidity') return 'Add liquidity to AMM pool';
  if (tx.palletName === 'AMMDex' && tx.callName === 'create_pool') return 'Create new AMM pool';
  if (tx.palletName === 'Eco' && tx.callName === 'mint_carbon_credit') return 'Mint carbon credit on-chain';
  if (tx.palletName === 'Eco' && tx.callName === 'log_reforestation') return 'Log reforestation event';
  if (tx.palletName === 'DPOS' && tx.callName === 'register_validator') return 'Register as DPoS validator';
  if (tx.palletName === 'DPOS' && tx.callName === 'vote') return 'Vote for DPoS validator';
  if (tx.palletName === 'Tokenomics' && tx.callName === 'mint') return 'Mint VRDX tokens';
  if (tx.palletName === 'Vesting' && tx.callName === 'claim_vested') return 'Claim vested tokens';
  return `Call ${tx.callPath}`;
}

// --- Copy to clipboard ---
function copyToClipboard(text, label) {
  navigator.clipboard.writeText(text).then(() => {
    const toast = document.createElement('div');
    toast.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#0f172a;color:#caff33;padding:10px 20px;border-radius:8px;font-size:13px;font-weight:600;z-index:99999;box-shadow:0 4px 12px rgba(0,0,0,0.3);';
    toast.textContent = '✓ ' + label + ' copied';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
  }).catch(() => {});
}

// --- Copy icon SVG ---
const COPY_ICON = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';

// --- Modal system ---
function showModal(type) {
  let modal = document.getElementById('detailModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'detailModal';
    modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);backdrop-filter:blur(4px);z-index:10000;display:flex;align-items:flex-start;justify-content:center;padding:40px 20px;overflow-y:auto;';
    modal.innerHTML = `
      <div style="background:#f8fafc;border-radius:16px;max-width:820px;width:100%;margin:auto;box-shadow:0 20px 60px rgba(0,0,0,0.3);overflow:hidden;">
        <div style="display:flex;align-items:center;justify-content:space-between;padding:14px 20px;background:#fff;border-bottom:1px solid #e2e8f0;position:sticky;top:0;z-index:10;">
          <h2 id="modalTitle" style="font-size:15px;font-weight:700;color:#0f172a;margin:0;display:flex;align-items:center;gap:8px;">Loading…</h2>
          <button onclick="closeModal()" style="width:32px;height:32px;border-radius:8px;border:1px solid #e2e8f0;background:#f8fafc;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:16px;color:#64748b;">✕</button>
        </div>
        <div id="modalBody" style="padding:20px;max-height:calc(100vh - 100px);overflow-y:auto;"></div>
      </div>`;
    document.body.appendChild(modal);
    modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
  }
  modal.style.display = 'flex';
  document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#475569;"><div style="display:inline-block;width:24px;height:24px;border:3px solid #e2e8f0;border-top-color:#caff33;border-radius:50%;animation:spin 1s linear infinite;"></div><div style="margin-top:12px;font-size:13px;">Fetching from node…</div></div>';
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  const m = document.getElementById('detailModal');
  if (m) m.style.display = 'none';
  document.body.style.overflow = '';
  if (window.location.hash) history.replaceState(null, '', window.location.pathname + window.location.search);
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// --- Copyable field component ---
function copyableField(label, value, isAddr) {
  if (!value || value === '—') return `<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;"><span style="font-size:13px;color:#64748b;font-weight:500;">${label}</span><span style="font-size:13px;color:#64748b;">—</span></div>`;
  return `<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #f1f5f9;">
    <span style="font-size:13px;color:#64748b;font-weight:500;flex-shrink:0;">${label}</span>
    <div style="display:flex;align-items:center;gap:6px;min-width:0;">
      <span class="mono" style="font-size:12px;color:#0f172a;word-break:break-all;">${isAddr ? shortAddr(value) : (value.length > 50 ? shortHash(value) : value)}</span>
      <button onclick="copyToClipboard('${value}','${label}')" style="flex-shrink:0;width:28px;height:28px;border:1px solid #e2e8f0;border-radius:6px;background:#f8fafc;cursor:pointer;display:flex;align-items:center;justify-content:center;color:#64748b;padding:0;" onmouseover="this.style.borderColor='#caff33';this.style.color='#0f172a'" onmouseout="this.style.borderColor='#e2e8f0';this.style.color='#64748b'">${COPY_ICON}</button>
    </div>
  </div>`;
}

// --- Block detail ---
async function showBlockDetail(blockNum) {
  showModal('block');
  const hash = await rpc('chain_getBlockHash', [blockNum]);
  if (!hash) { document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">Block not found</div>'; return; }
  const block = await rpc('chain_getBlock', [hash]);
  if (!block || !block.block) { document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">Failed to fetch</div>'; return; }
  const header = block.block.header;
  const extrinsics = block.block.extrinsics || [];
  const decodedTxs = [];
  for (let idx = 0; idx < extrinsics.length; idx++) {
    const d = decodeExtrinsic(extrinsics[idx], hash, blockNum);
    if (d) { d.hash = await generateTxHash(extrinsics[idx], hash, idx); d.index = idx; decodedTxs.push(d); }
  }
  const latestHeader = await rpc('chain_getHeader', []);
  const latestNum = latestHeader ? parseInt(latestHeader.number, 16) : blockNum;
  const confirmations = Math.max(0, latestNum - blockNum);
  const timestampTx = decodedTxs.find(t => t.palletName === 'Timestamp');
  const blockTime = timestampTx && timestampTx.decodedArgs.timestamp ? new Date(timestampTx.decodedArgs.timestamp) : null;
  const relTime = blockTime ? timeAgo(Math.floor(blockTime.getTime() / 1000)) : '—';

  document.getElementById('modalTitle').innerHTML = `<span style="width:24px;height:24px;border-radius:6px;background:linear-gradient(135deg,#caff33,#00a86b);display:inline-flex;align-items:center;justify-content:center;color:#0f172a;font-size:11px;font-weight:700;">#${blockNum}</span> Block #${blockNum}`;

  document.getElementById('modalBody').innerHTML = `
    <!-- Summary -->
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:16px;">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
        <span style="font-size:13px;color:#64748b;">📦 Block</span>
        <span style="padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;background:#dcfce7;color:#16a34a;">✓ ${confirmations} CONFIRMATION${confirmations === 1 ? '' : 'S'}</span>
      </div>
      <div style="font-size:14px;color:#0f172a;font-weight:500;">${extrinsics.length} transaction${extrinsics.length === 1 ? '' : 's'} in this block</div>
      ${blockTime ? `<div style="font-size:12px;color:#64748b;margin-top:4px;">${relTime} · ${blockTime.toUTCString()}</div>` : ''}
    </div>

    <!-- Detail rows -->
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:0 16px;margin-bottom:16px;">
      ${copyableField('Block Hash', hash, false)}
      ${copyableField('Parent Hash', header.parentHash, false)}
      ${copyableField('State Root', header.stateRoot, false)}
      ${copyableField('Extrinsics Root', header.extrinsicsRoot, false)}
      <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;">
        <span style="font-size:13px;color:#64748b;font-weight:500;">Extrinsics</span>
        <span style="font-size:13px;color:#0f172a;font-weight:600;">${decodedTxs.filter(t=>t.isSigned).length} signed · ${decodedTxs.filter(t=>!t.isSigned).length} unsigned</span>
      </div>
    </div>

    <!-- Digest -->
    ${header.digest && header.digest.logs && header.digest.logs.length ? `
    <div style="margin-bottom:16px;">
      <div style="font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Digest Logs</div>
      ${header.digest.logs.map(log => `<div class="mono" style="font-size:11px;color:#64748b;background:#f8fafc;padding:8px 12px;border-radius:6px;margin-bottom:4px;word-break:break-all;border:1px solid #e2e8f0;">${log}</div>`).join('')}
    </div>` : ''}

    <!-- Transactions -->
    <div>
      <div style="font-size:13px;font-weight:600;color:#0f172a;margin-bottom:10px;">Transactions (${decodedTxs.length})</div>
      ${decodedTxs.length === 0 ? '<div style="padding:20px;text-align:center;color:#64748b;font-size:13px;">No transactions</div>' :
        decodedTxs.map(tx => `
          <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:8px;cursor:pointer;transition:border-color 200ms;" onmouseover="this.style.borderColor='#caff33'" onmouseout="this.style.borderColor='#e2e8f0'" onclick="showTxDetail('${tx.hash}',${blockNum},${tx.index})">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
              <div style="display:flex;align-items:center;gap:6px;">
                <span style="font-size:11px;color:#94a3b8;font-weight:500;">#${tx.index}</span>
                <span style="padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;background:#f1f5f9;color:#0f172a;">${tx.callPath}</span>
                ${tx.isSigned ? '<span style="padding:1px 6px;border-radius:4px;font-size:10px;font-weight:600;background:#dcfce7;color:#16a34a;">SIGNED</span>' : '<span style="padding:1px 6px;border-radius:4px;font-size:10px;font-weight:500;background:#f1f5f9;color:#64748b;">INHERENT</span>'}
              </div>
              <span style="font-size:11px;color:#94a3b8;">${tx.size}B</span>
            </div>
            <div style="font-size:12px;color:#475569;">${describeTx(tx)}</div>
            ${tx.signer ? `<div style="font-size:11px;color:#94a3b8;margin-top:4px;">Signer: <span class="mono">${shortAddr(tx.signer)}</span></div>` : ''}
          </div>`).join('')}
    </div>`;
}

// --- Transaction detail ---
async function showTxDetail(txHash, blockNum, txIndex) {
  showModal('tx');
  const hash = await rpc('chain_getBlockHash', [blockNum]);
  if (!hash) { document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">Block not found</div>'; return; }
  const block = await rpc('chain_getBlock', [hash]);
  if (!block || !block.block) { document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">Failed to fetch</div>'; return; }
  const extrinsics = block.block.extrinsics || [];
  if (txIndex >= extrinsics.length) { document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">Transaction not found</div>'; return; }
  const tx = decodeExtrinsic(extrinsics[txIndex], hash, blockNum);
  if (!tx) { document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">Decode failed</div>'; return; }
  tx.hash = txHash; tx.index = txIndex;

  const latestHeader = await rpc('chain_getHeader', []);
  const latestNum = latestHeader ? parseInt(latestHeader.number, 16) : blockNum;
  const confirmations = Math.max(0, latestNum - blockNum);

  // Get block timestamp
  const timestampTx = extrinsics.map((b, i) => decodeExtrinsic(b, hash, blockNum)).find(t => t && t.palletName === 'Timestamp');
  const blockTime = timestampTx && timestampTx.decodedArgs.timestamp ? new Date(timestampTx.decodedArgs.timestamp) : null;
  const relTime = blockTime ? timeAgo(Math.floor(blockTime.getTime() / 1000)) : '—';

  document.getElementById('modalTitle').innerHTML = `<span style="width:24px;height:24px;border-radius:6px;background:#0f172a;display:inline-flex;align-items:center;justify-content:center;color:#caff33;font-size:10px;font-weight:700;">TX</span> ${tx.callPath}`;

  // Build the full detail page
  document.getElementById('modalBody').innerHTML = `
    <!-- Summary -->
    <div style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:12px;padding:16px;margin-bottom:16px;">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
        <span style="font-size:13px;color:#caff33;font-weight:600;">⚡ Summary</span>
      </div>
      <div style="font-size:14px;color:#fff;font-weight:500;">${describeTx(tx)}</div>
      <div style="display:flex;gap:8px;margin-top:8px;">
        <span style="padding:2px 10px;border-radius:4px;font-size:11px;font-weight:600;background:rgba(34,197,94,0.2);color:#22c55e;">✓ SUCCESS</span>
        <span style="padding:2px 10px;border-radius:4px;font-size:11px;font-weight:500;background:rgba(255,255,255,0.1);color:#94a3b8;">${confirmations} confirmation${confirmations === 1 ? '' : 's'}</span>
        ${tx.isSigned ? '<span style="padding:2px 10px;border-radius:4px;font-size:11px;font-weight:500;background:rgba(204,255,51,0.15);color:#caff33;">SIGNED</span>' : '<span style="padding:2px 10px;border-radius:4px;font-size:11px;font-weight:500;background:rgba(255,255,255,0.1);color:#94a3b8;">INHERENT</span>'}
      </div>
    </div>

    <!-- From / To / Amount section (for transfers) -->
    ${tx.fromAddr || tx.toAddr ? `
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:16px;">
      <div style="font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px;">Transfer</div>
      <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
        <div style="flex:1;min-width:120px;">
          <div style="font-size:11px;color:#64748b;margin-bottom:4px;">FROM</div>
          <div style="display:flex;align-items:center;gap:4px;">
            <span class="mono" style="font-size:12px;color:#0f172a;">${tx.fromAddr ? shortAddr(tx.fromAddr) : '—'}</span>
            ${tx.fromAddr ? `<button onclick="copyToClipboard('${tx.fromAddr}','Address')" style="width:24px;height:24px;border:1px solid #e2e8f0;border-radius:4px;background:#f8fafc;cursor:pointer;display:flex;align-items:center;justify-content:center;color:#64748b;padding:0;">${COPY_ICON}</button>` : ''}
          </div>
        </div>
        <div style="color:#caff33;font-size:18px;">→</div>
        <div style="flex:1;min-width:120px;">
          <div style="font-size:11px;color:#64748b;margin-bottom:4px;">TO</div>
          <div style="display:flex;align-items:center;gap:4px;">
            <span class="mono" style="font-size:12px;color:#0f172a;">${tx.toAddr ? shortAddr(tx.toAddr) : '—'}</span>
            ${tx.toAddr ? `<button onclick="copyToClipboard('${tx.toAddr}','Address')" style="width:24px;height:24px;border:1px solid #e2e8f0;border-radius:4px;background:#f8fafc;cursor:pointer;display:flex;align-items:center;justify-content:center;color:#64748b;padding:0;">${COPY_ICON}</button>` : ''}
          </div>
        </div>
      </div>
      ${tx.amount !== null ? `<div style="margin-top:12px;padding-top:12px;border-top:1px solid #f1f5f9;">
        <div style="font-size:11px;color:#64748b;margin-bottom:4px;">AMOUNT</div>
        <div style="font-size:18px;font-weight:700;color:#0f172a;">${formatAmount(tx.amount)}</div>
      </div>` : ''}
    </div>` : ''}

    <!-- Key-Value Detail Rows -->
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:0 16px;margin-bottom:16px;">
      ${copyableField('Transaction Hash', txHash, false)}
      <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;">
        <span style="font-size:13px;color:#64748b;font-weight:500;">Block</span>
        <a onclick="closeModal();showBlockDetail(${blockNum});return false;" style="font-size:13px;color:#6366f1;text-decoration:none;cursor:pointer;font-weight:600;">#${blockNum}</a>
      </div>
      <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;">
        <span style="font-size:13px;color:#64748b;font-weight:500;">Timestamp</span>
        <span style="font-size:12px;color:#0f172a;">${relTime}${blockTime ? ' · ' + blockTime.toUTCString() : ''}</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;">
        <span style="font-size:13px;color:#64748b;font-weight:500;">Result</span>
        <span style="padding:2px 10px;border-radius:4px;font-size:11px;font-weight:600;background:#dcfce7;color:#16a34a;">SUCCESS</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;">
        <span style="font-size:13px;color:#64748b;font-weight:500;">Confirmations</span>
        <span style="font-size:13px;color:#0f172a;font-weight:600;">${confirmations}</span>
      </div>
      ${tx.signer ? copyableField('Signer', tx.signer, true) : '<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;"><span style="font-size:13px;color:#64748b;font-weight:500;">Signer</span><span style="font-size:13px;color:#64748b;">Unsigned (inherent)</span></div>'}
      <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;">
        <span style="font-size:13px;color:#64748b;font-weight:500;">Call</span>
        <span style="font-size:13px;color:#0f172a;font-weight:600;">${tx.callPath}</span>
      </div>
      ${tx.nonce !== null ? `<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;"><span style="font-size:13px;color:#64748b;font-weight:500;">Nonce</span><span style="font-size:13px;color:#0f172a;font-weight:600;">${tx.nonce}</span></div>` : ''}
      ${tx.tip ? `<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;"><span style="font-size:13px;color:#64748b;font-weight:500;">Tip</span><span style="font-size:13px;color:#0f172a;font-weight:600;">${tx.tip}</span></div>` : ''}
      ${tx.era ? `<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f1f5f9;"><span style="font-size:13px;color:#64748b;font-weight:500;">Era</span><span class="mono" style="font-size:12px;color:#0f172a;">${tx.era === '0x80' ? 'Immortal' : 'Mortal (' + tx.era + ')'}</span></div>` : ''}
      <div style="display:flex;justify-content:space-between;padding:10px 0;">
        <span style="font-size:13px;color:#64748b;font-weight:500;">Size</span>
        <span style="font-size:13px;color:#0f172a;font-weight:600;">${tx.size} bytes</span>
      </div>
    </div>

    <!-- Arguments -->
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:16px;">
      <div style="font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;">Arguments</div>
      ${Object.keys(tx.decodedArgs).length > 0 ? `
        <div style="display:grid;gap:6px;">
          ${Object.entries(tx.decodedArgs).map(([k, v]) => `
            <div style="display:flex;gap:8px;font-size:13px;padding:6px 0;border-bottom:1px solid #f8fafc;">
              <span style="color:#64748b;min-width:80px;font-weight:500;">${k}:</span>
              <span class="mono" style="color:#0f172a;word-break:break-all;flex:1;">${v}</span>
            </div>`).join('')}
        </div>` : '<div style="font-size:13px;color:#64748b;">No decoded arguments</div>'}
      <details style="margin-top:8px;">
        <summary style="font-size:12px;color:#6366f1;cursor:pointer;font-weight:500;">▶ Show raw arguments hex</summary>
        <div class="mono" style="font-size:11px;color:#64748b;margin-top:8px;word-break:break-all;background:#f8fafc;padding:8px;border-radius:6px;">${tx.argsHex}</div>
      </details>
    </div>

    <!-- Technical Details -->
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:16px;">
      <div style="font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;">Technical Details</div>
      ${tx.signature ? `
        <div style="margin-bottom:8px;">
          <div style="font-size:11px;color:#64748b;margin-bottom:4px;">Signature (sr25519)</div>
          <div class="mono" style="font-size:11px;color:#0f172a;word-break:break-all;background:#f8fafc;padding:8px;border-radius:6px;">${tx.signature}</div>
        </div>` : ''}
      <div style="margin-bottom:8px;">
        <div style="font-size:11px;color:#64748b;margin-bottom:4px;">Block Hash</div>
        <div class="mono" style="font-size:11px;color:#0f172a;word-break:break-all;background:#f8fafc;padding:8px;border-radius:6px;">${hash}</div>
      </div>
      <div>
        <div style="font-size:11px;color:#64748b;margin-bottom:4px;">Raw Extrinsic (SCALE-encoded)</div>
        <div class="mono" style="font-size:11px;color:#0f172a;word-break:break-all;max-height:150px;overflow-y:auto;background:#f8fafc;padding:8px;border-radius:6px;">${tx.rawHex}</div>
      </div>
    </div>`;
}

// --- Hash routing ---
function handleHashRoute() {
  const h = window.location.hash;
  if (!h) return;
  if (h.startsWith('#block:')) { const n = parseInt(h.replace('#block:', '')); if (!isNaN(n)) showBlockDetail(n); }
  else if (h.startsWith('#hash:')) { const bh = h.replace('#hash:', ''); rpc('chain_getBlock', [bh]).then(b => { if (b && b.block) showBlockDetail(parseInt(b.block.header.number, 16)); }); }
  else if (h.startsWith('#tx:')) { const p = h.replace('#tx:', '').split(':'); if (p.length >= 2) showTxDetail(p[0], parseInt(p[1]), parseInt(p[2] || 0)); }
}
window.addEventListener('hashchange', handleHashRoute);
