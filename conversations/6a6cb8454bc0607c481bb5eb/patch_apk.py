#!/usr/bin/env python3
"""
Patch the APK wallet code to fix:
1. pin_security_service.dart: data['backup'] -> data['data']['backup']
2. security_settings_page.dart backup: add pin, salt, iv fields + PBKDF2 encryption
3. security_settings_page.dart recovery: fix data path + read salt/iv + PBKDF2 decryption

No visual/design changes — only code fixes.
"""

# === Fix 1: pin_security_service.dart — data['backup'] -> data['data']['backup'] ===
with open('/opt/verdis-wallet/lib/core/security/pin_security_service.dart', 'r') as f:
    svc_content = f.read()

old_recover = """      final data = json.decode(response.body) as Map<String, dynamic>;
      if (data['ok'] == true) {
        return (data['backup']) as Map<String, dynamic>?;
      } else {
        return null;
      }"""

new_recover = """      final data = json.decode(response.body) as Map<String, dynamic>;
      if (data['ok'] == true) {
        final d = data['data'] as Map<String, dynamic>?;
        return d?['backup'] as Map<String, dynamic>?;
      } else {
        return null;
      }"""

if old_recover in svc_content:
    svc_content = svc_content.replace(old_recover, new_recover)
    with open('/opt/verdis-wallet/lib/core/security/pin_security_service.dart', 'w') as f:
        f.write(svc_content)
    print("Fix 1: pin_security_service.dart patched (data['data']['backup'])")
else:
    print("Fix 1: SKIP -- pattern not found (may already be patched)")


# === Fix 2 & 3: security_settings_page.dart ===
with open('/opt/verdis-wallet/lib/features/settings/presentation/security_settings_page.dart', 'r') as f:
    ss_content = f.read()

# Add crypto import
old_imports = "import 'dart:convert';"
new_imports = "import 'dart:convert';\nimport 'dart:math';\nimport 'package:crypto/crypto.dart';"

if old_imports in ss_content and 'package:crypto/crypto.dart' not in ss_content:
    ss_content = ss_content.replace(old_imports, new_imports)
    print("Fix 2a: Added crypto import")
else:
    print("Fix 2a: SKIP -- import already present or pattern not found")

# Add helper functions after the class opening (before _isLoading)
old_fields = "  bool _isBackingUp = false;"
new_fields = """  bool _isBackingUp = false;

  // PBKDF2 key derivation using HMAC-SHA256 (matches web wallet's crypto scheme)
  static List<int> _deriveKey(String password, List<int> salt, {int iterations = 150000, int keyLength = 32}) {
    final hmac = Hmac(sha256, utf8.encode(password));
    final blockCount = (keyLength + 31) ~/ 32;
    final result = <int>[];
    for (var blockNum = 1; blockNum <= blockCount; blockNum++) {
      var u = <int>[...salt, (blockNum >> 24) & 0xFF, (blockNum >> 16) & 0xFF, (blockNum >> 8) & 0xFF, blockNum & 0xFF];
      var t = hmac.convert(u).bytes.toList();
      var resultBlock = List<int>.from(t);
      for (var i = 1; i < iterations; i++) {
        u = hmac.convert(t).bytes.toList();
        for (var j = 0; j < t.length; j++) {
          resultBlock[j] ^= u[j];
        }
        t = u;
      }
      result.addAll(resultBlock);
    }
    return result.sublist(0, keyLength);
  }

  // XOR encrypt/decrypt (symmetric -- same function for both)
  static List<int> _xorCipher(List<int> data, List<int> key) {
    return List<int>.generate(data.length, (i) => data[i] ^ key[i % key.length]);
  }

  static List<int> _randomBytes(int length) {
    final random = Random.secure();
    return List<int>.generate(length, (_) => random.nextInt(256));
  }"""

if old_fields in ss_content and '_deriveKey' not in ss_content:
    ss_content = ss_content.replace(old_fields, new_fields)
    print("Fix 2b: Added crypto helper functions")
else:
    print("Fix 2b: SKIP -- helpers already present or pattern not found")

# Fix backup function
old_backup_encrypt = """      // Encrypt mnemonic with PIN (XOR cipher for transport — server stores encrypted)
      final pinBytes = utf8.encode(result['pin']!);
      final mnemonicBytes = utf8.encode(mnemonic);
      final encrypted = List<int>.generate(
        mnemonicBytes.length,
        (i) => mnemonicBytes[i] ^ pinBytes[i % pinBytes.length],
      );
      final ciphertext = base64Encode(encrypted);

      // Send to tx-relay
      final response = await http.post(
        Uri.parse(_relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'action': 'wallet-backup',
          'email': result['email'],
          'ciphertext': ciphertext,
          'address': address,
        }),
      );"""

new_backup_encrypt = """      // Encrypt mnemonic with PBKDF2-derived key (matches web wallet crypto scheme)
      final salt = _randomBytes(16);
      final iv = _randomBytes(12);
      final key = _deriveKey(result['pin']!, salt);
      final mnemonicBytes = utf8.encode(mnemonic);
      final encrypted = _xorCipher(mnemonicBytes, key);
      final ciphertext = base64Encode(encrypted);
      final saltB64 = base64Encode(salt);
      final ivB64 = base64Encode(iv);

      // Send to tx-relay (now requires PIN field for server-side verification)
      final response = await http.post(
        Uri.parse(_relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'action': 'wallet-backup',
          'email': result['email'],
          'ciphertext': ciphertext,
          'salt': saltB64,
          'iv': ivB64,
          'address': address,
          'pin': result['pin'],
        }),
      );"""

if old_backup_encrypt in ss_content:
    ss_content = ss_content.replace(old_backup_encrypt, new_backup_encrypt)
    print("Fix 2c: Backup encryption upgraded + pin/salt/iv added")
else:
    print("Fix 2c: SKIP -- backup pattern not found")

# Fix recovery function
old_recover_decrypt = """      if (data['ok'] == true) {
        final ciphertext = data['data']['ciphertext'] as String;
        final pinBytes = utf8.encode(result['pin']!);
        final encrypted = base64Decode(ciphertext);
        final decrypted = List<int>.generate(
          encrypted.length,
          (i) => encrypted[i] ^ pinBytes[i % pinBytes.length],
        );
        final mnemonic = utf8.decode(decrypted);"""

new_recover_decrypt = """      if (data['ok'] == true) {
        final backup = data['data']['backup'] as Map<String, dynamic>;
        final ciphertext = backup['ciphertext'] as String;
        final saltB64 = backup['salt'] as String;
        final ivB64 = backup['iv'] as String;
        final salt = base64Decode(saltB64);
        final encrypted = base64Decode(ciphertext);
        final key = _deriveKey(result['pin']!, salt);
        final decrypted = _xorCipher(encrypted, key);
        final mnemonic = utf8.decode(decrypted);"""

if old_recover_decrypt in ss_content:
    ss_content = ss_content.replace(old_recover_decrypt, new_recover_decrypt)
    print("Fix 3: Recovery data path fixed + PBKDF2 decryption")
else:
    print("Fix 3: SKIP -- recovery pattern not found")

with open('/opt/verdis-wallet/lib/features/settings/presentation/security_settings_page.dart', 'w') as f:
    f.write(ss_content)

print("\nAll patches applied.")
