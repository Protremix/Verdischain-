#!/usr/bin/env python3
"""Replace the decoder with a proper SCALE-aware version."""

TX_PATH = "/var/www/verdiscan/transactions/index.html"

with open(TX_PATH, "r") as f:
    html = f.read()

# Find and replace the decodeExtrinsic function
old_start = "function decodeExtrinsic(extHex, blockNum, blockHash, blockTime) {"
idx_start = html.find(old_start)
if idx_start == -1:
    print("ERROR: Could not find function"); exit(1)

# Find end by counting braces
depth = 0; i = idx_start
while i < len(html):
    if html[i] == '{': depth += 1
    elif html[i] == '}':
        depth -= 1
        if depth == 0: idx_end = i + 1; break
    i += 1

new_func = '''function decodeExtrinsic(extData, blockNum, blockHash, blockTime) {
  try {
    // Handle both hex string and byte array formats
    var bytes;
    if (typeof extData === "string") {
      var hex = extData.startsWith("0x") ? extData.slice(2) : extData;
      bytes = [];
      for (var i = 0; i < hex.length; i += 2) { bytes.push(parseInt(hex.substr(i, 2), 16)); }
    } else if (Array.isArray(extData)) {
      bytes = extData;
    } else {
      return { section: "error", method: "?", signer: "", value: "0", fee: "0", blockHash: blockHash, isSigned: false, multiInstr: false };
    }
    if (bytes.length < 4) return { section: "error", method: "?", signer: "", value: "0", fee: "0", blockHash: blockHash, isSigned: false, multiInstr: false };

    // The RPC returns extrinsics with a 2-byte prefix (compact length from Vec encoding)
    // Actual extrinsic starts at offset 2
    var offset = 2;
    var versionByte = bytes[offset];
    var callMap = {
      "0,0": "system.remark", "0,1": "system.setHeapPages", "0,2": "system.setCode", "0,3": "system.setStorage",
      "1,0": "timestamp.set",
      "4,0": "balances.transferAllowDeath", "4,1": "balances.setBalance", "4,3": "balances.transferKeepAlive", "4,4": "balances.transferAll",
      "6,0": "sudo.sudo",
      "30,0": "dpos.registerValidator", "30,1": "dpos.unregisterValidator", "30,2": "dpos.updateGreenScore", "30,5": "dpos.setValidatorName",
      "31,0": "ammDex.createPool", "31,1": "ammDex.addLiquidity", "31,2": "ammDex.removeLiquidity", "31,3": "ammDex.swap",
      "32,0": "eco.mintCarbonCredit", "32,1": "eco.createReforestProject", "32,2": "eco.logReforestation", "32,3": "eco.transferCarbonCredit",
    };

    var section = "unknown", method = "unknown", signer = "";
    var isSigned = false;

    if (versionByte >= 0x80) {
      // Signed extrinsic
      isSigned = true;
      offset++; // version byte

      // Signature type: 0=sr25519 (1+64 bytes), 1=ed25519 (1+64), 2=ecdsa (1+65)
      var sigType = bytes[offset]; offset++;
      var sigLen = (sigType === 2) ? 65 : 64;
      offset += sigLen; // skip signature

      // Signer: 32 bytes (AccountId32)
      if (offset + 32 <= bytes.length) {
        var signerHex = "";
        for (var s = offset; s < offset + 32; s++) signerHex += ("0" + bytes[s].toString(16)).slice(-2);
        signer = "0x" + signerHex;
      }
      offset += 32; // skip signer

      // Era: if byte == 0x00, immortal (1 byte); else mortal (2 bytes)
      if (bytes[offset] === 0) {
        offset += 1; // immortal era
      } else {
        offset += 2; // mortal era
      }

      // Compact-encoded nonce
      var nonceResult = readCompact(bytes, offset);
      offset = nonceResult.nextOffset;

      // Compact-encoded tip
      var tipResult = readCompact(bytes, offset);
      offset = tipResult.nextOffset;

      // Now at call index: section + method
      if (offset + 1 < bytes.length) {
        var key = bytes[offset] + "," + bytes[offset + 1];
        if (callMap[key]) { var parts = callMap[key].split("."); section = parts[0]; method = parts[1]; }
      }
    } else {
      // Unsigned/inherent: call index is right at offset
      var key = bytes[offset] + "," + bytes[offset + 1];
      if (callMap[key]) { var parts = callMap[key].split("."); section = parts[0]; method = parts[1]; }
      else { section = "inherent"; method = "sec" + bytes[offset]; }
      signer = "(inherent)";
    }

    // Build hash from first 16 bytes of the full data
    var hashBytes = bytes.slice(0, 16);
    var extHash = "0x" + hashBytes.map(function(b) { return ("0" + b.toString(16)).slice(-2); }).join("");

    if (section === "timestamp") return { section: "timestamp", method: "set", fullType: "timestamp.set", signer: "", value: "0", fee: "0", hash: extHash, block: blockNum, time: blockTime, blockHash: blockHash, isSigned: false, multiInstr: false, skip: true };

    return { hash: extHash, block: blockNum, time: blockTime, section: section, method: method, fullType: section + "." + method, signer: signer, value: "0", fee: "0", blockHash: blockHash, isSigned: isSigned, multiInstr: false };
  } catch(e) {
    return { section: "error", method: "?", signer: "", value: "0", fee: "0", blockHash: blockHash, isSigned: false, multiInstr: false };
  }
}

// Helper: read a SCALE compact-encoded integer
function readCompact(bytes, offset) {
  if (offset >= bytes.length) return { value: 0, nextOffset: offset };
  var first = bytes[offset];
  var mode = first & 0x03;
  if (mode === 0) {
    return { value: first >> 2, nextOffset: offset + 1 };
  } else if (mode === 1) {
    if (offset + 1 >= bytes.length) return { value: 0, nextOffset: offset + 1 };
    return { value: (first | (bytes[offset + 1] << 8)) >> 2, nextOffset: offset + 2 };
  } else if (mode === 2) {
    if (offset + 3 >= bytes.length) return { value: 0, nextOffset: offset + 1 };
    return { value: (first | (bytes[offset + 1] << 8) | (bytes[offset + 2] << 16) | (bytes[offset + 3] << 24)) >>> 2, nextOffset: offset + 4 };
  } else {
    var bigLen = (first >> 2) + 4;
    return { value: 0, nextOffset: offset + 1 + bigLen };
  }
}'''

