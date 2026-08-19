import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:verdis_wallet/core/storage/hive_helper.dart';

/// Bulletproof persistent storage for non-sensitive wallet data.
///
/// Uses THREE storage layers for maximum reliability:
/// 1. Hive box (primary) — fast key-value DB, persists to disk, survives app kills
/// 2. Plain JSON file (fallback) — custom file in app documents directory
/// 3. In-memory cache (transient) — fast access during session
///
/// ONLY stores non-sensitive data:
/// - onboarding complete flag (bool)
/// - wallet address (public string)
/// - biometric enabled flag (bool)
///
/// NEVER store mnemonic, private key, or PIN here.
class PersistentStorage {
  static const _fileName = 'verdis_wallet_state.json';
  static const _hivePrefix = 'ps_';
  static Map<String, dynamic>? _cache;

  // === Hive keys ===
  static const _keyOnboarding = '${_hivePrefix}onboarding_complete';
  static const _keyWalletAddress = '${_hivePrefix}wallet_address';
  static const _keyBiometric = '${_hivePrefix}biometric_enabled';

  static Future<File> _getFile() async {
    final dir = await getApplicationDocumentsDirectory();
    return File('${dir.path}/$_fileName');
  }

  // === Onboarding ===

  static Future<void> setOnboardingComplete(bool value) async {
    _cache ??= {};
    _cache!['onboarding_complete'] = value;

    // Layer 1: Hive (primary — reliable disk persistence)
    try {
      await HiveHelper.setSetting(_keyOnboarding, value);
    } catch (e) {
      debugPrint('Hive write failed for onboarding: $e');
    }

    // Layer 2: Plain file (fallback)
    try {
      final data = await _readFile();
      data['onboarding_complete'] = value;
      await _writeFile(data);
    } catch (e) {
      debugPrint('File write failed for onboarding: $e');
    }
  }

  static Future<bool> isOnboardingComplete() async {
    // Check cache first
    if (_cache != null && _cache!.containsKey('onboarding_complete')) {
      return _cache!['onboarding_complete'] == true;
    }

    // Layer 1: Hive
    try {
      final value = HiveHelper.getSetting<bool>(_keyOnboarding);
      if (value != null) {
        _cache ??= {};
        _cache!['onboarding_complete'] = value;
        return value;
      }
    } catch (e) {
      debugPrint('Hive read failed for onboarding: $e');
    }

    // Layer 2: Plain file
    try {
      final data = await _readFile();
      if (data.containsKey('onboarding_complete')) {
        final value = data['onboarding_complete'] == true;
        // Migrate to Hive
        try {
          await HiveHelper.setSetting(_keyOnboarding, value);
        } catch (_) {}
        return value;
      }
    } catch (e) {
      debugPrint('File read failed for onboarding: $e');
    }

    return false;
  }

  // === Wallet Address ===

  static Future<void> setWalletAddress(String address) async {
    _cache ??= {};
    _cache!['wallet_address'] = address;

    // Layer 1: Hive
    try {
      await HiveHelper.setSetting(_keyWalletAddress, address);
    } catch (e) {
      debugPrint('Hive write failed for address: $e');
    }

    // Layer 2: Plain file
    try {
      final data = await _readFile();
      data['wallet_address'] = address;
      await _writeFile(data);
    } catch (e) {
      debugPrint('File write failed for address: $e');
    }
  }

  static Future<String?> getWalletAddress() async {
    // Check cache first
    if (_cache != null && _cache!.containsKey('wallet_address')) {
      final addr = _cache!['wallet_address'];
      return addr == null ? null : addr.toString();
    }

    // Layer 1: Hive
    try {
      final value = HiveHelper.getSetting<String>(_keyWalletAddress);
      if (value != null && value.isNotEmpty) {
        _cache ??= {};
        _cache!['wallet_address'] = value;
        return value;
      }
    } catch (e) {
      debugPrint('Hive read failed for address: $e');
    }

    // Layer 2: Plain file
    try {
      final data = await _readFile();
      final addr = data['wallet_address'];
      if (addr != null && addr.toString().isNotEmpty) {
        final addrStr = addr.toString();
        // Migrate to Hive
        try {
          await HiveHelper.setSetting(_keyWalletAddress, addrStr);
        } catch (_) {}
        return addrStr;
      }
    } catch (e) {
      debugPrint('File read failed for address: $e');
    }

    return null;
  }

  // === Biometric ===

  static Future<void> setBiometricEnabled(bool value) async {
    _cache ??= {};
    _cache!['biometric_enabled'] = value;

    // Layer 1: Hive
    try {
      await HiveHelper.setSetting(_keyBiometric, value);
    } catch (e) {
      debugPrint('Hive write failed for biometric: $e');
    }

    // Layer 2: Plain file
    try {
      final data = await _readFile();
      data['biometric_enabled'] = value;
      await _writeFile(data);
    } catch (e) {
      debugPrint('File write failed for biometric: $e');
    }
  }

  static Future<bool> isBiometricEnabled() async {
    // Check cache first
    if (_cache != null && _cache!.containsKey('biometric_enabled')) {
      return _cache!['biometric_enabled'] == true;
    }

    // Layer 1: Hive
    try {
      final value = HiveHelper.getSetting<bool>(_keyBiometric);
      if (value != null) {
        _cache ??= {};
        _cache!['biometric_enabled'] = value;
        return value;
      }
    } catch (e) {
      debugPrint('Hive read failed for biometric: $e');
    }

    // Layer 2: Plain file
    try {
      final data = await _readFile();
      if (data.containsKey('biometric_enabled')) {
        final value = data['biometric_enabled'] == true;
        // Migrate to Hive
        try {
          await HiveHelper.setSetting(_keyBiometric, value);
        } catch (_) {}
        return value;
      }
    } catch (e) {
      debugPrint('File read failed for biometric: $e');
    }

    return false;
  }

  // === Clear ===

  static Future<void> clear() async {
    _cache = {};

    try {
      await HiveHelper.removeSetting(_keyOnboarding);
      await HiveHelper.removeSetting(_keyWalletAddress);
      await HiveHelper.removeSetting(_keyBiometric);
    } catch (_) {}

    try {
      final file = await _getFile();
      if (await file.exists()) {
        await file.delete();
      }
    } catch (_) {}
  }

  // === File helpers ===

  static Future<Map<String, dynamic>> _readFile() async {
    try {
      final file = await _getFile();
      if (await file.exists()) {
        final content = await file.readAsString();
        return jsonDecode(content) as Map<String, dynamic>;
      }
    } catch (_) {}
    return {};
  }

  static Future<void> _writeFile(Map<String, dynamic> data) async {
    try {
      final file = await _getFile();
      await file.writeAsString(jsonEncode(data));
    } catch (_) {}
  }

  // === Debug ===

  static void debugPrint(String msg) {
    // ignore: avoid_print
    print('🔵 PersistentStorage: $msg');
  }
}
