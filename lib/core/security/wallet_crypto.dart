import 'dart:convert';
import 'dart:typed_data';
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

  static String hashPin(String pin) {
    final bytes = utf8.encode(pin);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  static bool verifyPin(String pin, String hash) {
    return hashPin(pin) == hash;
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
