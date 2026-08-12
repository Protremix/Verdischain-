import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final secureStorageProvider = Provider<SecureStorageHelper>((ref) {
  return SecureStorageHelper();
});

class SecureStorageHelper {

  SecureStorageHelper() : _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );
  final FlutterSecureStorage _storage;

  Future<void> storeMnemonic(String mnemonic) async {
    await _storage.write(key: 'wallet_mnemonic', value: mnemonic);
  }

  Future<String?> getMnemonic() async {
    return await _storage.read(key: 'wallet_mnemonic');
  }

  Future<void> storePrivateKey(String privateKey) async {
    await _storage.write(key: 'wallet_private_key', value: privateKey);
  }

  Future<String?> getPrivateKey() async {
    return await _storage.read(key: 'wallet_private_key');
  }

  Future<void> storePublicKey(String publicKey) async {
    await _storage.write(key: 'wallet_public_key', value: publicKey);
  }

  Future<String?> getPublicKey() async {
    return await _storage.read(key: 'wallet_public_key');
  }

  Future<void> storePinHash(String pinHash) async {
    await _storage.write(key: 'wallet_pin_hash', value: pinHash);
  }

  Future<String?> getPinHash() async {
    return await _storage.read(key: 'wallet_pin_hash');
  }

  Future<void> setBiometricEnabled(bool enabled) async {
    await _storage.write(key: 'biometric_enabled', value: enabled.toString());
  }

  Future<bool> isBiometricEnabled() async {
    final value = await _storage.read(key: 'biometric_enabled');
    return value == 'true';
  }

  // Email recovery
  Future<String?> getRecoveryEmail() async {
    return await _storage.read(key: 'recovery_email');
  }

  Future<void> setRecoveryEmail(String email) async {
    await _storage.write(key: 'recovery_email', value: email);
  }

  // Wallet address (stored during wallet creation)
  Future<String?> getWalletAddress() async {
    return await _storage.read(key: 'verdis_wallet_address') ??
        await _storage.read(key: 'wallet_address');
  }

  Future<void> storeWalletAddress(String address) async {
    await _storage.write(key: 'verdis_wallet_address', value: address);
  }

  Future<bool> hasWallet() async {
    // Check multiple key variants for backward compatibility
    final mnemonic = await getMnemonic();
    final storedMnemonic = await read('verdis_mnemonic');
    final walletAddress = await read('verdis_wallet_address');
    final walletKey = await read('verdis_wallet');
    final onboarding = await read('verdis_onboarding');
    return (mnemonic != null && mnemonic.isNotEmpty) ||
           (storedMnemonic != null && storedMnemonic.isNotEmpty) ||
           (walletAddress != null && walletAddress.isNotEmpty) ||
           (walletKey != null && walletKey.isNotEmpty) ||
           (onboarding == 'true');
  }

  Future<void> clearWallet() async {
    await _storage.delete(key: 'wallet_mnemonic');
    await _storage.delete(key: 'wallet_private_key');
    await _storage.delete(key: 'wallet_public_key');
    await _storage.delete(key: 'wallet_pin_hash');
    await _storage.delete(key: 'biometric_enabled');
    await _storage.delete(key: 'recovery_email');
  }

  Future<void> write(String key, String value) async {
    await _storage.write(key: key, value: value);
  }

  Future<String?> read(String key) async {
    return await _storage.read(key: key);
  }

  Future<void> delete(String key) async {
    await _storage.delete(key: key);
  }
}
