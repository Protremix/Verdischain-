#!/usr/bin/env python3
"""Patch wallet/index.html loadHistory to decode hex extrinsics properly."""

with open('/var/www/verdiscan/wallet/index.html', 'r') as f:
    content = f.read()

old_func = '''async function loadHistory() {
  const wallet = loadWallet();
  if (!wallet) return;
  const container = document.getElementById('txHistory');
  if (!container) return;
  container.textContent = 'Loading transactions...';

  try {
    const header = await rpcCall('chain_getHeader', []);
    if (!header) { container.textContent = 'Cannot connect to node.'; return; }
    const currentBlock = parseInt(header.number, 16);
    const myAddr = wallet.address;
    const txs = [];

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

        if (callHex && callHex.length > 10) {
          const callBytes = callHex.replace('0x', '');

          // Detect Balances.transfer_allow_death (pallet + call + dest + value)
          if (callBytes.length >= 72) {
            const destPrefix = callBytes.slice(4, 6);
            if (destPrefix === '00') {
              const destHex = callBytes.slice(6, 70);
              try {
                const destBytes = new Uint8Array(32);
                for (let j = 0; j < 32; j++) {
                  destBytes[j] = parseInt(destHex.slice(j*2, j*2+2), 16);
                }
                const destAddr = ss58Encode(destBytes, 909);

                let value = '';
                try {
                  const valueBytes = callBytes.slice(70);
                  const firstByte = parseInt(valueBytes.slice(0, 2), 16);
                  const mode = firstByte & 0x03;
                  if (mode === 0) {
                    value = (firstByte >> 2).toString();
                  } else if (mode === 1) {
                    const secondByte = parseInt(valueBytes.slice(2, 4), 16);
                    value = ((firstByte >> 2) + secondByte * 64).toString();
                  } else if (mode === 2) {
                    let v = firstByte >> 2;
                    for (let b = 1; b < 4; b++) {
                      v += parseInt(valueBytes.slice(b*2, b*2+2), 16) * Math.pow(256, b) / 4;
                    }
                    value = Math.floor(v).toString();
                  }
                  if (value && value !== '') {
                    const vrdx = parseInt(value) / 10**9;
                    value = vrdx.toFixed(4) + ' VRDX';
                  }
                } catch {}

                const isSent = signer === myAddr;
                const isReceived = destAddr === myAddr;

                if (isSent || isReceived) {
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

          // Detect system.remark
          if (callHex.startsWith('0x0001') && signer === myAddr) {'''

