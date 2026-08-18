import 'package:flutter/services.dart';

/// Platform-level security service for native security controls.
/// Handles screenshot prevention and root detection on Android.
class PlatformSecurityService {
  static const _channel = MethodChannel('com.verdis.wallet/security');

  /// Enable or disable screenshot prevention (FLAG_SECURE on Android).
  /// When enabled, the app content is hidden from the recents screen
  /// and blocks screenshots/screen recording.
  static Future<void> setSecureFlag({bool enabled = true}) async {
    try {
      await _channel.invokeMethod('setSecureFlag', {'enabled': enabled});
    } on PlatformException {
      // Silently fail on platforms that don't support it (iOS, web)
    }
  }

  /// Check if the device is rooted/jailbroken.
  /// Returns true if root indicators are found.
  static Future<bool> isDeviceRooted() async {
    try {
      final result = await _channel.invokeMethod<bool>('isDeviceRooted');
      return result ?? false;
    } on PlatformException {
      return false;
    }
  }
}
