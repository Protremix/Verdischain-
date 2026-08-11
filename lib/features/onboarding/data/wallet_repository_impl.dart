import 'dart:convert';
import 'dart:typed_data';
import 'package:bip39/bip39.dart' as bip39;
import 'package:crypto/crypto.dart';
import 'package:ed25519_hd_key/ed25519_hd_key.dart';
import 'package:hex/hex.dart';
import 'package:verdis_wallet/core/config/network_config.dart';
import 'package:verdis_wallet/core/security/secure_storage.dart';
import 'package:verdis_wallet/core/security/wallet_crypto.dart';
import '../domain/wallet_repository.dart';

/// Implementation of WalletRepository using bip39, ed25519_hd_key, crypto, and FlutterSecureStorage
class WalletRepositoryImpl implements WalletRepository {

  WalletRepositoryImpl(this._secureStorage);
  final SecureStorageHelper _secureStorage;

  static const String _mnemonicKey = 'verdis_mnemonic';

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
    final seed = bip39.mnemonicToSeed(cleaned);

    // Derive Ed25519 HD keypair for Verdis coin type (909)
    final keyData = await ED25519_HD_KEY.derivePath("m/44'/909'/0'/0/0", seed);
    final privateKeyHex = HEX.encode(keyData.key);

    // Derive the proper Ed25519 public key (32 bytes) from the private key
    final publicKeyBytes = await ED25519_HD_KEY.getPublicKey(keyData.key, false);
    final publicKeyHex = HEX.encode(publicKeyBytes);

    // Generate proper SS58 address with network prefix 909
    final publicKeyUint8 = Uint8List.fromList(publicKeyBytes);
    final address = WalletCrypto.ss58Address(publicKeyUint8);

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
    final bytes = utf8.encode('${pin}_verdis_salt_2026');
    final digest = sha256.convert(bytes);
    return digest.toString();
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
