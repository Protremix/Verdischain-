#!/usr/bin/env python3
"""Fix the decodeExtrinsic function to handle byte arrays."""

TX_PATH = "/var/www/verdiscan/transactions/index.html"

with open(TX_PATH, "r") as f:
    html = f.read()

# Find and replace the entire decodeExtrinsic function
old_start = "function decodeExtrinsic(extHex, blockNum, blockHash, blockTime) {"
idx_start = html.find(old_start)
if idx_start == -1:
    print("ERROR: Could not find decodeExtrinsic function")
    exit(1)

# Find the end of the function by counting braces
depth = 0
i = idx_start
while i < len(html):
    if html[i] == '{':
        depth += 1
    elif html[i] == '}':
        depth -= 1
        if depth == 0:
            idx_end = i + 1
            break
    i += 1

new_func = '''function decodeExtrinsic(extHex, blockNum, blockHash, blockTime) {
  try {
    var bytes;
    if (typeof extHex === "string") {
      var hex = extHex.startsWith("0x") ? extHex.slice(2) : extHex;
      bytes = [];
      for (var i = 0; i < hex.length; i += 2) { bytes.push(parseInt(hex.substr(i, 2), 16)); }
    } else if (Array.isArray(extHex)) {
      bytes = extHex;
    } else {
      return { section: "error", method: "?", signer: "", value: "0", fee: "0", blockHash: blockHash, isSigned: false, multiInstr: false };
    }
    if (bytes.length < 2) return { section: "error", method: "?", signer: "", value: "0", fee: "0", blockHash: blockHash, isSigned: false, multiInstr: false };

    var firstByte = bytes[0];
    var section = "unknown", method = "unknown", signer = "";
    var callMap = {
      "0,0": "system.remark", "0,1": "system.setHeapPages", "0,2": "system.setCode", "0,3": "system.setStorage",
      "1,0": "timestamp.set",
      "4,0": "balances.transferAllowDeath", "4,1": "balances.setBalance", "4,3": "balances.transferKeepAlive", "4,4": "balances.transferAll",
      "6,0": "sudo.sudo",
      "30,0": "dpos.registerValidator", "30,1": "dpos.unregisterValidator", "30,2": "dpos.updateGreenScore", "30,5": "dpos.setValidatorName",
      "31,0": "ammDex.createPool", "31,1": "ammDex.addLiquidity", "31,2": "ammDex.removeLiquidity", "31,3": "ammDex.swap",
      "32,0": "eco.mintCarbonCredit", "32,1": "eco.createReforestProject", "32,2": "eco.logReforestation", "32,3": "eco.transferCarbonCredit",
    };

    if (firstByte >= 0x80) {
      if (bytes.length > 97) {
        var signerBytes = bytes.slice(65, 97);
        signer = "0x" + signerBytes.map(function(b) { return ("0" + b.toString(16)).slice(-2); }).join("");
      } else { signer = "[signed]"; }
      for (var offset = 100; offset < bytes.length - 1; offset++) {
        var key = bytes[offset] + "," + bytes[offset + 1];
        if (callMap[key]) { var parts = callMap[key].split("."); section = parts[0]; method = parts[1]; break; }
      }
    } else {
      var key = bytes[0] + "," + bytes[1];
      if (callMap[key]) { var parts = callMap[key].split("."); section = parts[0]; method = parts[1]; } else { section = "inherent"; method = "sec" + bytes[0]; }
      signer = "(inherent)";
    }

    var hashBytes = bytes.slice(0, 16);
    var extHash = "0x" + hashBytes.map(function(b) { return ("0" + b.toString(16)).slice(-2); }).join("");

    if (section === "timestamp") return { section: "timestamp", method: "set", fullType: "timestamp.set", signer: "", value: "0", fee: "0", hash: extHash, block: blockNum, time: blockTime, blockHash: blockHash, isSigned: false, multiInstr: false, skip: true };

    return { hash: extHash, block: blockNum, time: blockTime, section: section, method: method, fullType: section + "." + method, signer: signer, value: "0", fee: "0", blockHash: blockHash, isSigned: firstByte >= 0x80, multiInstr: false };
  } catch(e) {
    return { section: "error", method: "?", signer: "", value: "0", fee: "0", blockHash: blockHash, isSigned: false, multiInstr: false };
  }
}'''

