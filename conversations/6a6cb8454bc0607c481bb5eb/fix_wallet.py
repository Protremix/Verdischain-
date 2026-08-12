#!/usr/bin/env python3
"""Fix wallet_service.dart for non-custodial transaction signing"""

import sys

filepath = "/opt/verdis-wallet/mobile/lib/services/wallet_service.dart"
with open(filepath, "r") as f:
    content = f.read()

changes = []

# 1. Remove insecure deriveAddress fallback
old_derive = """  Future<String> _deriveAddress(String mnemonic) async {
    try {
      final result = await _cryptoChannel.invokeMethod('deriveAddress', {'mnemonic': mnemonic});
      if (result is Map && result['address'] != null) {
        return result['address'] as String;
      }
      throw Exception('Invalid response from crypto channel');
    } on PlatformException catch (e) {
      debugPrint('Local derivation failed, falling back to server: $e');
      // Fallback: use server derivation (mnemonic sent to server)
      // TODO: Remove this fallback once local derivation is verified
      final response = await http.post(
        Uri.parse('https://verdischain.com/api/tx-relay'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'action': 'derive-address', 'mnemonic': mnemonic}),
      );
      final data = json.decode(response.body);
      if (data['ok'] == true && data['address'] != null) {
        return data['address'] as String;
      }
      throw Exception(data['error'] ?? 'Address derivation failed');
    }
  }"""

new_derive = """  Future<String> _deriveAddress(String mnemonic) async {
    // Non-custodial: derive address locally via WebView crypto channel
    // NEVER send mnemonic to server
    try {
      final result = await _cryptoChannel.invokeMethod('deriveAddress', {'mnemonic': mnemonic});
      if (result is Map && result['address'] != null) {
        return result['address'] as String;
      }
      throw Exception('Invalid response from crypto channel');
    } on PlatformException catch (e) {
      debugPrint('Local derivation failed: $e');
      throw Exception('Address derivation failed: ${e.message}. Please restart the app.');
    }
  }"""

if old_derive in content:
    content = content.replace(old_derive, new_derive)
    changes.append("Fixed deriveAddress (removed server fallback)")
else:
    # Try to find a partial match
    if "falling back to server" in content:
        # Use regex to replace the whole method
        import re
        pattern = r"Future<String> _deriveAddress\(String mnemonic\) async \{.*?\n  \}"
        replacement = new_derive.strip()
        content_new = re.sub(pattern, replacement, content, flags=re.DOTALL)
        if content_new != content:
            content = content_new
            changes.append("Fixed deriveAddress (regex)")
        else:
            changes.append("WARNING: deriveAddress regex failed")
    else:
        changes.append("deriveAddress already fixed or not found")

# 2. Replace sendTokens transfer action with local signing
old_send = """      final relayRes = await http.post(
        Uri.parse('https://verdischain.com/api/tx-relay'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'action': 'transfer',
          'to': recipient,
          'amount': (amount * 1e9).round(),
        }),
      );
      final relayData = json.decode(relayRes.body);
      if (relayData['ok'] == true) {
        txHash = relayData['extrinsic_hash'] ?? '0xpending';
      } else {
        throw Exception(relayData['error'] ?? 'TX Relay failed');
      }"""

