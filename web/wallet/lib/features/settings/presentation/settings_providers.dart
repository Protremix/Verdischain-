import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/config/network_config.dart';
import 'package:verdis_wallet/core/storage/hive_helper.dart';

/// Settings state
class SettingsState {

  const SettingsState({
    this.biometricEnabled = false,
    this.clipboardProtection = true,
    this.autoLockMinutes = 1,
    this.sessionTimeoutMinutes = 5,
    this.rpcEndpoint = NetworkConfig.rpcUrl,
    this.themeMode = ThemeMode.dark,
  });
  final bool biometricEnabled;
  final bool clipboardProtection;
  final int autoLockMinutes;
  final int sessionTimeoutMinutes;
  final String rpcEndpoint;
  final ThemeMode themeMode;

  SettingsState copyWith({
    bool? biometricEnabled,
    bool? clipboardProtection,
    int? autoLockMinutes,
    int? sessionTimeoutMinutes,
    String? rpcEndpoint,
    ThemeMode? themeMode,
  }) {
    return SettingsState(
      biometricEnabled: biometricEnabled ?? this.biometricEnabled,
      clipboardProtection: clipboardProtection ?? this.clipboardProtection,
      autoLockMinutes: autoLockMinutes ?? this.autoLockMinutes,
      sessionTimeoutMinutes: sessionTimeoutMinutes ?? this.sessionTimeoutMinutes,
      rpcEndpoint: rpcEndpoint ?? this.rpcEndpoint,
      themeMode: themeMode ?? this.themeMode,
    );
  }
}

/// Settings provider
final settingsProvider = StateNotifierProvider<SettingsNotifier, SettingsState>((ref) {
  return SettingsNotifier();
});

class SettingsNotifier extends StateNotifier<SettingsState> {

  SettingsNotifier() : super(const SettingsState()) {
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final bio = HiveHelper.getSetting<bool>('biometric_enabled') ?? false;
    final clipboard = HiveHelper.getSetting<bool>('clipboard_protection') ?? true;
    final autoLock = HiveHelper.getSetting<int>('auto_lock_minutes') ?? 1;
    final sessionTimeout = HiveHelper.getSetting<int>('session_timeout_minutes') ?? 5;
    final endpoint = HiveHelper.getSetting<String>('rpc_endpoint') ?? NetworkConfig.rpcUrl;

    state = SettingsState(
      biometricEnabled: bio,
      clipboardProtection: clipboard,
      autoLockMinutes: autoLock,
      sessionTimeoutMinutes: sessionTimeout,
      rpcEndpoint: endpoint,
    );
  }

  Future<void> setBiometric(bool enabled) async {
    await HiveHelper.setSetting('biometric_enabled', enabled);
    state = state.copyWith(biometricEnabled: enabled);
  }

  Future<void> setClipboardProtection(bool enabled) async {
    await HiveHelper.setSetting('clipboard_protection', enabled);
    state = state.copyWith(clipboardProtection: enabled);
  }

  Future<void> setAutoLockMinutes(int minutes) async {
    await HiveHelper.setSetting('auto_lock_minutes', minutes);
    state = state.copyWith(autoLockMinutes: minutes);
  }

  Future<void> setSessionTimeoutMinutes(int minutes) async {
    await HiveHelper.setSetting('session_timeout_minutes', minutes);
    state = state.copyWith(sessionTimeoutMinutes: minutes);
  }

  Future<void> setRpcEndpoint(String endpoint) async {
    await HiveHelper.setSetting('rpc_endpoint', endpoint);
    state = state.copyWith(rpcEndpoint: endpoint);
  }

  Future<void> resetSettings() async {
    await HiveHelper.settings.clear();
    state = const SettingsState();
  }
}

/// Network endpoint provider
final networkEndpointProvider = StateProvider<String>((ref) {
  return NetworkConfig.rpcUrl;
});