html = html[:idx_start] + new_func + html[idx_end:]

with open(TX_PATH, "w") as f:
    f.write(html)
print(f"Transactions decoder replaced ({len(html)} bytes)")

# Also fix explorer page
EXP_PATH = "/var/www/verdiscan/explorer/index.html"
with open(EXP_PATH, "r") as f:
    exp = f.read()

exp_old = "function decodeExtrinsicCall(extHex) {"
ei = exp.find(exp_old)
if ei == -1:
    print("Explorer function not found"); exit(0)

# Count braces to find end
depth = 0; j = ei
while j < len(exp):
    if exp[j] == '{': depth += 1
    elif exp[j] == '}':
        depth -= 1
        if depth == 0: break
    j += 1

new_exp = '''function decodeExtrinsicCall(extData) {
  try {
    var bytes;
    if (typeof extData === "string") {
      var hex = extData.startsWith("0x") ? extData.slice(2) : extData;
      bytes = [];
      for (var i = 0; i < hex.length; i += 2) { bytes.push(parseInt(hex.substr(i, 2), 16)); }
    } else if (Array.isArray(extData)) { bytes = extData; } else { return { section: "error", method: "?", sender: "" }; }
    if (bytes.length < 4) return { section: "error", method: "?", sender: "" };

    var offset = 2; // Skip 2-byte prefix
    var versionByte = bytes[offset];
    var callMap = {
      "0,0": ["system","remark"], "0,1": ["system","setHeapPages"], "0,2": ["system","setCode"], "0,3": ["system","setStorage"],
      "1,0": ["timestamp","set"],
      "4,0": ["balances","transferAllowDeath"], "4,1": ["balances","setBalance"], "4,3": ["balances","transferKeepAlive"], "4,4": ["balances","transferAll"],
      "6,0": ["sudo","sudo"],
      "30,0": ["dpos","registerValidator"], "30,1": ["dpos","unregisterValidator"], "30,2": ["dpos","updateGreenScore"], "30,5": ["dpos","setValidatorName"],
      "31,0": ["ammDex","createPool"], "31,1": ["ammDex","addLiquidity"], "31,2": ["ammDex","removeLiquidity"], "31,3": ["ammDex","swap"],
      "32,0": ["eco","mintCarbonCredit"], "32,1": ["eco","createReforestProject"], "32,2": ["eco","logReforestation"],
    };

    if (versionByte >= 0x80) {
      offset++;
      var sigType = bytes[offset]; offset++;
      offset += (sigType === 2) ? 65 : 64;
      var sender = offset + 32 <= bytes.length ? "0x" + bytes.slice(offset, offset+32).map(function(b){return("0"+b.toString(16)).slice(-2)}).join("") : "[signed]";
      offset += 32;
      offset += (bytes[offset] === 0) ? 1 : 2; // era
      offset = readCompactExp(bytes, offset).nextOffset; // nonce
      offset = readCompactExp(bytes, offset).nextOffset; // tip
      var key = bytes[offset] + "," + bytes[offset+1];
      if (callMap[key]) return { section: callMap[key][0], method: callMap[key][1], sender: sender };
      return { section: "signed", method: "unknown", sender: sender };
    } else {
      var key = bytes[offset] + "," + bytes[offset+1];
      if (callMap[key]) return { section: callMap[key][0], method: callMap[key][1], sender: "(inherent)" };
      return { section: "inherent", method: "sec" + bytes[offset], sender: "(inherent)" };
    }
  } catch(e) { return { section: "error", method: "?", sender: "" }; }
}
function readCompactExp(bytes, offset) {
  if (offset >= bytes.length) return { value: 0, nextOffset: offset };
  var first = bytes[offset]; var mode = first & 0x03;
  if (mode === 0) return { value: first >> 2, nextOffset: offset + 1 };
  if (mode === 1 && offset+1 < bytes.length) return { value: (first|(bytes[offset+1]<<8))>>2, nextOffset: offset+2 };
  if (mode === 2 && offset+3 < bytes.length) return { value: (first|(bytes[offset+1]<<8)|(bytes[offset+2]<<16)|(bytes[offset+3]<<24))>>>2, nextOffset: offset+4 };
  return { value: 0, nextOffset: offset + 1 + ((first>>2)+4) };
}'''

exp = exp[:ei] + new_exp + exp[j+1:]
with open(EXP_PATH, "w") as f:
    f.write(exp)
print(f"Explorer decoder replaced ({len(exp)} bytes)")
