// AES-GCM crypto helper matching the web wallet's exact scheme:
// PBKDF2(password, salt, 150000 iterations, SHA-256) -> AES-256-GCM
// Ciphertext format matches Web Crypto API: raw ciphertext + 16-byte GCM tag appended.
import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';
import 'package:cryptography/cryptography.dart';

class WalletCrypto {
  static final Pbkdf2 _pbkdf2 = Pbkdf2(
    macAlgorithm: Hmac.sha256(),
    iterations: 150000,
    bits: 256,
  );

  static final AesGcm _aesGcm = AesGcm.with256bits();

  /// Derive a 256-bit AES key from password + salt (matches web's deriveKeyFromPassword)
  static Future<SecretKey> deriveKey(String password, List<int> salt) async {
    final secretKey = SecretKey(utf8.encode(password));
    return _pbkdf2.deriveKey(secretKey: secretKey, nonce: salt);
  }

  /// Encrypt mnemonic with password (matches web's encryptMnemonic).
  /// Returns {ciphertext, salt, iv} all base64-encoded.
  static Future<Map<String, String>> encryptMnemonic(String mnemonic, String password) async {
    final salt = _randomBytes(16);
    final nonce = _randomBytes(12); // IV
    final key = await deriveKey(password, salt);

    final secretBox = await _aesGcm.encrypt(
      utf8.encode(mnemonic),
      secretKey: key,
      nonce: nonce,
    );

    // Web Crypto's AES-GCM output = ciphertext + 16-byte auth tag appended.
    // Dart's cryptography package returns them separately — concatenate to match.
    final combined = Uint8List.fromList([...secretBox.cipherText, ...secretBox.mac.bytes]);

    return {
      'ciphertext': base64Encode(combined),
      'salt': base64Encode(salt),
      'iv': base64Encode(nonce),
    };
  }

  /// Decrypt mnemonic with password (matches web's decryptMnemonic).
  static Future<String> decryptMnemonic(
    String ciphertextB64,
    String saltB64,
    String ivB64,
    String password,
  ) async {
    final salt = base64Decode(saltB64);
    final nonce = base64Decode(ivB64);
    final combined = base64Decode(ciphertextB64);

    if (combined.length < 16) {
      throw const FormatException('Invalid ciphertext: too short to contain GCM tag');
    }
    final cipherBytes = combined.sublist(0, combined.length - 16);
    final macBytes = combined.sublist(combined.length - 16);

    final key = await deriveKey(password, salt);

    final secretBox = SecretBox(
      cipherBytes,
      nonce: nonce,
      mac: Mac(macBytes),
    );

    final decrypted = await _aesGcm.decrypt(secretBox, secretKey: key);
    return utf8.decode(decrypted);
  }

  static final Random _secureRandom = Random.secure();

  static List<int> _randomBytes(int length) {
    return List<int>.generate(length, (_) => _secureRandom.nextInt(256));
  }
}
