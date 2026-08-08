import subprocess

result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/explorer/index.html"],
    capture_output=True, text=True
)
content = result.stdout
lines = content.split('\n')

# Find the scanBlockForTransfers function and replace it with a SCALE-decoding version
start_idx = None
end_idx = None
brace_count = 0
for i, line in enumerate(lines):
    if line.strip() == 'async function scanBlockForTransfers(blockNum) {':
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

print(f"Found scanBlockForTransfers at lines {start_idx+1}-{end_idx+1}")

new_func = '''// SCALE compact decoder
function decodeCompact(bytes, offset) {
  var b0 = bytes[offset];
  if ((b0 & 0x03) === 0) return { value: b0 >> 2, next: offset + 1 };
  if ((b0 & 0x03) === 1) return { value: (b0 >> 2) + (bytes[offset+1] << 6), next: offset + 2 };
  if ((b0 & 0x03) === 2) {
    var val = (b0 >> 2) + (bytes[offset+1] << 6) + (bytes[offset+2] << 14) + (bytes[offset+3] << 22);
    return { value: val, next: offset + 4 };
  }
  var nBytes = b0 >> 2;
  var val = 0;
  for (var i = 0; i < nBytes; i++) val += bytes[offset + 1 + i] << (8 * i);
  return { value: val, next: offset + 1 + nBytes };
}

// Convert 32-byte AccountId to SS58 address (prefix 42)
function accountIdToSS58(accountId) {
  // Simple SS58 encoding: prefix + accountId + checksum
  var prefix = 42;
  var data = [prefix].concat(accountId);
  // Simple checksum: first 2 bytes of blake2b256(data) — use a simplified approach
  // For display, just show hex if we can't compute blake2b
  var hex = accountId.map(function(b) { return ('0' + b.toString(16)).slice(-2); }).join('');
  return '0x' + hex.slice(0, 8) + '...' + hex.slice(-8);
}

// Decode extrinsic from byte array
function decodeExtrinsic(extBytes) {
  if (!extBytes || !extBytes.length) return null;
  var offset = 0;

  // Parse compact length
  var lenResult = decodeCompact(extBytes, offset);
  offset = lenResult.next;

  // Version byte
  var versionByte = extBytes[offset];
  var isSigned = (versionByte & 0x80) !== 0;
  var version = versionByte & 0x7f;
  offset++;

  var signer = null;

  if (isSigned) {
    // MultiAddress enum
    var addrType = extBytes[offset];
    offset++;
    if (addrType === 0) {
      // AccountId32
      signer = extBytes.slice(offset, offset + 32);
      offset += 32;
    } else {
      // Other address types — skip what we can
      if (addrType === 1) { offset += 4; } // AccountIndex
      else if (addrType === 2) { offset += 32; } // Account20
      else if (addrType === 3) { offset += 32; } // Account32 (same as Id)
      else { return { signer: null, pallet: -1, call: -1, method: 'unknown' }; }
    }

    // Signature (64 bytes for Sr25519, 65 for Ed25519) — check signature type
    // MultiSignature enum: 0 = Ed25519(64), 1 = Sr25519(64), 2 = Ecdsa(65)
    var sigType = extBytes[offset];
    offset++;
    if (sigType === 0 || sigType === 1) offset += 64;
    else if (sigType === 2) offset += 65;
    else offset += 64; // assume 64

    // Signed extras: era, nonce, tip
    // Era: 1 byte for immortal (0x00), or 2 bytes for mortal
    var eraByte = extBytes[offset];
    if (eraByte === 0) offset += 1; // immortal era
    else offset += 2; // mortal era

    // Nonce (compact-encoded u32)
    var nonceResult = decodeCompact(extBytes, offset);
    var nonce = nonceResult.value;
    offset = nonceResult.next;

    // Tip (compact-encoded u128 — might be compact)
    var tipResult = decodeCompact(extBytes, offset);
    offset = tipResult.next;
  }

  // Call data: pallet_index + call_index + args
  if (offset + 1 >= extBytes.length) return { signer: signer, pallet: -1, call: -1, method: 'unknown', nonce: nonce };
  var palletIndex = extBytes[offset];
  var callIndex = extBytes[offset + 1];
  offset += 2;

  var result = { signer: signer, pallet: palletIndex, call: callIndex, nonce: nonce || 0, args: extBytes.slice(offset), method: '' };

  // Known pallet + call mappings
  var palletNames = {0:'system',1:'timestamp',2:'babe',3:'grandpa',4:'balances',5:'tx_payment',6:'sudo',7:'session',8:'scheduler',9:'preimage',
    20:'contracts',30:'dpos',31:'ammDex',32:'eco',33:'tokenomics',34:'vesting',35:'storage',36:'utility',
    38:'multisig',39:'proxy',41:'nfts',42:'authorship',43:'council',44:'democracy',45:'historical',46:'offences',47:'treasury',
    50:'fungible_tokens',51:'poh',52:'gulf_stream',53:'turbine',54:'zk_compression',55:'alt',56:'sealevel',57:'ibc'};
  var palletName = palletNames[palletIndex] || ('pallet_' + palletIndex);

  var callNames = {
    'system': {0:'remark', 1:'set_heap_pages', 2:'set_code', 3:'set_code_without_checks'},
    'timestamp': {0:'set'},
    'balances': {0:'transfer', 1:'set_balance', 2:'force_transfer', 3:'transfer_keep_alive', 4:'transfer_all', 5:'force_unreserve', 6:'upgrade_pallets', 7:'transfer_allow_death'},
    'dpos': {0:'join_candidates', 1:'leave_candidates', 2:'vote', 3:'update_validator_name', 4:'set_validator_name'},
    'ammDex': {0:'add_liquidity', 1:'remove_liquidity', 2:'swap', 3:'create_pool'},
    'eco': {0:'mint_carbon_credit', 1:'log_reforestation', 2:'update_green_score'},
    'tokenomics': {0:'mint', 1:'burn'},
    'vesting': {0:'vest', 1:'vest_other'},
    'utility': {0:'batch', 1:'batch_all', 2:'dispatch_as'},
    'fungible_tokens': {0:'transfer', 1:'mint', 2:'burn'},
    'session': {0:'set_keys', 1:'purge_keys'},
    'sudo': {0:'sudo', 1:'sudo_as'},
    'treasury': {0:'propose_spend', 1:'reject_proposal', 2:'approve_proposal'},
    'democracy': {0:'propose', 1:'second', 2:'vote'},
    'council': {0:'propose', 1:'vote', 2:'close'},
    'multisig': {0:'as_multi', 1:'approve_as_multi'},
    'proxy': {0:'proxy', 1:'add_proxy', 2:'remove_proxy'},
    'nfts': {0:'mint', 1:'transfer', 2:'burn'},
    'contracts': {0:'call', 1:'instantiate_with_code', 2:'instantiate'},
  };

  var callName = (callNames[palletName] && callNames[palletName][callIndex]) || ('call_' + callIndex);
  result.method = palletName + '.' + callName;

  // Decode transfer args for balances.transfer (pallet 4, call 0)
  if (palletIndex === 4 && (callIndex === 0 || callIndex === 3 || callIndex === 7)) {
    // dest: MultiAddress (enum + 32 bytes)
    var destType = extBytes[offset];
    offset++;
    if (destType === 0) {
      result.dest = extBytes.slice(offset, offset + 32);
      offset += 32;
      // value: compact-encoded u128
      var valResult = decodeCompact(extBytes, offset);
      result.value = valResult.value;
    }
  }

  // Decode remark args for system.remark (pallet 0, call 0)
  if (palletIndex === 0 && callIndex === 0) {
    // remark: Vec<u8> — compact length + bytes
    var remarkLen = decodeCompact(extBytes, offset);
    result.remark = extBytes.slice(remarkLen.next, remarkLen.next + Math.min(remarkLen.value, 100));
  }

  // Decode transfer for fungible_tokens.transfer (pallet 50, call 0)
  if (palletIndex === 50 && callIndex === 0) {
    // token_id (compact) + dest (MultiAddress) + value (compact)
    var tokenId = decodeCompact(extBytes, offset);
    offset = tokenId.next;
    var destType2 = extBytes[offset];
    offset++;
    if (destType2 === 0) {
      result.dest = extBytes.slice(offset, offset + 32);
      offset += 32;
      var valResult2 = decodeCompact(extBytes, offset);
      result.value = valResult2.value;
    }
  }

  // Decode swap for ammDex.swap (pallet 31, call 2)
  if (palletIndex === 31 && callIndex === 2) {
    result.isSwap = true;
  }

  // Decode DEX operations
  if (palletIndex === 31) {
    result.isDexOp = true;
  }

  return result;
}

async function scanBlockForTransfers(blockNum) {
  try {
    var hash = await rpc('chain_getBlockHash', [blockNum]);
    if (!hash) return [];
    var block = await rpc('chain_getBlock', [hash]);
    if (!block || !block.block || !block.block.extrinsics) return [];
    var results = [];
    for (var i = 0; i < block.block.extrinsics.length; i++) {
      var extBytes = block.block.extrinsics[i];
      if (typeof extBytes === 'string') {
        // Hex string format — convert to byte array
        var hex = extBytes.replace(/^0x/, '');
        extBytes = [];
        for (var j = 0; j < hex.length; j += 2) extBytes.push(parseInt(hex.substr(j, 2), 16));
      }
      var decoded = decodeExtrinsic(extBytes);
      if (!decoded) continue;

      var signerDisplay = decoded.signer ? accountIdToSS58(decoded.signer) : '—';

      // Skip timestamp (pallet 1)
      if (decoded.pallet === 1) continue;

      var entry = {
        hash: hash,
        block: blockNum,
        from: signerDisplay,
        to: '—',
        amount: 0,
        type: decoded.method
      };

      // Balance transfers
      if (decoded.pallet === 4 && decoded.dest) {
        entry.to = accountIdToSS58(decoded.dest);
        entry.amount = decoded.value || 0;
      }

      // Token transfers (fungible_tokens)
      if (decoded.pallet === 50 && decoded.dest) {
        entry.to = accountIdToSS58(decoded.dest);
        entry.amount = decoded.value || 0;
        entry.type = 'tokens.transfer';
      }

      // System remarks
      if (decoded.pallet === 0 && decoded.call === 0) {
        entry.type = 'system.remark';
        if (decoded.remark && decoded.remark.length > 0) {
          var remarkText = '';
          for (var k = 0; k < Math.min(decoded.remark.length, 20); k++) {
            var ch = decoded.remark[k];
            remarkText += (ch >= 32 && ch < 127) ? String.fromCharCode(ch) : '.';
          }
          entry.to = 'Memo: ' + remarkText;
        }
      }

      // DEX operations
      if (decoded.isDexOp) {
        entry.to = 'AMM Pool';
        if (decoded.isSwap) entry.type = 'amm.swap';
      }

      // Validator operations (Dpos)
      if (decoded.pallet === 30) {
        entry.to = 'DPoS';
      }

      // Eco operations
      if (decoded.pallet === 32) {
        entry.to = 'Eco';
      }

      results.push(entry);
    }
    return results;
  } catch(e) { console.error('scanBlock error:', e); return []; }
}'''

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
