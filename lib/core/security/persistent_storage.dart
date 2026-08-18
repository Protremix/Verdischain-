import 'package:hive/hive.dart';

/// Persistent storage for non-sensitive wallet data.
///
/// Uses Hive (file-based key-value storage) which ALWAYS persists across app
/// kills, unlike flutter_secure_storage which can lose its Keystore-backed
/// encryption key on some Android devices.
///
/// ONLY stores non-sensitive data here:
/// - onboarding complete flag (bool)
/// - wallet address (public string)
/// - biometric enabled flag (bool)
///
/// NEVER store mnemonic, private key, or PIN here.
class PersistentStorage {
  static const _boxName = 'verdis_persistent';
  static Box<dynamic>? _box;

  static Future<Box<dynamic>> _getBox() async {
    if (_box != null && _box!.isOpen) return _box!;
    _box = await Hive.openBox(_boxName);
    return _box!;
  }

  // === Onboarding ===

  static Future<void> setOnboardingComplete(bool value) async {
    final box = await _getBox();
    await box.put('onboarding_complete', value);
  }

  static Future<bool> isOnboardingComplete() async {
    final box = await _getBox();
    return box.get('onboarding_complete', defaultValue: false) as bool;
  }

  // === Wallet Address ===

  static Future<void> setWalletAddress(String address) async {
    final box = await _getBox();
    await box.put('wallet_address', address);
  }

  static Future<String?> getWalletAddress() async {
    final box = await _getBox();
    final value = box.get('wallet_address');
    return value == null ? null : value.toString();
  }

  // === Biometric ===

  static Future<void> setBiometricEnabled(bool value) async {
    final box = await _getBox();
    await box.put('biometric_enabled', value);
  }

  static Future<bool> isBiometricEnabled() async {
    final box = await _getBox();
    return box.get('biometric_enabled', defaultValue: false) as bool;
  }

  // === Clear ===

  static Future<void> clear() async {
    final box = await _getBox();
    await box.clear();
  }
}
