import 'dart:convert';
import 'dart:typed_data';
import 'package:verdis_wallet/core/security/blake2b.dart';
import 'package:bip39/bip39.dart' as bip39;
import 'package:hex/hex.dart';
import 'package:polkadart_keyring/polkadart_keyring.dart';
import 'package:verdis_wallet/core/config/network_config.dart';
import 'package:verdis_wallet/core/security/secure_storage.dart';
import '../domain/wallet_repository.dart';

/// SR25519-based wallet repository using polkadart_keyring.
/// Replaces Ed25519 derivation — now matches the web wallet's crypto scheme.
class WalletRepositoryImpl implements WalletRepository {

  WalletRepositoryImpl(this._secureStorage);
  final SecureStorageHelper _secureStorage;

  static const String _mnemonicKey = 'verdis_mnemonic';
  static const int _ss58Format = 909; // Verdis network prefix

  @override
  Future<String> generateMnemonic() async {
    return bip39.generateMnemonic();
  }

  @override
  Future<bool> validateMnemonic(String mnemonic) async {
    final cleaned = mnemonic.trim().replaceAll(RegExp(r'\s+'), ' ');
    if (cleaned.isEmpty) return false;
    final words = cleaned.split(' ');
    if (words.length != 12 && words.length != 24) return false;
    return bip39.validateMnemonic(cleaned);
  }

  @override
  Future<Map<String, String>> deriveKeypair(String mnemonic) async {
    final cleaned = mnemonic.trim().replaceAll(RegExp(r'\s+'), ' ');

    // Derive SR25519 keypair from mnemonic (matches @polkadot/keyring addFromMnemonic)
    final keyPair = KeyPair.sr25519;
    keyPair.ss58Format = _ss58Format;
    await keyPair.fromMnemonic(cleaned);

    final address = keyPair.address;
    final publicKeyBytes = keyPair.publicKey.bytes;
    final publicKeyHex = HEX.encode(publicKeyBytes);

    // For SR25519, the private key is the secret key bytes
    final privateKeyHex = HEX.encode(keyPair.bytes());

    return {
      'mnemonic': cleaned,
      'privateKey': privateKeyHex,
      'publicKey': publicKeyHex,
      'address': address,
    };
  }

  @override
  Future<Map<String, String>> importFromMnemonic(String mnemonic) async {
    final isValid = await validateMnemonic(mnemonic);
    if (!isValid) {
      throw Exception('Invalid seed phrase. Please verify your 12 or 24 words.');
    }
    return deriveKeypair(mnemonic);
  }

  @override
  Future<void> storeWallet({
    required String mnemonic,
    required String privateKey,
    required String publicKey,
    required String address,
  }) async {
    await _secureStorage.storePrivateKey(privateKey);
    await _secureStorage.storePublicKey(publicKey);
    await _secureStorage.write(AppConstants.walletKey, address);
    await _secureStorage.write(_mnemonicKey, mnemonic);
    await _secureStorage.write(AppConstants.onboardingCompleteKey, 'true');
  }

  @override
  Future<Map<String, String>?> loadWallet() async {
    final privateKey = await _secureStorage.getPrivateKey();
    final publicKey = await _secureStorage.getPublicKey();
    final address = await _secureStorage.read(AppConstants.walletKey);
    final mnemonic = await _secureStorage.read(_mnemonicKey);

    if (privateKey == null || address == null) {
      return null;
    }

    return {
      if (mnemonic != null) 'mnemonic': mnemonic,
      'privateKey': privateKey,
      if (publicKey != null) 'publicKey': publicKey,
      'address': address,
    };
  }

  @override
  Future<void> deleteWallet() async {
    await _secureStorage.clearWallet();
    await _secureStorage.delete(_mnemonicKey);
    await _secureStorage.delete(AppConstants.walletKey);
    await _secureStorage.delete(AppConstants.onboardingCompleteKey);
  }

  @override
  Future<String> hashPin(String pin) async {
    // PBKDF2-like: iterate Blake2b with salt to resist brute-force
    final salt = utf8.encode('verdis_pin_salt_2026');
    var input = Uint8List.fromList([...utf8.encode(pin), ...salt]);
    for (var i = 0; i < 10000; i++) {
      input = blake2b256(input);
    }
    return HEX.encode(input);
  }

  @override
  Future<void> savePinHash(String pinHash) async {
    await _secureStorage.storePinHash(pinHash);
  }

  @override
  Future<bool> verifyPin(String pin) async {
    final storedHash = await _secureStorage.getPinHash();
    if (storedHash == null) return false;
    final currentHash = await hashPin(pin);
    return storedHash == currentHash;
  }

  @override
  Future<bool> hasWallet() async {
    return await _secureStorage.hasWallet();
  }

  @override
  Future<void> setBiometricEnabled(bool enabled) async {
    await _secureStorage.setBiometricEnabled(enabled);
  }

  @override
  Future<bool> isBiometricEnabled() async {
    return await _secureStorage.isBiometricEnabled();
  }
}
