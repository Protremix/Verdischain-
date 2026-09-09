import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Provider for the wallet repository interface
final walletRepositoryProvider = Provider<WalletRepository>((ref) {
  throw UnimplementedError('walletRepositoryProvider must be overridden in ProviderScope or initialized');
});

/// Abstract repository defining wallet operations
abstract class WalletRepository {
  /// Generate a 12-word BIP-39 mnemonic
  Future<String> generateMnemonic();

  /// Validate a mnemonic seed phrase checksum
  Future<bool> validateMnemonic(String mnemonic);

  /// Derive keypair (private key, public key, address) from a mnemonic
  Future<Map<String, String>> deriveKeypair(String mnemonic);

  /// Import wallet from mnemonic and derive keys
  Future<Map<String, String>> importFromMnemonic(String mnemonic);

  /// Persist wallet keys and address into secure storage
  Future<void> storeWallet({
    required String mnemonic,
    required String privateKey,
    required String publicKey,
    required String address,
  });

  /// Read active wallet keys and address from secure storage
  Future<Map<String, String>?> loadWallet();

  /// Delete stored wallet data
  Future<void> deleteWallet();

  /// Hash a 6-digit PIN with SHA-256 and salt
  Future<String> hashPin(String pin);

  /// Save hashed PIN into secure storage
  Future<void> savePinHash(String pinHash);

  /// Verify entered PIN against stored PIN hash
  Future<bool> verifyPin(String pin);

  /// Check if a wallet exists in secure storage
  Future<bool> hasWallet();

  /// Set biometric authentication state
  Future<void> setBiometricEnabled(bool enabled);

  /// Check if biometric authentication is enabled
  Future<bool> isBiometricEnabled();
}
