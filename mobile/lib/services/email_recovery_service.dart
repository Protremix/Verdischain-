import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'secure_crypto.dart';

/// Email-based wallet recovery service.
/// Mnemonic is encrypted locally with PBKDF2 + HMAC-CTR before upload.
/// Server only stores the encrypted blob — never plaintext or password.
class EmailRecoveryService {
  static const _relayUrl = 'https://verdischain.com/api/tx-relay';

  /// Backup mnemonic to server, encrypted with password.
  /// Returns true on success, throws on error.
  static Future<bool> backupWallet({
    required String email,
    required String password,
    required String mnemonic,
    String address = '',
  }) async {
    try {
      // Encrypt mnemonic locally — server never sees plaintext
      final encryptedBlob = SecureCrypto.encrypt(mnemonic, password);

      final res = await http.post(
        Uri.parse(_relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'action': 'wallet-backup',
          'email': email.trim().toLowerCase(),
          'ciphertext': encryptedBlob,
          'salt': '',
          'iv': '',
          'address': address,
        }),
      ).timeout(const Duration(seconds: 15));

      final data = json.decode(res.body);
      if (data['ok'] == true) {
        debugPrint('Wallet backup saved for $email');
        return true;
      } else {
        throw Exception(data['error'] ?? 'Backup failed');
      }
    } catch (e) {
      debugPrint('Backup error: $e');
      rethrow;
    }
  }

  /// Recover mnemonic from server by email + password.
  /// Returns the decrypted mnemonic, or throws on error.
  static Future<String> recoverWallet({
    required String email,
    required String password,
  }) async {
    try {
      final res = await http.post(
        Uri.parse(_relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'action': 'wallet-recover',
          'email': email.trim().toLowerCase(),
        }),
      ).timeout(const Duration(seconds: 15));

      final data = json.decode(res.body);
      if (data['ok'] != true) {
        throw Exception(data['error'] ?? 'No backup found');
      }

      final backup = data['backup'] as Map<String, dynamic>;
      final ciphertext = backup['ciphertext'] as String? ?? '';
      if (ciphertext.isEmpty) {
        throw Exception('Encrypted backup is empty');
      }

      // Decrypt locally — password never sent to server
      final mnemonic = SecureCrypto.decrypt(ciphertext, password);
      if (mnemonic == null) {
        throw Exception('Decryption failed — wrong password or corrupted backup');
      }

      debugPrint('Wallet recovered for $email');
      return mnemonic;
    } catch (e) {
      debugPrint('Recovery error: $e');
      rethrow;
    }
  }
}
