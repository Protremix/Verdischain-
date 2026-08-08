with open('/opt/verdis-wallet/mobile/lib/services/wallet_service.dart', 'r') as f:
    content = f.read()

# 1. Add imports
old_import = "import 'package:crypto/crypto.dart';"
new_imports = """import 'dart:math';
import 'package:crypto/crypto.dart';
import 'bip39_words.dart';"""

if 'dart:math' not in content:
    content = content.replace(old_import, new_imports, 1)
    print("Added dart:math and bip39_words imports")
else:
    if 'bip39_words' not in content:
        content = content.replace("import 'package:crypto/crypto.dart';",
            "import 'package:crypto/crypto.dart';\nimport 'bip39_words.dart';", 1)
        print("Added bip39_words import")

# 2. Fix Python-style if in sendTokens
old_py_if = """      if relayData['ok'] == true:
        txHash = relayData['extrinsic_hash'] ?? '0xpending';
      else:
        throw Exception(relayData['error'] ?? 'TX Relay failed');"""

new_dart_if = """      if (relayData['ok'] == true) {
        txHash = relayData['extrinsic_hash'] ?? '0xpending';
      } else {
        throw Exception(relayData['error'] ?? 'TX Relay failed');
      }"""

if old_py_if in content:
    content = content.replace(old_py_if, new_dart_if)
    print("Fixed Python-style if to Dart syntax")
else:
    print("Python if not found (may already be fixed)")

# 3. Fix broken fetchBalance (extra closing brace + leftover staking data)
old_balance = """      } catch (_) {
        // No simulated fallback — real RPC only
        // Balance will show 0 if RPC unavailable
      }
    }
    } catch (e) {"""

new_balance = """      } catch (_) {
        // Balance will show 0 if RPC unavailable
      }
    } catch (e) {"""

if old_balance in content:
    content = content.replace(old_balance, new_balance)
    print("Fixed fetchBalance structure")
else:
    # Try simpler fix
    old_balance2 = """        // Balance will show 0 if RPC unavailable
      }
    }
    } catch (e) {"""
    new_balance2 = """        // Balance will show 0 if RPC unavailable
      }
    } catch (e) {"""
    if old_balance2 in content:
        content = content.replace(old_balance2, new_balance2)
        print("Fixed fetchBalance (simpler)")
    else:
        print("fetchBalance structure not found for fix")

# 4. Replace _generateAddress with server-based async derivation
old_gen_addr = """  // Generate deterministic address from seed/name
  String _generateAddress(String input) {
    final bytes = utf8.encode(input + DateTime.now().microsecondsSinceEpoch.toString());
    final digest = sha256.convert(bytes);
    final hexStr = digest.toString().substring(0, 36);
    return 'vrdx1q$hexStr';
  }"""

new_gen_addr = """  // Derive SS58 address from mnemonic via server (sr25519, prefix 909)
  Future<String> _deriveAddress(String mnemonic) async {
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
  }"""

if old_gen_addr in content:
    content = content.replace(old_gen_addr, new_gen_addr)
    print("Replaced _generateAddress with _deriveAddress (server-based)")
else:
    print("ERROR: _generateAddress not found")

# 5. Replace generateSeedPhrase with BIP39 standard
old_seed = """  // Generate random 12-word seed phrase
  String generateSeedPhrase() {
    const wordList = [
      'green', 'verdis', 'carbon', 'forest', 'energy', 'solar',
      'clean', 'block', 'chain', 'crypto', 'shield', 'secure',
      'future', 'planet', 'leaf', 'nature', 'seed', 'sprout',
      'harmony', 'stream', 'token', 'vault', 'beacon', 'breeze'
    ];
    final random = Random.secure();
    final List<String> words = [];
    for (int i = 0; i < 12; i++) {
      words.add(wordList[random.nextInt(wordList.length)]);
    }
    return words.join(' ');
  }"""

new_seed = """  // Generate BIP39 standard 12-word mnemonic
  String generateSeedPhrase() {
    final random = Random.secure();
    // 128 bits = 16 bytes of entropy
    final entropy = List<int>.generate(16, (_) => random.nextInt(256));
    // SHA256 checksum (first 4 bits)
    final checksumByte = sha256.convert(entropy).bytes[0];
    // Combine entropy bits + checksum bits
    String bits = '';
    for (final b in entropy) {
      bits += b.toRadixString(2).padLeft(8, '0');
    }
    bits += (checksumByte >> 4).toRadixString(2).padLeft(4, '0');
    // Map 11-bit groups to BIP39 words
    final List<String> mnemonic = [];
    for (int i = 0; i < 12; i++) {
      final index = int.parse(bits.substring(i * 11, (i + 1) * 11), radix: 2);
      mnemonic.add(BIP39_WORDS[index]);
    }
    return mnemonic.join(' ');
  }"""

if old_seed in content:
    content = content.replace(old_seed, new_seed)
    print("Replaced generateSeedPhrase with BIP39 standard")
else:
    print("ERROR: generateSeedPhrase not found")

# 6. Update createNewWallet to use async _deriveAddress
old_create = """  Future<AccountRecord?> createNewWallet(String name, {String? seedPhrase}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final seed = seedPhrase ?? generateSeedPhrase();
      final address = _generateAddress(seed);
      final encryptedKey = base64.encode(utf8.encode(seed));"""

new_create = """  Future<AccountRecord?> createNewWallet(String name, {String? seedPhrase}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final seed = seedPhrase ?? generateSeedPhrase();
      final address = await _deriveAddress(seed);
      final encryptedKey = base64.encode(utf8.encode(seed));"""

if old_create in content:
    content = content.replace(old_create, new_create)
    print("Updated createNewWallet to use async _deriveAddress")
else:
    print("ERROR: createNewWallet not found")

# 7. Update importWallet to use async _deriveAddress
old_import = """      final address = _generateAddress(cleanInput);
      final encryptedKey = base64.encode(utf8.encode(cleanInput));"""

new_import = """      final address = await _deriveAddress(cleanInput);
      final encryptedKey = base64.encode(utf8.encode(cleanInput));"""

if old_import in content:
    content = content.replace(old_import, new_import)
    print("Updated importWallet to use async _deriveAddress")
else:
    print("ERROR: importWallet _generateAddress call not found")

# 8. Remove leftover staking data in fetchBalance
old_staking = """        // Balance will show 0 if RPC unavailable
          _stakedAmount = 500.0;
          _stakingRewards = 14.25;
        }"""
if old_staking in content:
    content = content.replace(old_staking, "        // Balance will show 0 if RPC unavailable\n      }")
    print("Removed leftover staking data")

# 9. Remove hardcoded fallback balance
old_fallback = """        if (_vrdxBalance == 0.0) {
          _vrdxBalance = 1540.75;"""
if old_fallback in content:
    content = content.replace(old_fallback, "        // Balance is 0 if RPC unavailable")
    print("Removed hardcoded fallback balance")

# 10. Remove any remaining simulated staking values
old_sim_stake = """          _stakedAmount = 500.0;
          _stakingRewards = 14.25;"""
if old_sim_stake in content:
    content = content.replace(old_sim_stake, "")
    print("Removed simulated staking values")

with open('/opt/verdis-wallet/mobile/lib/services/wallet_service.dart', 'w') as f:
    f.write(content)

print("All wallet_service.dart fixes applied")
