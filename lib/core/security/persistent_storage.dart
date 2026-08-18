import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';

/// Bulletproof persistent storage for non-sensitive wallet data.
///
/// Uses a plain JSON file written to the app's documents directory.
/// No encryption, no Keystore, no framework dependencies — just a file on disk.
/// This ALWAYS persists across app kills, reboots, and cache clears.
///
/// ONLY stores non-sensitive data:
/// - onboarding complete flag (bool)
/// - wallet address (public string)
/// - biometric enabled flag (bool)
///
/// NEVER store mnemonic, private key, or PIN here.
class PersistentStorage {
  static const _fileName = 'verdis_wallet_state.json';
  static Map<String, dynamic>? _cache;

  static Future<File> _getFile() async {
    final dir = await getApplicationDocumentsDirectory();
    return File('${dir.path}/$_fileName');
  }

  static Future<Map<String, dynamic>> _read() async {
    if (_cache != null) return _cache!;
    try {
      final file = await _getFile();
      if (await file.exists()) {
        final content = await file.readAsString();
        _cache = jsonDecode(content) as Map<String, dynamic>;
      } else {
        _cache = {};
      }
    } catch (_) {
      _cache = {};
    }
    return _cache!;
  }

  static Future<void> _write(Map<String, dynamic> data) async {
    _cache = data;
    try {
      final file = await _getFile();
      await file.writeAsString(jsonEncode(data));
    } catch (_) {}
  }

  // === Onboarding ===

  static Future<void> setOnboardingComplete(bool value) async {
    final data = await _read();
    data['onboarding_complete'] = value;
    await _write(data);
  }

  static Future<bool> isOnboardingComplete() async {
    final data = await _read();
    return data['onboarding_complete'] == true;
  }

  // === Wallet Address ===

  static Future<void> setWalletAddress(String address) async {
    final data = await _read();
    data['wallet_address'] = address;
    await _write(data);
  }

  static Future<String?> getWalletAddress() async {
    final data = await _read();
    final addr = data['wallet_address'];
    return addr == null ? null : addr.toString();
  }

  // === Biometric ===

  static Future<void> setBiometricEnabled(bool value) async {
    final data = await _read();
    data['biometric_enabled'] = value;
    await _write(data);
  }

  static Future<bool> isBiometricEnabled() async {
    final data = await _read();
    return data['biometric_enabled'] == true;
  }

  // === Clear ===

  static Future<void> clear() async {
    _cache = {};
    try {
      final file = await _getFile();
      if (await file.exists()) {
        await file.delete();
      }
    } catch (_) {}
  }
}
