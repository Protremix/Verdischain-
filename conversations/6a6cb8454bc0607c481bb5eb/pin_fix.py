#!/usr/bin/env python3
"""Fix PIN hashing: Upgrade to PBKDF2, unify all 3 implementations."""
import os

# 1. Update WalletCrypto with PBKDF2
wallet_crypto_path = '/opt/verdis-wallet/lib/core/security/wallet_crypto.dart'
with open(wallet_crypto_path, 'r') as f:
    content = f.read()

old_hash = """  static String hashPin(String pin) {
    final bytes = utf8.encode(pin);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  static bool verifyPin(String pin, String hash) {
    return hashPin(pin) == hash;
  }"""

new_hash = """  /// PBKDF2 with HMAC-SHA256: 100,000 iterations, 32-byte key, random salt.
  /// Format: "saltHex:hashHex" - salt is 16 bytes, hash is 32 bytes.
  static const int _pbkdf2Iterations = 100000;
  static const int _pbkdf2KeyLen = 32;
  static const int _pbkdf2SaltLen = 16;

  static String _pbkdf2HmacSha256(String pin, Uint8List salt) {
    final hmac = Hmac(sha256, salt);
    final pinBytes = utf8.encode(pin);
    final blockLen = 32; // SHA-256 output size
    final numBlocks = (_pbkdf2KeyLen + blockLen - 1) ~/ blockLen;
    final result = <int>[];
    for (var block = 1; block <= numBlocks; block++) {
      final blockBytes = Uint8List(4);
      blockBytes[0] = (block >> 24) & 0xFF;
      blockBytes[1] = (block >> 16) & 0xFF;
      blockBytes[2] = (block >> 8) & 0xFF;
      blockBytes[3] = block & 0xFF;
      var u = Uint8List.fromList([...pinBytes, ...blockBytes]);
      u = Uint8List.fromList(hmac.convert(u).bytes);
      final t = Uint8List.fromList(u);
      for (var i = 1; i < _pbkdf2Iterations; i++) {
        u = Uint8List.fromList(hmac.convert(u).bytes);
        for (var j = 0; j < t.length; j++) {
          t[j] ^= u[j];
        }
      }
      result.addAll(t);
    }
    return HEX.encode(Uint8List.fromList(result.sublist(0, _pbkdf2KeyLen)));
  }

  static String hashPin(String pin) {
    final salt = _generateRandomBytes(_pbkdf2SaltLen);
    final hash = _pbkdf2HmacSha256(pin, salt);
    return HEX.encode(salt) + ':' + hash;
  }

  static bool verifyPin(String pin, String stored) {
    final parts = stored.split(':');
    if (parts.length != 2) return false;
    try {
      final salt = Uint8List.fromList(HEX.decode(parts[0]));
      final hash = _pbkdf2HmacSha256(pin, salt);
      return _constantTimeEquals(hash, parts[1]);
    } catch (_) {
      return false;
    }
  }

  static Uint8List _generateRandomBytes(int length) {
    final random = Random.secure();
    return Uint8List.fromList(
      List<int>.generate(length, (_) => random.nextInt(256)),
    );
  }

  static bool _constantTimeEquals(String a, String b) {
    if (a.length != b.length) return false;
    var result = 0;
    for (var i = 0; i < a.length; i++) {
      result |= a.codeUnitAt(i) ^ b.codeUnitAt(i);
    }
    return result == 0;
  }"""

if old_hash in content:
    content = content.replace(old_hash, new_hash)
    # Add Random import
    if "import 'dart:math'" not in content:
        content = content.replace(
            "import 'dart:typed_data';",
            "import 'dart:typed_data';\nimport 'dart:math' show Random;"
        )
    with open(wallet_crypto_path, 'w') as f:
        f.write(content)
    print('Updated WalletCrypto with PBKDF2')
else:
    print('Could not find old hashPin in wallet_crypto.dart')

# 2. Fix SettingsRepositoryImpl
settings_path = '/opt/verdis-wallet/lib/features/settings/data/settings_repository_impl.dart'
with open(settings_path, 'r') as f:
    settings = f.read()

