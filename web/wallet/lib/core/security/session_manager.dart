import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/network_config.dart';

final sessionManagerProvider = Provider<SessionManager>((ref) {
  return SessionManager();
});

/// Manages app session lifecycle, auto-lock, and timeout
class SessionManager {
  Timer? _sessionTimer;
  Timer? _autoLockTimer;
  bool _isLocked = false;
  DateTime? _lastActivity;
  bool _isClipboardProtected = false;

  bool get isLocked => _isLocked;
  DateTime? get lastActivity => _lastActivity;
  bool get isClipboardProtected => _isClipboardProtected;

  /// Start session tracking
  void startSession({required VoidCallback onTimeout, required VoidCallback onAutoLock}) {
    _lastActivity = DateTime.now();
    _isLocked = false;

    _sessionTimer?.cancel();
    _autoLockTimer?.cancel();

    // Session timeout (5 minutes)
    _sessionTimer = Timer.periodic(
      const Duration(minutes: AppConstants.sessionTimeoutMinutes),
      (_) {
        onTimeout();
      },
    );

    // Auto-lock (1 minute of inactivity)
    _autoLockTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) {
        if (_lastActivity != null) {
          final idle = DateTime.now().difference(_lastActivity!);
          if (idle.inMinutes >= AppConstants.autoLockMinutes) {
            _isLocked = true;
            onAutoLock();
          }
        }
      },
    );
  }

  /// Record user activity
  void recordActivity() {
    _lastActivity = DateTime.now();
  }

  /// Lock the session
  void lock() {
    _isLocked = true;
    _sessionTimer?.cancel();
    _autoLockTimer?.cancel();
  }

  /// Unlock the session
  void unlock() {
    _isLocked = false;
    _lastActivity = DateTime.now();
  }

  /// End session
  void endSession() {
    _sessionTimer?.cancel();
    _autoLockTimer?.cancel();
    _isLocked = true;
    _lastActivity = null;
  }

  /// Enable clipboard protection (auto-clear after 30 seconds)
  void enableClipboardProtection(Timer Function(Function, Duration) timerFactory) {
    _isClipboardProtected = true;
    timerFactory((_) {
      _isClipboardProtected = false;
    }, const Duration(seconds: AppConstants.clipboardClearSeconds),);
  }

  /// Check device integrity (placeholder for platform-specific checks)
  Future<bool> checkDeviceIntegrity() async {
    // Platform-specific integrity checks would go here
    // Android: Play Integrity API
    // iOS: DeviceCheck
    return true;
  }
}

typedef VoidCallback = void Function();
