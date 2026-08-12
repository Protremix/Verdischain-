import 'dart:convert';
import 'dart:typed_data';
import 'dart:math' show Random;
import 'package:crypto/crypto.dart';
import 'package:bip39/bip39.dart' as bip39;
import 'package:hex/hex.dart';
import 'package:bs58/bs58.dart';
import 'package:verdis_wallet/core/security/blake2b.dart';

class WalletCrypto {
  WalletCrypto._();

  static String generateMnemonic() {
    return bip39.generateMnemonic(strength: 128);
  }

  static String generateMnemonic24() {
    return bip39.generateMnemonic(strength: 256);
  }

  static bool validateMnemonic(String mnemonic) {
    return bip39.validateMnemonic(mnemonic.trim().toLowerCase());
  }

  static Uint8List mnemonicToSeed(String mnemonic) {
    return bip39.mnemonicToSeed(mnemonic.trim().toLowerCase());
  }

  /// PBKDF2 with HMAC-SHA256: 100,000 iterations, 32-byte key, random salt.
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
  }

  static String ss58Address(Uint8List publicKey) {
    const int networkId = 909;
    final prefix = _encodeNetworkId(networkId);
    final input = Uint8List.fromList([...prefix, ...publicKey]);
    // Substrate SS58 uses Blake2b-256 for checksums (NOT SHA-256)
    final hash1 = blake2b256(input);
    final hash2 = blake2b256(hash1);
    final checksum = hash2.sublist(0, 2);
    final address = Uint8List.fromList([...prefix, ...publicKey, ...checksum]);
    return base58.encode(address);
  }

  static Uint8List _encodeNetworkId(int id) {
    if (id < 64) {
      return Uint8List.fromList([id]);
    } else {
      // Correct SS58 multi-byte encoding for prefix >= 64
      final first = 0xC0 | ((id >> 8) & 0x3F);
      final second = id & 0xFF;
      return Uint8List.fromList([first, second]);
    }
  }

  static Uint8List hexToBytes(String hex) {
    return Uint8List.fromList(HEX.decode(hex));
  }

  static String bytesToHex(Uint8List bytes) {
    return HEX.encode(bytes);
  }

  static String shortenAddress(String address, {int prefix = 6, int suffix = 6}) {
    if (address.length <= prefix + suffix + 3) return address;
    return '${address.substring(0, prefix)}...${address.substring(address.length - suffix)}';
  }
}

class Keypair {
  Keypair({required this.privateKey, required this.publicKey});
  final Uint8List privateKey;
  final Uint8List publicKey;
  String get publicKeyHex => WalletCrypto.bytesToHex(publicKey);
  String get privateKeyHex => WalletCrypto.bytesToHex(privateKey);
  String get address => WalletCrypto.ss58Address(publicKey);
}