new_func = '''async function loadHistory() {
  const wallet = loadWallet();
  if (!wallet) return;
  const container = document.getElementById('txHistory');
  if (!container) return;
  container.textContent = 'Loading transactions...';

  try {
    const header = await rpcCall('chain_getHeader', []);
    if (!header) { container.textContent = 'Cannot connect to node.'; return; }
    const currentBlock = parseInt(header.number, 16);
    const myAddr = wallet.address;
    const txs = [];

    // Helper: convert hex string to byte array
    function hexToBytes(hex) {
      hex = hex.replace('0x', '');
      const bytes = [];
      for (let i = 0; i < hex.length; i += 2) {
        bytes.push(parseInt(hex.substr(i, 2), 16));
      }
      return bytes;
    }

    // Helper: read SCALE compact integer
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
        // mode 3: big integer, 6-byte prefix
        if (offset + 5 >= bytes.length) return { value: 0, nextOffset: offset + 5 };
        let v = 0;
        const nBytes = (first >> 2) + 4;
        for (let b = 0; b < nBytes && offset + 1 + b < bytes.length; b++) {
          v += bytes[offset + 1 + b] * Math.pow(256, b);
        }
        return { value: v, nextOffset: offset + 1 + nBytes };
      }
    }

    // Decode a hex extrinsic: extract signer, call index, and for Balances.transfer_allow_death, dest + value
    function decodeExtrinsicTx(hexStr, blockNum, blockHash) {
      const bytes = hexToBytes(hexStr);
      if (bytes.length < 4) return null;

      // Skip compact length prefix (1-2 bytes)
      let offset = 0;
      const lenResult = readCompact(bytes, offset);
      offset = lenResult.nextOffset;

      // Version byte
      if (offset >= bytes.length) return null;
      const versionByte = bytes[offset];
      const isSigned = (versionByte & 0x80) !== 0;

      if (!isSigned) {
        // Unsigned/inherent (e.g., timestamp) — skip
        return null;
      }

      offset++; // skip version byte

      // Signature: 1 byte type + 64 bytes (sr25519) or 65 bytes (ecdsa)
      if (offset >= bytes.length) return null;
      const sigType = bytes[offset];
      const sigLen = (sigType === 2) ? 65 : 64;
      offset += 1 + sigLen; // skip sig type + signature

      // Signer: AccountId32 (1 byte enum + 32 bytes)
      if (offset + 33 > bytes.length) return null;
      offset += 1; // skip enum prefix (0 = AccountId32)
      let signerBytes = [];
      for (let s = offset; s < offset + 32; s++) signerBytes.push(bytes[s]);
      offset += 32;

      // Encode signer as SS58
      let signer = '';
      try {
        signer = ss58Encode(new Uint8Array(signerBytes), 909);
      } catch(e) {
        signer = '0x' + signerBytes.map(b => ('0' + b.toString(16)).slice(-2)).join('');
      }

      // Era: 0x00 = immortal (1 byte), else mortal (2 bytes)
      if (offset >= bytes.length) return null;
      if (bytes[offset] === 0) {
        offset += 1;
      } else {
        offset += 2;
      }

      // Nonce (compact)
      const nonceResult = readCompact(bytes, offset);
      offset = nonceResult.nextOffset;

      // Tip (compact)
      const tipResult = readCompact(bytes, offset);
      offset = tipResult.nextOffset;

      // Call index: pallet index + function index
      if (offset + 1 >= bytes.length) return null;
      const palletIdx = bytes[offset];
      const funcIdx = bytes[offset + 1];
      offset += 2;

      // Balances pallet = 4
      // transfer_allow_death = 0 (in current Substrate versions)
      // transfer_keep_alive = 3
      if (palletIdx === 4 && (funcIdx === 0 || funcIdx === 3)) {
        // Dest: MultiAddress enum (0 = AccountId32)
        if (offset >= bytes.length) return null;
        const destType = bytes[offset];
        offset += 1;

        if (destType === 0 && offset + 32 <= bytes.length) {
          // AccountId32
          let destBytes = [];
          for (let d = offset; d < offset + 32; d++) destBytes.push(bytes[d]);
          offset += 32;

          // Value (compact-encoded u128)
          const valueResult = readCompact(bytes, offset);
          const valueRaw = valueResult.value;

          let destAddr = '';
          try {
            destAddr = ss58Encode(new Uint8Array(destBytes), 909);
          } catch(e) {
            destAddr = '0x' + destBytes.map(b => ('0' + b.toString(16)).slice(-2)).join('');
          }

          const vrdx = valueRaw / 1e9;
          const valueStr = vrdx.toFixed(4) + ' VRDX';

          return {
            signer: signer,
            dest: destAddr,
            value: valueStr,
            method: funcIdx === 0 ? 'Transfer' : 'TransferKeepAlive',
            block: blockNum,
            blockHash: blockHash,
            hash: '0x' + bytes.slice(0, 8).map(b => ('0' + b.toString(16)).slice(-2)).join('')
          };
        }
      }

      // system.remark (pallet 0, func 0)
      if (palletIdx === 0 && funcIdx === 1) {
        return {
          signer: signer,
          dest: '',
          value: '',
          method: 'System.remark',
          block: blockNum,
          blockHash: blockHash,
          hash: '0x' + bytes.slice(0, 8).map(b => ('0' + b.toString(16)).slice(-2)).join('')
        };
      }

      // Other signed extrinsics — still record if from our address
      return {
        signer: signer,
        dest: '',
        value: '',
        method: 'pallet_' + palletIdx + '_call_' + funcIdx,
        block: blockNum,
        blockHash: blockHash,
        hash: '0x' + bytes.slice(0, 8).map(b => ('0' + b.toString(16)).slice(-2)).join('')
      };
    }

    for (let i = 0; i < 200 && currentBlock - i > 0; i++) {
      if (txs.length >= 30) break;
      const bn = currentBlock - i;
      const blockHash = await rpcCall('chain_getBlockHash', [bn]);
      if (!blockHash) continue;
      const blockData = await rpcCall('chain_getBlock', [blockHash]);
      if (!blockData || !blockData.block || !blockData.block.extrinsics) continue;

      for (const ext of blockData.block.extrinsics) {
        // Extrinsics come as hex strings from RPC — decode them
        const extHex = typeof ext === 'string' ? ext : '0x' + ext.map(b => ('0' + b.toString(16)).slice(-2)).join('');
        const decoded = decodeExtrinsicTx(extHex, bn, blockHash);
        if (!decoded) continue;

        const isSent = decoded.signer === myAddr;
        const isReceived = decoded.dest === myAddr;

        if (isSent || isReceived) {
          const existing = txs.find(t => t.block === bn && t.signer === decoded.signer);
          if (!existing) {
            txs.push({
              hash: decoded.hash,
              block: bn,
              type: isSent ? 'sent' : 'received',
              signer: decoded.signer,
              dest: decoded.dest,
              method: decoded.method,
              value: decoded.value
            });
          }
        }
      }
    }'''

if old_func not in content:
    print("PATCH FAILED: old function pattern not found")
    # Let's find where the mismatch is
    import difflib
    # Find the approximate location
    start_marker = 'async function loadHistory() {'
    end_marker = 'txs.sort((a, b) => b.block - a.block);'
    si = content.find(start_marker)
    ei = content.find(end_marker)
    if si >= 0 and ei >= 0:
        print(f"Found loadHistory at char {si}, sort at char {ei}")
        # Show the first 200 chars of the old function in the file
        print("File content starts:")
        print(repr(content[si:si+200]))
        print("Expected content starts:")
        print(repr(old_func[:200]))
    else:
        print(f"start marker at {si}, end marker at {ei}")
else:
    content = content.replace(old_func, new_func)
    with open('/var/www/verdiscan/wallet/index.html', 'w') as f:
        f.write(content)
    print("PATCH APPLIED SUCCESSFULLY")
