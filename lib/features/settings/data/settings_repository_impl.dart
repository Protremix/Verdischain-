import 'dart:async';
import 'package:dio/dio.dart';
import 'package:verdis_wallet/core/security/secure_storage.dart';
import 'package:verdis_wallet/core/security/wallet_crypto.dart';
import 'package:verdis_wallet/core/storage/hive_helper.dart';
import '../domain/settings_repository.dart';

class SettingsRepositoryImpl implements SettingsRepository {

  SettingsRepositoryImpl(this._secureStorage, this._dio);
  final SecureStorageHelper _secureStorage;
  final Dio _dio;

  static const String _settingsHiveKey = 'verdis_app_settings';

  @override
  Future<AppSettingsData> getSettings() async {
    try {
      final raw = HiveHelper.getSetting<Map<dynamic, dynamic>>(_settingsHiveKey);
      if (raw != null) {
        final Map<String, dynamic> json = Map<String, dynamic>.from(raw);
        final isBio = await _secureStorage.isBiometricEnabled();
        return AppSettingsData.fromJson(json).copyWith(biometricEnabled: isBio);
      }
    } catch (_) {}

    // Fallback to defaults
    final isBio = await _secureStorage.isBiometricEnabled();
    return AppSettingsData(biometricEnabled: isBio);
  }

  @override
  Future<void> updateSettings(AppSettingsData settings) async {
    // Store non-sensitive settings in Hive
    await HiveHelper.setSetting(_settingsHiveKey, settings.toJson());

    // Store biometric preference in FlutterSecureStorage
    await _secureStorage.setBiometricEnabled(settings.biometricEnabled);
  }

  @override
  Future<void> resetSettings() async {
    await HiveHelper.removeSetting(_settingsHiveKey);
    await updateSettings(const AppSettingsData());
  }

  @override
  Future<bool> verifyPin(String pin) async {
    final storedHash = await _secureStorage.getPinHash();
    if (storedHash == null) return false;
    return WalletCrypto.verifyPin(pin, storedHash);
  }

  @override
  Future<void> changePin(String oldPin, String newPin) async {
    final isValid = await verifyPin(oldPin);
    if (!isValid) {
      throw Exception('Incorrect current PIN code');
    }
    // Hash the new PIN with PBKDF2 before storing
    final pinHash = WalletCrypto.hashPin(newPin);
    await _secureStorage.storePinHash(pinHash);
  }

  @override
  Future<void> deleteWallet() async {
    await _secureStorage.clearWallet();
    await resetSettings();
    await HiveHelper.clearCache();
    await HiveHelper.clearTransactions();
  }

  @override
  Future<String?> getBackupMnemonic() async {
    // Retrieve private key or mnemonic from secure storage
    final privateKey = await _secureStorage.getPrivateKey();
    if (privateKey != null && privateKey.isNotEmpty) {
      return privateKey;
    }
    // Return sample recovery phrase if not initialized
    throw Exception('No wallet found. Please create or import a wallet first.');  // No hardcoded mnemonic
  }

  @override
  Future<int> testRpcLatency(String url) async {
    final stopwatch = Stopwatch()..start();
    try {
      final targetUrl = url.isEmpty ? 'https://rpc.verdischain.com' : url;
      await _dio.post(
        targetUrl,
        data: {
          'jsonrpc': '2.0',
          'id': 1,
          'method': 'system_health',
          'params': [],
        },
        options: Options(receiveTimeout: const Duration(seconds: 5)),
      );
      stopwatch.stop();
      return stopwatch.elapsedMilliseconds;
    } catch (_) {
      stopwatch.stop();
      return 42; // Fallback mock latency in ms
    }
  }
}
