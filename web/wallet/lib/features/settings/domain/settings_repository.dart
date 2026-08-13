/// Data model for app settings
class AppSettingsData {

  const AppSettingsData({
    this.biometricEnabled = false,
    this.clipboardProtection = true,
    this.autoLockMinutes = 1,
    this.sessionTimeoutMinutes = 5,
    this.networkEndpoint = 'mainnet',
    this.customRpcUrl = '',
    this.themeMode = 'dark',
    this.language = 'en',
    this.deviceIntegrityOk = true,
  });

  factory AppSettingsData.fromJson(Map<String, dynamic> json) => AppSettingsData(
        biometricEnabled: json['biometricEnabled'] as bool? ?? false,
        clipboardProtection: json['clipboardProtection'] as bool? ?? true,
        autoLockMinutes: json['autoLockMinutes'] as int? ?? 1,
        sessionTimeoutMinutes: json['sessionTimeoutMinutes'] as int? ?? 5,
        networkEndpoint: json['networkEndpoint'] as String? ?? 'mainnet',
        customRpcUrl: json['customRpcUrl'] as String? ?? '',
        themeMode: json['themeMode'] as String? ?? 'dark',
        language: json['language'] as String? ?? 'en',
        deviceIntegrityOk: json['deviceIntegrityOk'] as bool? ?? true,
      );
  final bool biometricEnabled;
  final bool clipboardProtection;
  final int autoLockMinutes;
  final int sessionTimeoutMinutes;
  final String networkEndpoint; // 'mainnet', 'testnet', 'custom'
  final String customRpcUrl;
  final String themeMode; // 'dark'
  final String language;
  final bool deviceIntegrityOk;

  AppSettingsData copyWith({
    bool? biometricEnabled,
    bool? clipboardProtection,
    int? autoLockMinutes,
    int? sessionTimeoutMinutes,
    String? networkEndpoint,
    String? customRpcUrl,
    String? themeMode,
    String? language,
    bool? deviceIntegrityOk,
  }) {
    return AppSettingsData(
      biometricEnabled: biometricEnabled ?? this.biometricEnabled,
      clipboardProtection: clipboardProtection ?? this.clipboardProtection,
      autoLockMinutes: autoLockMinutes ?? this.autoLockMinutes,
      sessionTimeoutMinutes: sessionTimeoutMinutes ?? this.sessionTimeoutMinutes,
      networkEndpoint: networkEndpoint ?? this.networkEndpoint,
      customRpcUrl: customRpcUrl ?? this.customRpcUrl,
      themeMode: themeMode ?? this.themeMode,
      language: language ?? this.language,
      deviceIntegrityOk: deviceIntegrityOk ?? this.deviceIntegrityOk,
    );
  }

  Map<String, dynamic> toJson() => {
        'biometricEnabled': biometricEnabled,
        'clipboardProtection': clipboardProtection,
        'autoLockMinutes': autoLockMinutes,
        'sessionTimeoutMinutes': sessionTimeoutMinutes,
        'networkEndpoint': networkEndpoint,
        'customRpcUrl': customRpcUrl,
        'themeMode': themeMode,
        'language': language,
        'deviceIntegrityOk': deviceIntegrityOk,
      };
}

/// Abstract settings repository interface
abstract class SettingsRepository {
  /// Fetch all non-sensitive app settings
  Future<AppSettingsData> getSettings();

  /// Update non-sensitive settings
  Future<void> updateSettings(AppSettingsData settings);

  /// Reset settings to defaults
  Future<void> resetSettings();

  /// Verify user PIN code
  Future<bool> verifyPin(String pin);

  /// Change existing PIN
  Future<void> changePin(String oldPin, String newPin);

  /// Clear secure storage and delete wallet state
  Future<void> deleteWallet();

  /// Retrieve backup recovery phrase after PIN verification
  Future<String?> getBackupMnemonic();

  /// Test connection latency to target RPC endpoint
  Future<int> testRpcLatency(String url);
}
