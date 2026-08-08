#!/usr/bin/env python3
"""Fix wallet-app.js and explorer/index.html to use state_getStorage instead of system_account RPC"""

import re

# ============= FIX wallet-app.js =============
with open('wallet-app.js', 'r') as f:
    wallet_js = f.read()

# 1. Add getAccountInfo function after rpcCall function
get_account_fn = """
    // --- Account Info via state_getStorage (system_account RPC not available) ---
    const SYSTEM_ACCOUNT_PREFIX = '0x26aa394eea5630e07c48ae0c9558cef7b99d880ec681799c0cf30e8886371da9';
    async function getAccountInfo(accountIdHex) {
      try {
        var acctHex = accountIdHex.startsWith('0x') ? accountIdHex.slice(2) : accountIdHex;
        var acctBytes = new Uint8Array(acctHex.match(/.{2}/g).map(function(b) { return parseInt(b, 16); }));
        var blakeHash = window.blake2b(acctBytes, { dkLen: 16 });
        var blakeHex = Array.from(blakeHash).map(function(b) { return ('0' + b.toString(16)).slice(-2); }).join('');
        var storageKey = SYSTEM_ACCOUNT_PREFIX + blakeHex + acctHex;
        var result = await rpcCall('state_getStorage', [storageKey]);
        if (!result || result === '0x' || result.length < 10) return null;
        var hex = result.slice(2);
        var bytes = new Uint8Array(hex.match(/.{2}/g).map(function(b) { return parseInt(b, 16); }));
        var nonce = bytes[0] | (bytes[1] << 8) | (bytes[2] << 16) | (bytes[3] << 24);
        function decodeU128LE(offset) {
          var val = 0n;
          for (var i = 0; i < 16; i++) { val += BigInt(bytes[offset + i]) << (8n * BigInt(i)); }
          return val;
        }
        var free = decodeU128LE(16);
        var reserved = decodeU128LE(32);
        return { nonce: nonce, data: { free: free.toString(), reserved: reserved.toString() } };
      } catch(e) {
        console.warn('getAccountInfo error:', e);
        return null;
      }
    }

    // --- Tab Switching ---"""

wallet_js = wallet_js.replace("    // --- Tab Switching ---", get_account_fn, 1)

# 2. Replace system_account call with getAccountInfo
wallet_js = wallet_js.replace(
    "var accountInfo = await rpcCall('system_account', [accountIdHex]);",
    "var accountInfo = await getAccountInfo(accountIdHex);"
)

# 3. Fix balance parsing: use BigInt and 1e9 divisor (VRDX has 9 decimals, not 18)
old_balance = """          if (accountInfo && accountInfo.data) {
            var freeStr = accountInfo.data.free || '0';
            var free = typeof freeStr === 'string' ? parseInt(freeStr, freeStr.startsWith('0x') ? 16 : 10) : freeStr;
            walletState.balanceVRDX = free / 1e18;"""

new_balance = """          if (accountInfo && accountInfo.data) {
            var freeStr = accountInfo.data.free || '0';
            var freeBigInt = BigInt(freeStr);
            walletState.balanceVRDX = Number(freeBigInt / BigInt(1000000000)) + Number(freeBigInt % BigInt(1000000000)) / 1000000000;"""

wallet_js = wallet_js.replace(old_balance, new_balance)

with open('wallet-app-fixed.js', 'w') as f:
    f.write(wallet_js)

print(f"wallet-app.js: {len(wallet_js)} chars -> wallet-app-fixed.js")

# ============= FIX explorer/index.html =============
with open('explorer-index.html', 'r') as f:
    explorer_html = f.read()

# 1. Add module script for blake2b and base58 before the main script
module_script = """<script type="module">
import { blake2b } from 'https://esm.sh/@noble/hashes@1.5.0/blake2b';
import { base58 } from 'https://esm.sh/@scure/base@1.1.5';
window.blake2b = blake2b;
window.base58Decode = base58.decode;
</script>
<script>"""

