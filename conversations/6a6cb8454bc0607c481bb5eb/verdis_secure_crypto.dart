import "dart:convert";
import "dart:math";
import "dart:typed_data";
import "package:crypto/crypto.dart";

/// Secure crypto utilities for the Verdis wallet.
/// Uses PBKDF2-HMAC-SHA256 for key derivation and HMAC-CTR for encryption.
/// This is a pragmatic solution using only the `crypto` package.

class SecureCrypto {
  static const int _pbkdf2Iterations = 100000;
  static const int _saltLength = 32;
  static const int _keyLength = 32;
  static const int _hmacBlockSize = 32;

  /// Generate a cryptographically random salt
  static List<int> generateSalt() {
    final random = Random.secure();
    return List<int>.generate(_saltLength, (_) => random.nextInt(256));
  }

  /// PBKDF2 key derivation using HMAC-SHA256
  static List<int> _pbkdf2(String password, List<int> salt, int iterations, int keyLength) {
    final hmac = Hmac(sha256, utf8.encode(password));
    final blockCount = (keyLength / _hmacBlockSize).ceil();
    var result = <int>[];

    for (var blockNum = 1; blockNum <= blockCount; blockNum++) {
      // Encode block number as 4 bytes big-endian
      final blockBytes = ByteData(4)..setUint32(0, blockNum);
      final blockNumList = blockBytes.buffer.asUint8List().toList();

      // U1 = HMAC(password, salt + block_num)
      var u = hmac.convert(salt + blockNumList).bytes;
      var t = List<int>.from(u);

      // U2..Uc
      for (var i = 1; i < iterations; i++) {
        u = hmac.convert(u).bytes;
        for (var j = 0; j < _hmacBlockSize; j++) {
          t[j] ^= u[j];
        }
      }

      result.addAll(t);
    }

    return result.sublist(0, keyLength);
  }

  /// Encrypt plaintext using PBKDF2-derived key + HMAC-CTR stream cipher
  /// Returns a self-contained encrypted blob: version(1) + salt(32) + ciphertext + hmac(32)
  static String encrypt(String plaintext, String password) {
    final salt = generateSalt();
    final key = _pbkdf2(password, salt, _pbkdf2Iterations, _keyLength * 2);
    final encKey = key.sublist(0, _keyLength);
    final macKey = key.sublist(_keyLength);

    final plaintextBytes = utf8.encode(plaintext);
    final ciphertext = <int>[];

    // HMAC-CTR stream cipher
    final hmac = Hmac(sha256, encKey);
    var counter = 0;
    for (var i = 0; i < plaintextBytes.length; i += _hmacBlockSize) {
      final counterBytes = ByteData(8)..setUint64(0, counter);
      final keystream = hmac.convert(counterBytes.buffer.asUint8List().toList()).bytes;

      final end = (i + _hmacBlockSize < plaintextBytes.length)
          ? i + _hmacBlockSize
          : plaintextBytes.length;
      for (var j = i; j < end; j++) {
        ciphertext.add(plaintextBytes[j] ^ keystream[j - i]);
      }
      counter++;
    }

    // HMAC for authentication
    final macHmac = Hmac(sha256, macKey);
    final mac = macHmac.convert(ciphertext).bytes;

    // Version byte (0x01) + salt + ciphertext + mac
    final blob = <int>[0x01] + salt + ciphertext + mac;
    return base64.encode(blob);
  }

  /// Decrypt an encrypted blob. Returns null if decryption fails (wrong password, tampered data).
  static String? decrypt(String encryptedBlob, String password) {
    try {
      final blob = base64.decode(encryptedBlob);
      if (blob.isEmpty || blob[0] != 0x01) return null;

      final salt = blob.sublist(1, 1 + _saltLength);
      final mac = blob.sublist(blob.length - _hmacBlockSize);
      final ciphertext = blob.sublist(1 + _saltLength, blob.length - _hmacBlockSize);

      final key = _pbkdf2(password, salt, _pbkdf2Iterations, _keyLength * 2);
      final encKey = key.sublist(0, _keyLength);
      final macKey = key.sublist(_keyLength);

      // Verify HMAC first (authenticate before decrypt)
      final macHmac = Hmac(sha256, macKey);
      final computedMac = macHmac.convert(ciphertext).bytes;

      // Constant-time comparison
      var valid = true;
      for (var i = 0; i < _hmacBlockSize; i++) {
        if (computedMac[i] != mac[i]) valid = false;
      }
      if (!valid) return null;

      // Decrypt
      final hmac = Hmac(sha256, encKey);
      final plaintext = <int>[];
      var counter = 0;
      for (var i = 0; i < ciphertext.length; i += _hmacBlockSize) {
        final counterBytes = ByteData(8)..setUint64(0, counter);
        final keystream = hmac.convert(counterBytes.buffer.asUint8List().toList()).bytes;

        final end = (i + _hmacBlockSize < ciphertext.length)
            ? i + _hmacBlockSize
            : ciphertext.length;
        for (var j = i; j < end; j++) {
          plaintext.add(ciphertext[j] ^ keystream[j - i]);
        }
        counter++;
      }

      return utf8.decode(plaintext);
    } catch (_) {
      return null;
    }
  }

  /// Hash a PIN with a random salt using PBKDF2
  /// Returns "iterations:saltBase64:hashBase64"
  static String hashPin(String pin, {List<int>? salt}) {
    final s = salt ?? generateSalt();
    final hash = _pbkdf2(pin, s, _pbkdf2Iterations, _keyLength);
    return "$_pbkdf2Iterations:${base64.encode(s)}:${base64.encode(hash)}";
  }

  /// Verify a PIN against a stored hash
  static bool verifyPin(String pin, String stored) {
    try {
      final parts = stored.split(":");
      if (parts.length != 3) return false;
      final iterations = int.parse(parts[0]);
      final salt = base64.decode(parts[1]);
      final storedHash = base64.decode(parts[2]);

      final hash = _pbkdf2(pin, salt, iterations, _keyLength);

      // Constant-time comparison
      var valid = true;
      for (var i = 0; i < storedHash.length; i++) {
        if (i < hash.length && hash[i] != storedHash[i]) valid = false;
      }
      return valid;
    } catch (_) {
      return false;
    }
  }

  /// Validate a Verdis SS58 address (basic format check)
  static bool isValidAddress(String address) {
    if (address.isEmpty) return false;

    // SS58 format: prefix + public key + checksum, base58 encoded
    // Verdis uses prefix 909, addresses start with specific chars
    // Basic validation: length 10-50, alphanumeric, no special chars
    if (address.length < 10 || address.length > 50) return false;

    // Check for valid base58 characters (no 0, O, I, l)
    final validChars = RegExp(r"^[1-9A-HJ-NP-Za-km-z]+$");
    if (!validChars.hasMatch(address)) return false;

    return true;
  }
}
