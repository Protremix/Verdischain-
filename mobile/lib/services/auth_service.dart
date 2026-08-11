import "dart:async";
import "dart:convert";
import "dart:io";
import "package:flutter/foundation.dart";
import "package:path_provider/path_provider.dart";
import "secure_crypto.dart";

class AuthService extends ChangeNotifier {
  static const String _pinKey = "verdis_wallet_pin_hash_v2";
  static const String _biometricKey = "verdis_wallet_biometric_enabled";
  static const int _inactivityTimeoutSeconds = 60;
  static const int _maxPinAttempts = 5;

  bool _isLocked = true;
  bool _hasPinSet = false;
  bool _biometricEnabled = false;
  int _pinAttempts = 0;
  Timer? _inactivityTimer;

  bool get isLocked => _isLocked;
  bool get hasPinSet => _hasPinSet;
  bool get biometricEnabled => _biometricEnabled;
  bool get isPinLocked => _pinAttempts >= _maxPinAttempts;
  int get remainingAttempts => _maxPinAttempts - _pinAttempts;

  AuthService() {
    _initAuth();
  }

  Future<File> _getPrefsFile() async {
    final dir = await getApplicationDocumentsDirectory();
    return File("${dir.path}/verdis_prefs.json");
  }

  Future<Map<String, dynamic>> _readPrefs() async {
    try {
      final file = await _getPrefsFile();
      if (await file.exists()) {
        return jsonDecode(await file.readAsString());
      }
    } catch (e) {
      debugPrint("Error reading prefs: $e");
    }
    return {};
  }

  Future<void> _writePrefs(Map<String, dynamic> prefs) async {
    try {
      final file = await _getPrefsFile();
      await file.writeAsString(jsonEncode(prefs));
    } catch (e) {
      debugPrint("Error writing prefs: $e");
    }
  }

  Future<void> _initAuth() async {
    try {
      final prefs = await _readPrefs();
      final pinHash = prefs[_pinKey];
      _hasPinSet = pinHash != null && pinHash.toString().isNotEmpty;
      _biometricEnabled = prefs[_biometricKey] ?? false;
      // Check for old v1 PIN hash and migrate
      if (!_hasPinSet && prefs["verdis_wallet_pin_hash"] != null) {
        _hasPinSet = true;
      }
      if (!_hasPinSet) {
        _isLocked = false;
      }
      notifyListeners();
    } catch (e) {
      debugPrint("Auth initialization error: $e");
    }
  }

  Future<bool> setPin(String pin) async {
    if (pin.length != 6) return false;
    try {
      final prefs = await _readPrefs();
      // Use PBKDF2 with random salt (100k iterations)
      final hashed = SecureCrypto.hashPin(pin);
      prefs[_pinKey] = hashed;
      // Remove old v1 hash if present
      prefs.remove("verdis_wallet_pin_hash");
      await _writePrefs(prefs);
      _hasPinSet = true;
      _isLocked = false;
      _pinAttempts = 0;
      resetInactivityTimer();
      notifyListeners();
      return true;
    } catch (e) {
      debugPrint("Error setting PIN: $e");
      return false;
    }
  }

  Future<bool> verifyPin(String pin) async {
    if (_pinAttempts >= _maxPinAttempts) return false;
    try {
      final prefs = await _readPrefs();
      final storedHash = prefs[_pinKey];
      if (storedHash == null) return false;

      final isValid = SecureCrypto.verifyPin(pin, storedHash.toString());
      if (isValid) {
        _isLocked = false;
        _pinAttempts = 0;
        resetInactivityTimer();
        notifyListeners();
      } else {
        _pinAttempts++;
        notifyListeners();
      }
      return isValid;
    } catch (e) {
      debugPrint("Error verifying PIN: $e");
      return false;
    }
  }

  Future<bool> authenticateBiometrics() async {
    // Biometric auth requires flutter_local_auth package
    // TODO: Add local_auth plugin for production
    return false;
  }

  Future<void> setBiometricEnabled(bool enabled) async {
    try {
      final prefs = await _readPrefs();
      prefs[_biometricKey] = enabled;
      await _writePrefs(prefs);
      _biometricEnabled = enabled;
      notifyListeners();
    } catch (e) {
      debugPrint("Error setting biometric state: $e");
    }
  }

  void resetInactivityTimer() {
    _inactivityTimer?.cancel();
    if (_hasPinSet && !_isLocked) {
      _inactivityTimer = Timer(const Duration(seconds: _inactivityTimeoutSeconds), () {
        lock();
      });
    }
  }

  void lock() {
    if (_hasPinSet && !_isLocked) {
      _isLocked = true;
      _inactivityTimer?.cancel();
      notifyListeners();
    }
  }

  void unlock() {
    _isLocked = false;
    _pinAttempts = 0;
    resetInactivityTimer();
    notifyListeners();
  }

  Future<void> clearAuthData() async {
    try {
      final prefs = await _readPrefs();
      prefs.remove(_pinKey);
      prefs.remove("verdis_wallet_pin_hash"); // legacy
      prefs.remove(_biometricKey);
      await _writePrefs(prefs);
      _hasPinSet = false;
      _isLocked = false;
      _biometricEnabled = false;
      _pinAttempts = 0;
      _inactivityTimer?.cancel();
      notifyListeners();
    } catch (e) {
      debugPrint("Error clearing auth data: $e");
    }
  }

  @override
  void dispose() {
    _inactivityTimer?.cancel();
    super.dispose();
  }
}
