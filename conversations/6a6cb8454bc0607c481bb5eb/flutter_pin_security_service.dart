import 'dart:convert';
import 'package:http/http.dart' as http;

/// Server-side PIN security service for the Verdis wallet.
///
/// Communicates with the TX Relay backend to:
/// - Register PIN (salted hash stored server-side)
/// - Verify PIN (rate-limited, with lockout)
/// - Check PIN status (is a PIN registered for this address?)
///
/// The server NEVER stores or sees the raw PIN — only a salted SHA-256 hash
/// with 100,000 iterations.
class PinSecurityService {
  static const String _baseUrl = 'https://verdischain.com/api/tx-relay';

  /// Register a PIN for a wallet address on the server.
  /// Called when user creates a new wallet or imports for the first time.
  ///
  /// Returns (success, message).
  static Future<(bool, String)> registerPin({
    required String address,
    required String pin,
  }) async {
    if (pin.length < 4 || pin.length > 6 || !RegExp(r'^\d{4,6}$').hasMatch(pin)) {
      return (false, 'PIN must be 4-6 digits');
    }

    try {
      final response = await http.post(
        Uri.parse(_baseUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'action': 'pin-register',
          'address': address,
          'pin': pin,
        }),
      );

      final data = json.decode(response.body) as Map<String, dynamic>;
      if (data['ok'] == true) {
        return (true, 'PIN registered successfully');
      } else {
        final error = data['error'] as String? ?? 'Registration failed';
        return (false, error);
      }
    } catch (e) {
      return (false, 'Network error: $e');
    }
  }

  /// Verify a PIN against the server's stored hash.
  /// Returns (success, message, attemptsRemaining).
  ///
  /// If the address has no PIN registered, returns (true, 'no_pin_registered', 5).
  /// If the PIN is wrong, returns (false, 'wrong_pin', remaining).
  /// If locked out, returns (false, 'locked', 0).
  static Future<(bool, String, int)> verifyPin({
    required String address,
    required String pin,
  }) async {
    if (pin.length < 4 || pin.length > 6 || !RegExp(r'^\d{4,6}$').hasMatch(pin)) {
      return (false, 'PIN must be 4-6 digits', 0);
    }

    try {
      final response = await http.post(
        Uri.parse(_baseUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'action': 'pin-verify',
          'address': address,
          'pin': pin,
        }),
      );

      final data = json.decode(response.body) as Map<String, dynamic>;
      if (data['ok'] == true) {
        final dataInner = data['data'] as Map<String, dynamic>? ?? {};
        final attemptsRemaining = (dataInner['attempts_remaining'] ?? 5) as int;
        final message = (dataInner['message'] ?? 'verified') as String;
        return (true, message, attemptsRemaining);
      } else {
        final error = (data['error'] ?? 'Verification failed') as String;
        if (error.contains('Locked')) {
          return (false, 'locked', 0);
        }
        // Extract attempts remaining from error message
        final match = RegExp(r'(\d+) attempts remaining').firstMatch(error);
        final remaining = match != null ? int.parse(match.group(1)!) : 0;
        return (false, 'wrong_pin', remaining);
      }
    } catch (e) {
      return (false, 'Network error: $e', 0);
    }
  }

  /// Check if a PIN is registered for an address.
  /// Returns a map with 'has_pin', 'locked', and 'locked_remaining' keys.
  static Future<Map<String, dynamic>> getPinStatus(String address) async {
    try {
      final response = await http.post(
        Uri.parse(_baseUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'action': 'pin-status',
          'address': address,
        }),
      );

      final data = json.decode(response.body) as Map<String, dynamic>;
      if (data['ok'] == true) {
        return (data['data'] ?? {'has_pin': false, 'locked': false}) as Map<String, dynamic>;
      }
    } catch (e) {
      // Network error — assume no PIN for graceful degradation
    }
    return {'has_pin': false, 'locked': false};
  }

  /// Recover wallet from email — requires PIN.
  /// Returns the encrypted backup blob if PIN is verified.
  static Future<Map<String, dynamic>?> recoverFromEmail({
    required String email,
    required String password,
    required String pin,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(_baseUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'action': 'wallet-recover',
          'email': email,
          'pin': pin,
        }),
      );

      final data = json.decode(response.body) as Map<String, dynamic>;
      if (data['ok'] == true) {
        return (data['backup'] ?? null) as Map<String, dynamic>?;
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }
}
