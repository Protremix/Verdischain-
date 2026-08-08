#!/usr/bin/env python3
"""Fix Portfolio tab: address comparison, green validators format, SS58 decoding."""

EXP_PATH = "/var/www/verdiscan/explorer/index.html"

with open(EXP_PATH, "r") as f:
    html = f.read()

# 1. Replace the ss58ToHex function with a proper base58 decoder
old_ss58_func = '''function ss58ToHex(ss58) {
  // Simple SS58 to hex conversion for comparison
  // This is a basic implementation - works for standard AccountId32
  try {
    if (ss58.startsWith("0x") && ss58.length === 66) return ss58;
    // Base58 decode is complex in pure JS - use the address as-is for comparison
    // The RPC returns hex addresses, so we compare case-insensitively
    return null;
  } catch(e) { return null; }
}'''

new_ss58_func = '''function ss58ToHex(ss58) {
  try {
    if (ss58.startsWith("0x") && ss58.length === 66) return ss58.toLowerCase();
    if (!ss58 || ss58.length < 5) return null;
    // Base58 decode (no hashing needed for decode)
    var ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
    var num = BigInt(0);
    for (var i = 0; i < ss58.length; i++) {
      var idx = ALPHABET.indexOf(ss58[i]);
      if (idx === -1) return null;
      num = num * 58n + BigInt(idx);
    }
    var bytes = [];
    while (num > 0n) { bytes.push(Number(num & 255n)); num = num >> 8n; }
    bytes = bytes.reverse();
    // Leading '1's = leading 0x00 bytes
    for (var i = 0; i < ss58.length && ss58[i] === "1"; i++) bytes.unshift(0);
    // SS58 format: [version(1-2 bytes)] + [payload(32 bytes)] + [checksum(2 bytes)]
    var versionLen = 1;
    if (bytes.length > 0 && (bytes[0] & 0xC0) === 0xC0) versionLen = 2;
    var payloadStart = versionLen;
    var payloadEnd = payloadStart + 32;
    if (bytes.length < payloadEnd + 2) return null;
    var hex = "";
    for (var i = payloadStart; i < payloadEnd; i++) hex += ("0" + bytes[i].toString(16)).slice(-2);
    return "0x" + hex;
  } catch(e) { return null; }
}'''

if old_ss58_func in html:
    html = html.replace(old_ss58_func, new_ss58_func)
    print("ss58ToHex replaced with base58 decoder")
else:
    print("WARNING: ss58ToHex function not found")

# 2. Fix the staking validator check to use direct SS58 comparison
old_validator_check = '''var isValidator = allValidators && allValidators.some(function(v) {
      return v.toLowerCase() === (hexAddr || "").toLowerCase() || v === addr;
    });'''
new_validator_check = '''var isValidator = allValidators && allValidators.some(function(v) {
      return v === addr || (hexAddr && v.toLowerCase() === hexAddr.toLowerCase());
    });'''

if old_validator_check in html:
    html = html.replace(old_validator_check, new_validator_check)
    print("Validator check fixed")
else:
    print("WARNING: validator check not found")

# 3. Fix the active validator check similarly
old_active_check = '''var isActive = activeValidators && activeValidators.some(function(v) {
          return v.toLowerCase() === (hexAddr || "").toLowerCase() || v === addr;
        });'''
new_active_check = '''var isActive = activeValidators && activeValidators.some(function(v) {
          return v === addr || (hexAddr && v.toLowerCase() === hexAddr.toLowerCase());
        });'''

if old_active_check in html:
    html = html.replace(old_active_check, new_active_check)
    print("Active validator check fixed")

# 4. Fix the green validator check - getAllGreenValidators returns [[address, score], ...]
old_green_check = '''var isGreen = allGreen && allGreen.some(function(v) {
      return v.toLowerCase() === (hexAddr || "").toLowerCase() || v === addr;
    });'''
new_green_check = '''var isGreen = allGreen && allGreen.some(function(v) {
      var gAddr = Array.isArray(v) ? v[0] : v;
      return gAddr === addr || (hexAddr && gAddr.toLowerCase() === hexAddr.toLowerCase());
    });'''

if old_green_check in html:
    html = html.replace(old_green_check, new_green_check)
    print("Green validator check fixed")

# 5. Also fix the transaction history signer comparison
# The signer is extracted as "0x" + hex, and we compare with ss58ToHex(addr)
# This should now work with the new ss58ToHex function
# But let's also check if the comparison is using the right variable
old_signer_check = '''if (hexAddr && signerHex.toLowerCase() === hexAddr.replace("0x","").toLowerCase()) {'''
new_signer_check = '''if (hexAddr && ("0x" + signerHex).toLowerCase() === hexAddr.toLowerCase()) {'''

if old_signer_check in html:
    html = html.replace(old_signer_check, new_signer_check)
    print("Signer comparison fixed")

with open(EXP_PATH, "w") as f:
    f.write(html)
print(f"All fixes applied ({len(html)} bytes)")
