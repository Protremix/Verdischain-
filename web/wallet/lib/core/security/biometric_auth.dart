import 'package:local_auth/local_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final biometricAuthProvider = Provider<BiometricManager>((ref) {
  return BiometricManager();
});

/// Handles biometric authentication (fingerprint, face ID, etc.)
class BiometricManager {
  final LocalAuthentication _auth = LocalAuthentication();

  /// Check if device supports biometric authentication
  Future<bool> isAvailable() async {
    final canCheck = await _auth.canCheckBiometrics;
    final isDeviceSupported = await _auth.isDeviceSupported();
    return canCheck && isDeviceSupported;
  }

  /// Get available biometric types
  Future<List<BiometricType>> getAvailableBiometrics() async {
    return await _auth.getAvailableBiometrics();
  }

  /// Authenticate with biometrics
  Future<bool> authenticate({String reason = 'Authenticate to access Verdis Wallet'}) async {
    try {
      return await _auth.authenticate(
        localizedReason: reason,
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: false,
        ),
      );
    } catch (e) {
      return false;
    }
  }

  /// Stop authentication
  Future<void> stopAuthentication() async {
    await _auth.stopAuthentication();
  }
}