explorer_html = explorer_html.replace("<script>", module_script, 1)

# 2. Add SS58 decoder and getAccountInfo after the rpc function
# Find the closing of the rpc function and add after it
old_rpc_end = """    return j.result;
  } catch(e) { return null; }
}

// API helper"""

new_rpc_end = """    return j.result;
  } catch(e) { return null; }
}

// SS58 decode: extract 32-byte AccountId from SS58 address
function ss58ToAccountId(ss58) {
  try {
    const d = window.base58Decode(ss58);
    if (d.length === 35) return d.slice(1, 33); // 1-byte prefix
    if (d.length === 36) return d.slice(2, 34); // 2-byte prefix
    return null;
  } catch(e) { return null; }
}

// System::Account storage key prefix (twox_128("System") + twox_128("Account"))
const SYS_ACCT_PREFIX = '0x26aa394eea5630e07c48ae0c9558cef7b99d880ec681799c0cf30e8886371da9';

// Query account info via state_getStorage (replaces missing system_account RPC)
async function getAccountInfo(ss58Address) {
  try {
    const acctBytes = ss58ToAccountId(ss58Address);
    if (!acctBytes) return null;
    const blakeHash = window.blake2b(acctBytes, { dkLen: 16 });
    const blakeHex = Array.from(blakeHash).map(b => ('0' + b.toString(16)).slice(-2)).join('');
    const acctHex = Array.from(acctBytes).map(b => ('0' + b.toString(16)).slice(-2)).join('');
    const storageKey = SYS_ACCT_PREFIX + blakeHex + acctHex;
    const result = await rpc('state_getStorage', [storageKey]);
    if (!result || result === '0x' || result.length < 10) return null;
    const hex = result.slice(2);
    const bytes = new Uint8Array(hex.match(/.{2}/g).map(b => parseInt(b, 16)));
    const nonce = bytes[0] | (bytes[1] << 8) | (bytes[2] << 16) | (bytes[3] << 24);
    function decodeU128LE(offset) {
      let val = 0n;
      for (let i = 0; i < 16; i++) { val += BigInt(bytes[offset + i]) << (8n * BigInt(i)); }
      return val;
    }
    const free = decodeU128LE(16);
    return { nonce, data: { free: free.toString() } };
  } catch(e) { return null; }
}

// API helper"""

explorer_html = explorer_html.replace(old_rpc_end, new_rpc_end, 1)

# 3. Replace system_account call in explorer
old_explorer_call = """      const accRes = await rpc('system_account', [q]);
      if (accRes && accRes.data) {
        balance = (Number(accRes.data.free) / 1e9).toLocaleString('en-US') + ' VRDX';
        if (accRes.nonce !== undefined) nonce = accRes.nonce;
      }"""

new_explorer_call = """      const accRes = await getAccountInfo(q);
      if (accRes && accRes.data) {
        const freeBal = BigInt(accRes.data.free) / BigInt(1000000000);
        balance = Number(freeBal).toLocaleString('en-US') + ' VRDX';
        if (accRes.nonce !== undefined) nonce = accRes.nonce;
      }"""

explorer_html = explorer_html.replace(old_explorer_call, new_explorer_call)

with open('explorer-fixed.html', 'w') as f:
    f.write(explorer_html)

print(f"explorer-index.html: {len(explorer_html)} chars -> explorer-fixed.html")

# Verify replacements
print("\n=== Verification ===")
print(f"wallet-app has 'getAccountInfo': {'getAccountInfo' in wallet_js}")
print(f"wallet-app has 'system_account': {'system_account' in wallet_js}")
print(f"wallet-app has 1e18: {'1e18' in wallet_js}")
print(f"explorer has 'getAccountInfo': {'getAccountInfo' in explorer_html}")
check = "rpc(system_account" not in explorer_html; print(f"explorer has system_account RPC call: {not check}")
print(f"explorer has base58Decode: {'base58Decode' in explorer_html}")