# Fix verifyPin
old_verify = """  @override
  Future<bool> verifyPin(String pin) async {
    final storedHash = await _secureStorage.getPinHash();
    if (storedHash == null) {
      // Default pin verification for demo/uninitialized state
      return false;  // No backdoor PIN
    }
    // Simple hash verification comparison
    return storedHash == pin;  // No backdoor PIN
  }"""

new_verify = """  @override
  Future<bool> verifyPin(String pin) async {
    final storedHash = await _secureStorage.getPinHash();
    if (storedHash == null) return false;
    return WalletCrypto.verifyPin(pin, storedHash);
  }"""

if old_verify in settings:
    settings = settings.replace(old_verify, new_verify)
    print('Fixed SettingsRepositoryImpl.verifyPin')
else:
    print('verifyPin pattern not found in settings')

# Fix changePin
old_change = """    // Hash the new PIN before storing (never store raw PIN)
    final bytes = utf8.encode('${newPin}_verdis_salt_2026');
    final digest = sha256.convert(bytes);
    await _secureStorage.storePinHash(digest.toString());"""

new_change = """    // Hash the new PIN with PBKDF2 before storing
    final pinHash = WalletCrypto.hashPin(newPin);
    await _secureStorage.storePinHash(pinHash);"""

if old_change in settings:
    settings = settings.replace(old_change, new_change)
    print('Fixed SettingsRepositoryImpl.changePin')
else:
    print('changePin pattern not found in settings')

# Add WalletCrypto import
if 'wallet_crypto' not in settings:
    settings = settings.replace(
        "import 'package:verdis_wallet/core/security/secure_storage.dart';",
        "import 'package:verdis_wallet/core/security/secure_storage.dart';\nimport 'package:verdis_wallet/core/security/wallet_crypto.dart';"
    )
    print('Added WalletCrypto import to settings')

# Remove unused crypto import since we no longer use sha256 directly
# Actually keep it - might be used elsewhere

with open(settings_path, 'w') as f:
    f.write(settings)

# 3. Fix WalletRepositoryImpl
wallet_repo_path = '/opt/verdis-wallet/lib/features/onboarding/data/wallet_repository_impl.dart'
with open(wallet_repo_path, 'r') as f:
    repo = f.read()

old_repo_hash = """  @override
  Future<String> hashPin(String pin) async {
    // PBKDF2-like: iterate Blake2b with salt to resist brute-force
    final salt = utf8.encode('verdis_pin_salt_2026');
    var input = Uint8List.fromList([...utf8.encode(pin), ...salt]);
    for (var i = 0; i < 10000; i++) {
      input = blake2b256(input);
    }
    return HEX.encode(input);
  }"""

new_repo_hash = """  @override
  Future<String> hashPin(String pin) async {
    // Use canonical PBKDF2 from WalletCrypto
    return WalletCrypto.hashPin(pin);
  }"""

if old_repo_hash in repo:
    repo = repo.replace(old_repo_hash, new_repo_hash)
    print('Fixed WalletRepositoryImpl.hashPin')
else:
    print('hashPin pattern not found in wallet_repo')

old_repo_verify = """  @override
  Future<bool> verifyPin(String pin) async {
    final storedHash = await _secureStorage.getPinHash();
    if (storedHash == null) return false;
    final currentHash = await hashPin(pin);
    return storedHash == currentHash;
  }"""

new_repo_verify = """  @override
  Future<bool> verifyPin(String pin) async {
    final storedHash = await _secureStorage.getPinHash();
    if (storedHash == null) return false;
    return WalletCrypto.verifyPin(pin, storedHash);
  }"""

if old_repo_verify in repo:
    repo = repo.replace(old_repo_verify, new_repo_verify)
    print('Fixed WalletRepositoryImpl.verifyPin')
else:
    print('verifyPin pattern not found in wallet_repo')

# Add WalletCrypto import
if 'wallet_crypto' not in repo:
    # Find a verdis_wallet import line and add after it
    lines = repo.split('\n')
    for i, line in enumerate(lines):
        if 'import' in line and 'verdis_wallet' in line:
            lines.insert(i + 1, "import 'package:verdis_wallet/core/security/wallet_crypto.dart';")
            break
    repo = '\n'.join(lines)
    print('Added WalletCrypto import to wallet_repo')

with open(wallet_repo_path, 'w') as f:
    f.write(repo)

print('All PIN hashing fixes applied')
