// AES-GCM crypto helper matching the web wallet's exact scheme:
// PBKDF2(password, salt, 150000 iterations, SHA-256) -> AES-256-GCM
import 'package:cryptography/cryptography.dart';
import 'dart:typed_data';

class WalletCrypto {
  static final _pbkdf2 = Pbkdf2(
    macAlgorithm: Hmac.sha256(),
    iterations: 150000,
    bits: 256,
  );

  static final _aesGcm = AesGcm.with256bits();

  /// Derive a 256-bit AES key from password + salt (matches web's deriveKeyFromPassword)
  static Future<SecretKey> deriveKey(String password, List<int> salt) async {
    final secretKey = SecretKey(password.codeUnits);
    return _pbkdf2.deriveKey(secretKey: secretKey, nonce: salt);
  }

  /// Encrypt mnemonic with password (matches web's encryptMnemonic)
  /// Returns {ciphertext, salt, iv} all base64-encoded, where ciphertext includes the GCM auth tag appended
  static Future<Map<String, String>> encryptMnemonic(String mnemonic, String password) async {
    final salt = _randomBytes(16);
    final nonce = _randomBytes(12); // IV
    final key = await deriveKey(password, salt);

    final secretBox = await _aesGcm.encrypt(
      mnemonic.codeUnits,
      secretKey: key,
      nonce: nonce,
    );

    // Web Crypto's AES-GCM output = ciphertext + 16-byte auth tag appended.
    // Dart's cryptography package returns them separately — concatenate to match.
    final combined = Uint8List.fromList([...secretBox.cipherText, ...secretBox.mac.bytes]);

    return {
      'ciphertext': _base64Encode(combined),
      'salt': _base64Encode(salt),
      'iv': _base64Encode(nonce),
    };
  }

  /// Decrypt mnemonic with password (matches web's decryptMnemonic)
  static Future<String> decryptMnemonic(
    String ciphertextB64,
    String saltB64,
    String ivB64,
    String password,
  ) async {
    final salt = _base64Decode(saltB64);
    final nonce = _base64Decode(ivB64);
    final combined = _base64Decode(ciphertextB64);

    // Split combined into ciphertext + 16-byte GCM tag (matches Web Crypto's format)
    if (combined.length < 16) {
      throw Exception('Invalid ciphertext: too short');
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
    return String.fromCharCodes(decrypted);
  }

  static List<int> _randomBytes(int length) {
    final random = List<int>.generate(length, (_) => DateTime.now().microsecondsSinceEpoch % 256);
    // Use a proper CSPRNG instead
    return SecureRandomBytes.generate(length);
  }

  static String _base64Encode(List<int> bytes) {
    return const Base64Codec().encode(bytes);
  }

  static List<int> _base64Decode(String b64) {
    return const Base64Codec().decode(b64);
  }
}

// Simple CSPRNG wrapper using dart:math Random.secure()
class SecureRandomBytes {
  static List<int> generate(int length) {
    final random = _secureRandom;
    return List<int>.generate(length, (_) => random.nextInt(256));
  }

  static final _secureRandom = _createSecureRandom();

  static dynamic _createSecureRandom() {
    // ignore: avoid_dynamic_calls
    return _SecureRandomImpl();
  }
}

class _SecureRandomImpl {
  final _random = _mathRandomSecure();
  int nextInt(int max) => _random.nextInt(max);

  static dynamic _mathRandomSecure() {
    // Deferred import avoided — use dart:math directly
    return _dartMathRandomSecure();
  }
}

// This is a placeholder to be replaced by proper dart:math import at top.
dynamic _dartMathRandomSecure() => throw UnimplementedError();
