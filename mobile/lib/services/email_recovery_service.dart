import 'dart:convert';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:cryptography/cryptography.dart';

/// Email-based wallet recovery service.
///
/// Encryption scheme (matches the TX Relay v3 backend contract): AES-256-GCM
/// with a key derived via PBKDF2-HMAC-SHA256 (100,000 iterations) from the
/// user's password and a random 16-byte salt. A random 12-byte IV is used
/// per encryption. The server stores three separate base64 fields —
/// ciphertext, salt, iv — and never sees the plaintext mnemonic or password.
class EmailRecoveryService {
  static const _relayUrl = 'https://verdischain.com/api/tx-relay';
  static const _pbkdf2Iterations = 100000;
  static const _saltLength = 16;
  static const _ivLength = 12;

  static final _algorithm = AesGcm.with256bits();
  static final _pbkdf2 = Pbkdf2(
    macAlgorithm: Hmac.sha256(),
    iterations: _pbkdf2Iterations,
    bits: 256,
  );

  static List<int> _randomBytes(int length) {
    final random = Random.secure();
    return List<int>.generate(length, (_) => random.nextInt(256));
  }

  static Future<SecretKey> _deriveKey(String password, List<int> salt) async {
    final secretKey = SecretKey(utf8.encode(password));
    return _pbkdf2.deriveKey(secretKey: secretKey, nonce: salt);
  }

  /// Encrypt [plaintext] with [password]. Returns {ciphertext, salt, iv} —
  /// all base64-encoded, ready to send to the server.
  static Future<Map<String, String>> _encrypt(String plaintext, String password) async {
    final salt = _randomBytes(_saltLength);
    final iv = _randomBytes(_ivLength);
    final key = await _deriveKey(password, salt);

    final secretBox = await _algorithm.encrypt(
      utf8.encode(plaintext),
      secretKey: key,
      nonce: iv,
    );

    // Store ciphertext + 16-byte GCM tag concatenated, matching common
    // AES-GCM wire format (tag appended to ciphertext).
    final combined = <int>[...secretBox.cipherText, ...secretBox.mac.bytes];

    return {
      'ciphertext': base64.encode(combined),
      'salt': base64.encode(salt),
      'iv': base64.encode(iv),
    };
  }

  /// Decrypt using {ciphertext, salt, iv} (all base64) + password.
  /// Returns the plaintext mnemonic, or throws if the password is wrong
  /// or the data is corrupted (GCM auth tag check fails).
  static Future<String> _decrypt({
    required String ciphertextB64,
    required String saltB64,
    required String ivB64,
    required String password,
  }) async {
    final salt = base64.decode(saltB64);
    final iv = base64.decode(ivB64);
    final combined = base64.decode(ciphertextB64);

    // AES-GCM tag is 16 bytes, appended to the ciphertext.
    if (combined.length < 16) {
      throw Exception('Corrupted backup data');
    }
    final cipherBytes = combined.sublist(0, combined.length - 16);
    final macBytes = combined.sublist(combined.length - 16);

    final key = await _deriveKey(password, salt);
    final secretBox = SecretBox(cipherBytes, nonce: iv, mac: Mac(macBytes));

    try {
      final plainBytes = await _algorithm.decrypt(secretBox, secretKey: key);
      return utf8.decode(plainBytes);
    } catch (e) {
      throw Exception('Decryption failed — wrong password or corrupted backup');
    }
  }

  /// Backup mnemonic to server, encrypted with password.
  static Future<bool> backupWallet({
    required String email,
    required String password,
    required String mnemonic,
    String address = '',
  }) async {
    try {
      final enc = await _encrypt(mnemonic, password);

      final res = await http.post(
        Uri.parse(_relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'action': 'wallet-backup',
          'email': email.trim().toLowerCase(),
          'ciphertext': enc['ciphertext'],
          'salt': enc['salt'],
          'iv': enc['iv'],
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

      // Response shape: {"ok": true, "data": {"backup": {...}}}
      final payload = data['data'] as Map<String, dynamic>?;
      final backup = payload?['backup'] as Map<String, dynamic>?;
      if (backup == null) {
        throw Exception('Malformed server response — no backup data');
      }

      final ciphertext = backup['ciphertext'] as String? ?? '';
      final salt = backup['salt'] as String? ?? '';
      final iv = backup['iv'] as String? ?? '';

      if (ciphertext.isEmpty || salt.isEmpty || iv.isEmpty) {
        throw Exception(
          'This backup was created in an old, incompatible format. '
          'Please create a new backup from Settings > Backup to Email.',
        );
      }

      final mnemonic = await _decrypt(
        ciphertextB64: ciphertext,
        saltB64: salt,
        ivB64: iv,
        password: password,
      );

      debugPrint('Wallet recovered for $email');
      return mnemonic;
    } catch (e) {
      debugPrint('Recovery error: $e');
      rethrow;
    }
  }
}
