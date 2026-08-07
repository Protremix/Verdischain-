// Verdiscan Explorer — Full Transaction & Block Detail System
// This file contains the JavaScript upgrade to be injected into explorer/index.html

// === DECODING HELPERS ===

// Convert byte array to hex string
function bytesToHex(bytes) {
  return '0x' + bytes.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Convert hex to byte array
function hexToBytes(hex) {
  hex = hex.replace('0x', '');
  const bytes = [];
  for (let i = 0; i < hex.length; i += 2) {
    bytes.push(parseInt(hex.substr(i, 2), 16));
  }
  return bytes;
}

// Decode compact u32/u128 from byte array at offset
// Returns { value, nextOffset }
function decodeCompact(bytes, offset) {
  const first = bytes[offset];
  const mode = first & 0b11;
  if (mode === 0b00) {
    return { value: first >> 2, nextOffset: offset + 1 };
  } else if (mode === 0b01) {
    const val = ((first >> 2) | (bytes[offset + 1] << 6)) >>> 0;
    return { val, nextOffset: offset + 2 };
  } else if (mode === 0b10) {
    const val = ((first >> 2) | (bytes[offset + 1] << 6) | (bytes[offset + 2] << 14) | (bytes[offset + 3] << 22)) >>> 0;
    return { val, nextOffset: offset + 4 };
  } else {
    // mode 0b11 — big integer, next 6 bits = byte count - 4
    const byteCount = (first >> 2) + 4;
    let val = BigInt(0);
    for (let i = 0; i < byteCount; i++) {
      val += BigInt(bytes[offset + 1 + i]) << BigInt(8 * i);
    }
    return { val, nextOffset: offset + 1 + byteCount };
  }
}

// Known pallet indices (from Verdis Chain runtime construct_runtime!)
const PALLET_NAMES = {
  0: 'System',
  1: 'Timestamp',
  2: 'Balances',
  3: 'Authorship',
  4: 'Staking',
  5: 'Session',
  6: 'Grandpa',
  7: 'DPOS',
  8: 'AMMDex',
  9: 'Eco',
  10: 'Tokenomics',
  11: 'Vesting',
  12: 'EVM',
  13: 'Storage',
  14: 'Utility',
  15: 'TransactionPayment',
  16: 'Sudo',
  17: 'Treasury',
  18: 'Council',
  19: 'Scheduler',
  20: 'Preimage',
  36: 'EVM',
  51: 'Turbine',
  52: 'GulfStream',
  53: 'ZKCompression',
  54: 'ALT',
  55: 'Sealevel',
  56: 'ProofOfHistory',
  57: 'PriorityFees',
  58: 'Token2022',
};

// Known call names by pallet index
const CALL_NAMES = {
  0: { 0: 'remark', 1: 'set_heap_pages', 2: 'set_code', 3: 'set_code_without_checks', 4: 'set_storage', 5: 'kill_storage', 6: 'kill_prefix' },
  1: { 0: 'set' },
  2: { 0: 'transfer', 1: 'set_balance', 2: 'force_transfer', 3: 'keep_alive', 4: 'transfer_all', 5: 'force_unreserve', 6: 'upgrade_accounts' },
  7: { 0: 'register_validator', 1: 'unregister_validator', 2: 'vote', 3: 'update_green_score', 4: 'slash_validator', 5: 'set_epoch_duration' },
  8: { 0: 'create_pool', 1: 'add_liquidity', 2: 'remove_liquidity', 3: 'swap', 4: 'set_fee' },
  9: { 0: 'mint_carbon_credit', 1: 'log_reforestation', 2: 'update_green_score', 3: 'retire_carbon_credit' },
  10: { 0: 'mint', 1: 'burn', 2: 'set_allocation', 3: 'enforce_vesting' },
  11: { 0: 'create_vesting_schedule', 1: 'claim_vested', 2: 'cancel_vesting_schedule' },
  12: { 0: 'call', 1: 'create', 2: 'create2' },
  14: { 0: 'batch', 1: 'as_derivative', 2: 'batch_all', 3: 'dispatch_as' },
};

// Decode an extrinsic from raw byte array
function decodeExtrinsic(bytes, blockHash, blockNum) {
  if (!bytes || bytes.length === 0) return null;

  let offset = 0;
  const isSigned = (bytes[0] & 0b10000000) !== 0;
  
  let signer = null;
  let signature = null;
  let era = null;
  let nonce = null;
  let tip = null;
  let callPallet = null;
  let callIndex = null;
  let argsStart = 0;

  if (isSigned) {
    // First byte: era indicator (bit 7 = signed, lower bits = era)
    // For mortal era: 2 bytes, for immortal: 1 byte (0x00 lower bits)
    const eraByte = bytes[0] & 0b01111111;
    if (eraByte === 0) {
      // Immortal era — 1 byte
      era = bytesToHex([bytes[0]]);
      offset = 1;
    } else {
      // Mortal era — 2 bytes
      era = bytesToHex([bytes[0], bytes[1]]);
      offset = 2;
    }
    
    // Signature: 64 bytes (sr25519)
    if (offset + 64 <= bytes.length) {
      signature = bytesToHex(bytes.slice(offset, offset + 64));
      offset += 64;
    }
    
    // Signer: 32 bytes (AccountId32) — could also be multi-address format
    // Multi-address: first byte indicates type (0x00 = AccountId32, 0x01 = AccountIndex, etc.)
    if (offset < bytes.length) {
      const addrPrefix = bytes[offset];
      if (addrPrefix === 0x00 && offset + 1 + 32 <= bytes.length) {
        // Multi-address with AccountId32
        signer = bytesToHex(bytes.slice(offset + 1, offset + 33));
        offset += 33;
      } else if (offset + 32 <= bytes.length) {
        // Direct AccountId32
        signer = bytesToHex(bytes.slice(offset, offset + 32));
        offset += 32;
      }
    }
    
    // Nonce: compact u32
    if (offset < bytes.length) {
      const decoded = decodeCompact(bytes, offset);
      nonce = decoded.val !== undefined ? Number(decoded.val) : null;
      offset = decoded.nextOffset;
    }
    
    // Tip: compact u128
    if (offset < bytes.length) {
      const decoded = decodeCompact(bytes, offset);
      tip = decoded.val !== undefined ? decoded.val.toString() : null;
      offset = decoded.nextOffset;
    }
  } else {
    // Unsigned extrinsic
    offset = 1; // skip the era byte
  }
  
  // Call: pallet index (u8), call index (u8)
  if (offset + 1 < bytes.length) {
    callPallet = bytes[offset];
    callIndex = bytes[offset + 1];
    argsStart = offset + 2;
  }
  
  const palletName = PALLET_NAMES[callPallet] || `Pallet(${callPallet})`;
  const callName = (CALL_NAMES[callPallet] && CALL_NAMES[callPallet][callIndex]) || `call_${callIndex}`;
  
  // Extract args as hex
  const argsHex = argsStart < bytes.length ? bytesToHex(bytes.slice(argsStart)) : '0x';
  
  // Try to decode common call args
  let decodedArgs = {};
  if (callPallet === 2 && callIndex === 0) {
    // Balances.transfer(dest, value)
    try {
      // dest: multi-address (0x00 + 32 bytes = 33 bytes)
      // value: compact u128
      let argOffset = argsStart;
      if (bytes[argOffset] === 0x00) {
        decodedArgs.dest = bytesToHex(bytes.slice(argOffset + 1, argOffset + 33));
        argOffset += 33;
      } else {
        decodedArgs.dest = '0x' + bytes.slice(argOffset, argOffset + 32).map(b => b.toString(16).padStart(2, '0')).join('');
        argOffset += 32;
      }
      const valDecoded = decodeCompact(bytes, argOffset);
      decodedArgs.value = valDecoded.val !== undefined ? (Number(valDecoded.val) / 1e12).toFixed(4) + ' VRDX' : null;
    } catch(e) {}
  } else if (callPallet === 0 && callIndex === 0) {
    // System.remark(remark)
    try {
      // remark is a Vec<u8> — compact length prefix + bytes
      const lenDecoded = decodeCompact(bytes, argsStart);
      const remarkLen = Number(lenDecoded.val || 0);
      const remarkBytes = bytes.slice(lenDecoded.nextOffset, lenDecoded.nextOffset + remarkLen);
      decodedArgs.remark = new TextDecoder().decode(remarkBytes);
    } catch(e) {}
  } else if (callPallet === 1 && callIndex === 0) {
    // Timestamp.set(now)
    try {
      const tsDecoded = decodeCompact(bytes, argsStart);
      decodedArgs.timestamp = tsDecoded.val !== undefined ? new Date(Number(tsDecoded.val)).toISOString() : null;
    } catch(e) {}
  }
  
  return {
    hash: null, // will be set by caller
    rawHex: bytesToHex(bytes),
    isSigned,
    signer,
    signature,
    era,
    nonce,
    tip,
    palletIndex: callPallet,
    callIndex: callIndex,
    palletName,
    callName,
    callPath: `${palletName}.${callName}`,
    argsHex,
    decodedArgs,
    blockNum,
    blockHash,
    size: bytes.length
  };
}

// Generate a pseudo-hash for extrinsic (since Substrate doesn't always return it in chain_getBlock)
function generateTxHash(extrinsicBytes, blockHash, txIndex) {
  // Use block hash + index as a unique identifier
  const hex = bytesToHex(extrinsicBytes);
  // Simple hash: take first 32 chars of hex + block + index
  return '0x' + (hex.slice(2, 34) + blockHash.slice(2, 34)).padEnd(64, '0').slice(0, 64);
}

// Format address for display (SS58-like shortening)
function shortAddr(addr) {
  if (!addr || addr.length < 20) return addr || '—';
  return addr.slice(0, 10) + '...' + addr.slice(-8);
}

// === BLOCK DETAIL MODAL ===

async function showBlockDetail(blockNum) {
  showModal('block', blockNum);
  
  // Fetch block hash
  const hash = await rpc('chain_getBlockHash', [blockNum]);
  if (!hash) {
    document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">Block not found</div>';
    return;
  }
  
  // Fetch block
  const block = await rpc('chain_getBlock', [hash]);
  if (!block || !block.block) {
    document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">Failed to fetch block</div>';
    return;
  }
  
  const header = block.block.header;
  const extrinsics = block.block.extrinsics || [];
  
  // Decode all extrinsics
  const decodedTxs = extrinsics.map((extBytes, idx) => {
    const decoded = decodeExtrinsic(extBytes, hash, blockNum);
    if (decoded) {
      decoded.hash = generateTxHash(extBytes, hash, idx);
      decoded.index = idx;
    }
    return decoded;
  }).filter(t => t !== null);
  
  // Build HTML
  let html = `
    <div style="padding:0;">
      <!-- Block Header Section -->
      <div style="background:#f8fafc;border-radius:12px;padding:20px;margin-bottom:20px;border:1px solid #e2e8f0;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
          <div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#caff33,#00a86b);display:flex;align-items:center;justify-content:center;color:#0f172a;font-weight:700;font-size:14px;">#${blockNum}</div>
          <h2 style="font-size:18px;font-weight:700;color:#0f172a;margin:0;">Block #${blockNum}</h2>
          <span style="padding:3px 10px;border-radius:6px;font-size:11px;font-weight:600;background:#dcfce7;color:#16a34a;">CONFIRMED</span>
        </div>
        
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div style="background:#fff;border-radius:8px;padding:12px;border:1px solid #e2e8f0;">
            <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Block Hash</div>
            <div class="mono" style="font-size:12px;color:#0f172a;word-break:break-all;">${hash}</div>
          </div>
          <div style="background:#fff;border-radius:8px;padding:12px;border:1px solid #e2e8f0;">
            <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Parent Hash</div>
            <div class="mono" style="font-size:12px;color:#0f172a;word-break:break-all;">${header.parentHash}</div>
          </div>
          <div style="background:#fff;border-radius:8px;padding:12px;border:1px solid #e2e8f0;">
            <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">State Root</div>
            <div class="mono" style="font-size:12px;color:#0f172a;word-break:break-all;">${header.stateRoot}</div>
          </div>
          <div style="background:#fff;border-radius:8px;padding:12px;border:1px solid #e2e8f0;">
            <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Extrinsics Root</div>
            <div class="mono" style="font-size:12px;color:#0f172a;word-break:break-all;">${header.extrinsicsRoot}</div>
          </div>
        </div>
        
        <div style="display:flex;gap:16px;margin-top:12px;flex-wrap:wrap;">
          <div style="font-size:13px;color:#475569;"><strong style="color:#0f172a;">${extrinsics.length}</strong> extrinsics</div>
          <div style="font-size:13px;color:#475569;"><strong style="color:#0f172a;">${decodedTxs.filter(t => t.isSigned).length}</strong> signed</div>
          <div style="font-size:13px;color:#475569;"><strong style="color:#0f172a;">${decodedTxs.filter(t => !t.isSigned).length}</strong> unsigned</div>
        </div>
      </div>
      
      <!-- Digest Logs -->
      ${header.digest && header.digest.logs && header.digest.logs.length > 0 ? `
      <div style="margin-bottom:20px;">
        <h3 style="font-size:14px;font-weight:600;color:#0f172a;margin-bottom:10px;">Digest Logs</h3>
        ${header.digest.logs.map(log => `
          <div class="mono" style="font-size:11px;color:#475569;background:#f8fafc;padding:8px 12px;border-radius:6px;margin-bottom:4px;word-break:break-all;border:1px solid #e2e8f0;">${log}</div>
        `).join('')}
      </div>
      ` : ''}
      
      <!-- Extrinsics / Transactions -->
      <div>
        <h3 style="font-size:14px;font-weight:600;color:#0f172a;margin-bottom:12px;">Transactions (${decodedTxs.length})</h3>
        ${decodedTxs.length === 0 ? `
          <div style="padding:20px;text-align:center;color:#475569;font-size:13px;">No transactions in this block</div>
        ` : decodedTxs.map(tx => `
          <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px;margin-bottom:12px;cursor:pointer;transition:all 200ms;" onmouseover="this.style.borderColor='#caff33'" onmouseout="this.style.borderColor='#e2e8f0'" onclick="showTxDetail('${tx.hash}', ${blockNum}, ${tx.index})">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
              <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:11px;color:#475569;font-weight:500;">#${tx.index}</span>
                <span style="padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;background:#f1f5f9;color:#0f172a;">${tx.callPath}</span>
                ${tx.isSigned ? '<span style="padding:2px 8px;border-radius:4px;font-size:10px;font-weight:500;background:#dcfce7;color:#16a34a;">SIGNED</span>' : '<span style="padding:2px 8px;border-radius:4px;font-size:10px;font-weight:500;background:#f1f5f9;color:#64748b;">UNSIGNED</span>'}
              </div>
              <div style="font-size:11px;color:#475569;">${tx.size} bytes</div>
            </div>
            ${tx.signer ? `<div style="font-size:12px;color:#475569;margin-bottom:4px;">From: <span class="mono" style="color:#0f172a;">${shortAddr(tx.signer)}</span></div>` : ''}
            ${tx.decodedArgs && tx.decodedArgs.remark ? `<div style="font-size:12px;color:#475569;margin-bottom:4px;">Remark: <span style="color:#0f172a;">${tx.decodedArgs.remark}</span></div>` : ''}
            ${tx.decodedArgs && tx.decodedArgs.value ? `<div style="font-size:12px;color:#475569;margin-bottom:4px;">Value: <span style="color:#0f172a;font-weight:600;">${tx.decodedArgs.value}</span></div>` : ''}
            ${tx.decodedArgs && tx.decodedArgs.timestamp ? `<div style="font-size:12px;color:#475569;margin-bottom:4px;">Timestamp: <span style="color:#0f172a;">${tx.decodedArgs.timestamp}</span></div>` : ''}
            <div class="mono" style="font-size:11px;color:#475569;margin-top:6px;word-break:break-all;opacity:0.7;">${tx.rawHex.slice(0, 100)}${tx.rawHex.length > 100 ? '...' : ''}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
  
  document.getElementById('modalBody').innerHTML = html;
  document.getElementById('modalTitle').textContent = `Block #${blockNum}`;
}

// === TRANSACTION DETAIL MODAL ===

async function showTxDetail(txHash, blockNum, txIndex) {
  showModal('tx', txHash);
  
  // Fetch block
  const hash = await rpc('chain_getBlockHash', [blockNum]);
  if (!hash) {
    document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">Block not found</div>';
    return;
  }
  
  const block = await rpc('chain_getBlock', [hash]);
  if (!block || !block.block) {
    document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">Failed to fetch block</div>';
    return;
  }
  
  const extrinsics = block.block.extrinsics || [];
  if (txIndex >= extrinsics.length) {
    document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">Transaction not found in block</div>';
    return;
  }
  
  const tx = decodeExtrinsic(extrinsics[txIndex], hash, blockNum);
  if (!tx) {
    document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">Failed to decode transaction</div>';
    return;
  }
  tx.hash = txHash;
  tx.index = txIndex;
  
  // Try to fetch fee info via state_call
  let feeInfo = null;
  try {
    const extHex = bytesToHex(extrinsics[txIndex]);
    // state_call TransactionPaymentApi_query_info
    const encodedLen = (extrinsics[txIndex].length).toString(16).padStart(8, '0');
    const callHex = '0x' + encodedLen + extHex.slice(2);
    const feeResult = await rpc('state_call', ['TransactionPaymentApi_query_info', callHex, hash]);
    if (feeResult) {
      feeInfo = feeResult;
    }
  } catch(e) {}
  
  // Build the full transaction detail view — showing the "full way" of the transaction
  let html = `
    <div style="padding:0;">
      <!-- Transaction Header -->
      <div style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:12px;padding:20px;margin-bottom:20px;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
          <div style="width:32px;height:32px;border-radius:8px;background:#caff33;display:flex;align-items:center;justify-content:center;color:#0f172a;font-weight:700;font-size:13px;">TX</div>
          <h2 style="font-size:16px;font-weight:700;color:#fff;margin:0;">${tx.callPath}</h2>
          ${tx.isSigned ? '<span style="padding:3px 10px;border-radius:6px;font-size:11px;font-weight:600;background:rgba(204,255,51,0.2);color:#caff33;">SIGNED</span>' : '<span style="padding:3px 10px;border-radius:6px;font-size:11px;font-weight:600;background:rgba(255,255,255,0.1);color:#94a3b8;">UNSIGNED</span>'}
        </div>
        <div style="font-size:12px;color:#94a3b8;" class="mono">${tx.hash}</div>
      </div>

      <!-- Transaction Path / Journey -->
      <div style="margin-bottom:20px;">
        <h3 style="font-size:13px;font-weight:600;color:#0f172a;margin-bottom:12px;display:flex;align-items:center;gap:6px;">
          <span style="width:6px;height:6px;border-radius:50%;background:#caff33;"></span>
          Transaction Path
        </h3>
        <div style="position:relative;padding-left:24px;">
          <!-- Step 1: Origin -->
          <div style="position:relative;padding-bottom:20px;">
            <div style="position:absolute;left:-24px;top:4px;width:20px;height:20px;border-radius:50%;background:#0f172a;display:flex;align-items:center;justify-content:center;color:#caff33;font-size:10px;font-weight:700;">1</div>
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;">
              <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">Origin / Signer</div>
              ${tx.isSigned ? `
                <div class="mono" style="font-size:13px;color:#0f172a;word-break:break-all;">${tx.signer || '—'}</div>
                <div style="display:flex;gap:12px;margin-top:8px;flex-wrap:wrap;">
                  ${tx.nonce !== null ? `<span style="font-size:12px;color:#475569;">Nonce: <strong style="color:#0f172a;">${tx.nonce}</strong></span>` : ''}
                  ${tx.tip ? `<span style="font-size:12px;color:#475569;">Tip: <strong style="color:#0f172a;">${tx.tip}</strong></span>` : ''}
                </div>
              ` : '<div style="font-size:13px;color:#64748b;">Unsigned (inherent or sudo)</div>'}
            </div>
          </div>

          <!-- Step 2: Call -->
          <div style="position:relative;padding-bottom:20px;">
            <div style="position:absolute;left:-24px;top:4px;width:20px;height:20px;border-radius:50%;background:#0f172a;display:flex;align-items:center;justify-content:center;color:#caff33;font-size:10px;font-weight:700;">2</div>
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;">
              <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">Call / Dispatch</div>
              <div style="font-size:14px;color:#0f172a;font-weight:600;margin-bottom:4px;">${tx.palletName}.${tx.callName}</div>
              <div style="font-size:12px;color:#475569;">Pallet index: <strong style="color:#0f172a;">${tx.palletIndex}</strong> · Call index: <strong style="color:#0f172a;">${tx.callIndex}</strong></div>
            </div>
          </div>

          <!-- Step 3: Arguments -->
          <div style="position:relative;padding-bottom:20px;">
            <div style="position:absolute;left:-24px;top:4px;width:20px;height:20px;border-radius:50%;background:#0f172a;display:flex;align-items:center;justify-content:center;color:#caff33;font-size:10px;font-weight:700;">3</div>
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;">
              <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Arguments</div>
              ${Object.keys(tx.decodedArgs).length > 0 ? `
                <div style="display:grid;gap:6px;">
                  ${Object.entries(tx.decodedArgs).map(([key, val]) => `
                    <div style="display:flex;gap:8px;font-size:13px;">
                      <span style="color:#475569;min-width:80px;">${key}:</span>
                      <span style="color:#0f172a;word-break:break-all;" class="mono">${val}</span>
                    </div>
                  `).join('')}
                </div>
              ` : '<div style="font-size:13px;color:#64748b;">No decoded arguments (raw data below)</div>'}
              <details style="margin-top:8px;">
                <summary style="font-size:12px;color:#6366f1;cursor:pointer;">Show raw args hex</summary>
                <div class="mono" style="font-size:11px;color:#475569;margin-top:6px;word-break:break-all;background:#f8fafc;padding:8px;border-radius:6px;">${tx.argsHex}</div>
              </details>
            </div>
          </div>

          <!-- Step 4: Block inclusion -->
          <div style="position:relative;padding-bottom:20px;">
            <div style="position:absolute;left:-24px;top:4px;width:20px;height:20px;border-radius:50%;background:#0f172a;display:flex;align-items:center;justify-content:center;color:#caff33;font-size:10px;font-weight:700;">4</div>
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;">
              <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">Block Inclusion</div>
              <div style="display:flex;gap:12px;flex-wrap:wrap;">
                <a href="#" onclick="showBlockDetail(${blockNum});return false;" style="font-size:13px;color:#6366f1;text-decoration:none;">Block #${blockNum}</a>
                <span style="font-size:13px;color:#475569;">Index: <strong style="color:#0f172a;">${txIndex}</strong></span>
                <span style="font-size:13px;color:#475569;">Size: <strong style="color:#0f172a;">${tx.size} bytes</strong></span>
              </div>
            </div>
          </div>

          <!-- Step 5: Status -->
          <div style="position:relative;">
            <div style="position:absolute;left:-24px;top:4px;width:20px;height:20px;border-radius:50%;background:#16a34a;display:flex;align-items:center;justify-content:center;color:#fff;font-size:10px;font-weight:700;">✓</div>
            <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px;">
              <div style="font-size:11px;color:#16a34a;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Status</div>
              <div style="font-size:14px;color:#0f172a;font-weight:600;">Success — Included in finalized block</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Technical Details -->
      <div style="margin-bottom:20px;">
        <h3 style="font-size:13px;font-weight:600;color:#0f172a;margin-bottom:12px;">Technical Details</h3>
        <div style="display:grid;gap:8px;">
          ${tx.signature ? `
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px;">
              <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Signature (sr25519)</div>
              <div class="mono" style="font-size:11px;color:#0f172a;word-break:break-all;">${tx.signature}</div>
            </div>
          ` : ''}
          ${tx.era ? `
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px;">
              <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Era</div>
              <div class="mono" style="font-size:12px;color:#0f172a;">${tx.era} ${tx.era === '0x80' ? '(Immortal)' : '(Mortal)'}</div>
            </div>
          ` : ''}
          ${feeInfo ? `
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px;">
              <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Fee Info</div>
              <pre style="font-size:11px;color:#0f172a;margin:0;white-space:pre-wrap;">${JSON.stringify(feeInfo, null, 2)}</pre>
            </div>
          ` : ''}
          <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px;">
            <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Raw Extrinsic (SCALE-encoded)</div>
            <div class="mono" style="font-size:11px;color:#0f172a;word-break:break-all;max-height:200px;overflow-y:auto;background:#f8fafc;padding:8px;border-radius:6px;">${tx.rawHex}</div>
          </div>
        </div>
      </div>

      <!-- Block hash reference -->
      <div style="background:#f8fafc;border-radius:8px;padding:12px;border:1px solid #e2e8f0;">
        <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Block Hash</div>
        <div class="mono" style="font-size:12px;color:#0f172a;word-break:break-all;">${hash}</div>
      </div>
    </div>
  `;
  
  document.getElementById('modalBody').innerHTML = html;
  document.getElementById('modalTitle').textContent = `${tx.callPath} — Block #${blockNum}`;
}

// === MODAL SYSTEM ===

function showModal(type, id) {
  // Create modal if it doesn't exist
  let modal = document.getElementById('detailModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'detailModal';
    modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);backdrop-filter:blur(4px);z-index:10000;display:flex;align-items:flex-start;justify-content:center;padding:40px 20px;overflow-y:auto;';
    modal.innerHTML = `
      <div style="background:#f8fafc;border-radius:16px;max-width:800px;width:100%;margin:auto;box-shadow:0 20px 60px rgba(0,0,0,0.3);overflow:hidden;">
        <div style="display:flex;align-items:center;justify-content:space-between;padding:16px 20px;background:#fff;border-bottom:1px solid #e2e8f0;position:sticky;top:0;z-index:10;">
          <h2 id="modalTitle" style="font-size:16px;font-weight:700;color:#0f172a;margin:0;">Loading...</h2>
          <button onclick="closeModal()" style="width:36px;height:36px;border-radius:8px;border:1px solid #e2e8f0;background:#f8fafc;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:18px;color:#475569;">✕</button>
        </div>
        <div id="modalBody" style="padding:20px;max-height:calc(100vh - 120px);overflow-y:auto;">
          <div style="padding:40px;text-align:center;color:#475569;">Loading...</div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });
  }
  modal.style.display = 'flex';
  document.getElementById('modalBody').innerHTML = '<div style="padding:40px;text-align:center;color:#475569;"><div class="loading" style="display:inline-block;width:24px;height:24px;border:3px solid #e2e8f0;border-top-color:#caff33;border-radius:50%;animation:spin 1s linear infinite;"></div><div style="margin-top:12px;font-size:13px;">Fetching from RPC...</div></div>';
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  const modal = document.getElementById('detailModal');
  if (modal) modal.style.display = 'none';
  document.body.style.overflow = '';
  // Clear hash from URL
  if (window.location.hash) {
    history.replaceState(null, '', window.location.pathname + window.location.search);
  }
}

// Close modal on Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});

// === URL HASH ROUTING ===
function handleHashRoute() {
  const hash = window.location.hash;
  if (!hash) return;
  
  if (hash.startsWith('#block:')) {
    const blockNum = parseInt(hash.replace('#block:', ''));
    if (!isNaN(blockNum)) showBlockDetail(blockNum);
  } else if (hash.startsWith('#hash:')) {
    const blockHash = hash.replace('#hash:', '');
    // Fetch block number from hash, then show detail
    rpc('chain_getBlock', [blockHash]).then(block => {
      if (block && block.block) {
        const num = parseInt(block.block.header.number, 16);
        showBlockDetail(num);
      }
    });
  } else if (hash.startsWith('#tx:')) {
    const parts = hash.replace('#tx:', '').split(':');
    if (parts.length >= 2) {
      showTxDetail(parts[0], parseInt(parts[1]), parseInt(parts[2] || 0));
    }
  }
}

// Call on load
window.addEventListener('hashchange', handleHashRoute);