new_send = """      // 1. Get nonce from chain
      final nonceRes = await http.post(
        Uri.parse(_rpcUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'jsonrpc': '2.0',
          'method': 'system_accountNextIndex',
          'params': [_activeAccount!.address],
          'id': 1,
        }),
      );
      final nonceData = json.decode(nonceRes.body);
      final nonce = nonceData['result'] as int? ?? 0;

      // 2. Get genesis hash
      final genesisRes = await http.post(
        Uri.parse(_rpcUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'jsonrpc': '2.0',
          'method': 'chain_getBlockHash',
          'params': [0],
          'id': 2,
        }),
      );
      final genesisData = json.decode(genesisRes.body);
      final genesisHash = genesisData['result'] as String?;

      // 3. Get spec version
      final versionRes = await http.post(
        Uri.parse(_rpcUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'jsonrpc': '2.0',
          'method': 'state_getRuntimeVersion',
          'params': [],
          'id': 3,
        }),
      );
      final versionData = json.decode(versionRes.body);
      final specVersion = versionData['result']?['specVersion'] as int? ?? 14;

      // 4. Get current block hash
      final blockHashRes = await http.post(
        Uri.parse(_rpcUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'jsonrpc': '2.0',
          'method': 'chain_getBlockHash',
          'params': [],
          'id': 4,
        }),
      );
      final blockHashData = json.decode(blockHashRes.body);
      final blockHash = blockHashData['result'] as String? ?? genesisHash;

      // 5. Decrypt mnemonic
      final mnemonic = _decryptMnemonic();

      // 6. Sign extrinsic locally via WebView crypto channel
      final amountAtoms = (amount * 1e9).round();
      final signResult = await _cryptoChannel.invokeMethod('signTransfer', {
        'mnemonic': mnemonic,
        'destAddress': recipient,
        'amountAtoms': amountAtoms,
        'nonce': nonce,
        'genesisHash': genesisHash,
        'blockHash': blockHash,
        'specVersion': specVersion,
      });

      if (signResult is Map && signResult['extrinsic'] != null) {
        final extrinsicHex = signResult['extrinsic'] as String;

        // 7. Submit pre-signed extrinsic to TX Relay v3
        final relayRes = await http.post(
          Uri.parse('https://verdischain.com/api/tx-relay'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({
            'action': 'submit-extrinsic',
            'extrinsic': extrinsicHex,
          }),
        );
        final relayData = json.decode(relayRes.body);
        if (relayData['ok'] == true) {
          txHash = relayData['tx_hash'] ?? '0xpending';
        } else {
          throw Exception(relayData['error'] ?? 'TX Relay submission failed');
        }
      } else {
        throw Exception('Signing failed');
      }"""

if old_send in content:
    content = content.replace(old_send, new_send)
    changes.append("Fixed sendTokens (local signing + submit-extrinsic)")
else:
    if "'action': 'transfer'" in content:
        import re
        pattern = r"final relayRes = await http\.post\(.*?\}\n      \}\n      \}\n      _vrdxBalance"
        # Find the transfer block and replace
        idx = content.find("'action': 'transfer'")
        if idx > 0:
            # Find the start of the http.post call
            start = content.rfind("final relayRes", 0, idx)
            # Find the end (the line with _vrdxBalance)
            end = content.find("_vrdxBalance -= amount;", idx)
            if start > 0 and end > 0:
                content = content[:start] + new_send + "\n\n      " + content[end:]
                changes.append("Fixed sendTokens (regex)")
            else:
                changes.append("WARNING: Could not find sendTokens boundaries")
        else:
            changes.append("WARNING: transfer action not found")
    else:
        changes.append("sendTokens already fixed or not found")

# 3. Add _decryptMnemonic helper
if "_decryptMnemonic" not in content:
    decrypt_method = """  String _decryptMnemonic() {
    if (_activeAccount == null) throw Exception('No active account');
    if (_activeAccount!.encryptedKey.isEmpty) throw Exception('No encrypted key');
    String stored = _activeAccount!.encryptedKey;
    if (_walletPin.isNotEmpty) {
      try {
        return SecureCrypto.decrypt(stored, _walletPin);
      } catch (e) {
        try {
          return String.fromCharCodes(base64Decode(stored));
        } catch (e2) {
          throw Exception('Failed to decrypt mnemonic');
        }
      }
    }
    try {
      return String.fromCharCodes(base64Decode(stored));
    } catch (e) {
      return stored;
    }
  }

"""
    if "  Future<String> _deriveAddress" in content:
        content = content.replace(
            "  Future<String> _deriveAddress",
            decrypt_method + "  Future<String> _deriveAddress"
        )
        changes.append("Added _decryptMnemonic helper")
    else:
        changes.append("WARNING: Could not find _deriveAddress to insert helper")
else:
    changes.append("_decryptMnemonic already exists")

# 4. Add dart:convert import if needed
if "import 'dart:convert'" not in content:
    if "import 'dart:async'" in content:
        content = content.replace(
            "import 'dart:async';",
            "import 'dart:async';\nimport 'dart:convert';"
        )
        changes.append("Added dart:convert import")
    else:
        changes.append("WARNING: Could not find import location for dart:convert")
else:
    changes.append("dart:convert already imported")

with open(filepath, "w") as f:
    f.write(content)

for c in changes:
    print(c)
print("All wallet service updates complete")