html = html[:idx_start] + new_func + html[idx_end:]

with open(TX_PATH, "w") as f:
    f.write(html)
print("Transactions page decoder fixed (" + str(len(html)) + " bytes)")

# Also fix explorer page
EXP_PATH = "/var/www/verdiscan/explorer/index.html"
with open(EXP_PATH, "r") as f:
    exp = f.read()

exp_old = "function decodeExtrinsicCall(extHex) {"
ei = exp.find(exp_old)
if ei != -1:
    depth = 0
    j = ei
    while j < len(exp):
        if exp[j] == '{': depth += 1
        elif exp[j] == '}':
            depth -= 1
            if depth == 0: break
        j += 1
    
    new_exp = '''function decodeExtrinsicCall(extHex) {
  try {
    var bytes;
    if (typeof extHex === "string") {
      var hex = extHex.startsWith("0x") ? extHex.slice(2) : extHex;
      bytes = [];
      for (var i = 0; i < hex.length; i += 2) { bytes.push(parseInt(hex.substr(i, 2), 16)); }
    } else if (Array.isArray(extHex)) { bytes = extHex; } else { return { section: "error", method: "?", sender: "" }; }
    if (bytes.length < 2) return { section: "error", method: "?", sender: "" };
    
    var firstByte = bytes[0];
    var callMap = {
      "0,0": ["system","remark"], "0,1": ["system","setHeapPages"], "0,2": ["system","setCode"], "0,3": ["system","setStorage"],
      "1,0": ["timestamp","set"],
      "4,0": ["balances","transferAllowDeath"], "4,1": ["balances","setBalance"], "4,3": ["balances","transferKeepAlive"], "4,4": ["balances","transferAll"],
      "6,0": ["sudo","sudo"],
      "30,0": ["dpos","registerValidator"], "30,1": ["dpos","unregisterValidator"], "30,2": ["dpos","updateGreenScore"], "30,5": ["dpos","setValidatorName"],
      "31,0": ["ammDex","createPool"], "31,1": ["ammDex","addLiquidity"], "31,2": ["ammDex","removeLiquidity"], "31,3": ["ammDex","swap"],
      "32,0": ["eco","mintCarbonCredit"], "32,1": ["eco","createReforestProject"], "32,2": ["eco","logReforestation"],
    };
    
    if (firstByte >= 0x80) {
      var sender = bytes.length > 97 ? "0x" + bytes.slice(65,73).map(function(b){return("0"+b.toString(16)).slice(-2)}).join("") + "..." : "[signed]";
      for (var offset = 100; offset < bytes.length - 1; offset++) {
        var key = bytes[offset] + "," + bytes[offset+1];
        if (callMap[key]) return { section: callMap[key][0], method: callMap[key][1], sender: sender };
      }
      return { section: "signed", method: "unknown", sender: sender };
    } else {
      var key = bytes[0] + "," + bytes[1];
      if (callMap[key]) return { section: callMap[key][0], method: callMap[key][1], sender: "(inherent)" };
      return { section: "inherent", method: "sec" + bytes[0], sender: "(inherent)" };
    }
  } catch(e) { return { section: "error", method: "?", sender: "" }; }
}'''
    
    exp = exp[:ei] + new_exp + exp[j+1:]
    with open(EXP_PATH, "w") as f:
        f.write(exp)
    print("Explorer decoder fixed (" + str(len(exp)) + " bytes)")
else:
    print("Explorer function not found - skipping")
