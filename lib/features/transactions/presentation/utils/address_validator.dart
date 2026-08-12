import 'package:bs58/bs58.dart';
import 'package:verdis_wallet/core/security/blake2b.dart';
import 'dart:typed_data';

/// Helper utility for validating and formatting Verdis SS58 wallet addresses.
class AddressValidator {
  AddressValidator._();

  /// Valid SS58 address characters (Base58 alphabet)
  static const String _base58Alphabet =
      '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

  /// Verdis SS58 network prefix ID (909) or standard SS58
  static const int verdisNetworkPrefix = 909;

  /// Check if an address is valid
  static bool isValid(String? address) {
    if (address == null || address.trim().isEmpty) return false;
    final trimmed = address.trim();

    // Check basic length bounds for SS58 addresses (typically 32 to 64 chars)
    if (trimmed.length < 32 || trimmed.length > 64) {
      return false;
    }

    // Check Base58 character set
    for (int i = 0; i < trimmed.length; i++) {
      if (!_base58Alphabet.contains(trimmed[i])) {
        return false;
      }
    }

    // Try decoding base58 and checking checksum
    try {
      final decoded = base58.decode(trimmed);
      if (decoded.length < 35) return false; // prefix + pubkey (32) + checksum (2)
      return validateChecksum(trimmed);
    } catch (_) {
      return false;
    }
  }

  /// Validate checksum of base58 decoded bytes
  static bool validateChecksum(String address) {
    try {
      final decoded = base58.decode(address.trim());
      if (decoded.length < 35) return false;

      final body = decoded.sublist(0, decoded.length - 2);
      final checksum = decoded.sublist(decoded.length - 2);

      final hash1 = blake2b256(Uint8List.fromList(body));  // Substrate uses Blake2b
      final hash2 = blake2b256(hash1);

      return checksum[0] == hash2[0] && checksum[1] == hash2[1];
    } catch (_) {
      return false;
    }
  }

  /// Returns user-friendly validation error message or null if valid.
  static String? getValidationError(String? address) {
    if (address == null || address.trim().isEmpty) {
      return 'Recipient address is required';
    }
    final trimmed = address.trim();
    if (trimmed.length < 32 || trimmed.length > 64) {
      return 'Invalid address length (${trimmed.length} characters)';
    }
    for (int i = 0; i < trimmed.length; i++) {
      if (!_base58Alphabet.contains(trimmed[i])) {
        return 'Address contains invalid character: ${trimmed[i]}';
      }
    }
    if (!isValid(trimmed)) {
      return 'Invalid Verdis SS58 address checksum';
    }
    return null;
  }

  /// Format address for compact UI display (e.g., verdis1a2...x89)
  static String formatAddress(String address, {int start = 6, int end = 6}) {
    final trimmed = address.trim();
    if (trimmed.length <= start + end + 3) {
      return trimmed;
    }
    return '${trimmed.substring(0, start)}...${trimmed.substring(trimmed.length - end)}';
  }
}
