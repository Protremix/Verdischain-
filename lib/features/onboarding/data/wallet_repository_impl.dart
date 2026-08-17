import 'package:verdis_wallet/core/security/wallet_crypto.dart';
import 'package:bip39/bip39.dart' as bip39;
import 'package:hex/hex.dart';
import 'package:polkadart_keyring/polkadart_keyring.dart';
import 'package:verdis_wallet/core/config/network_config.dart';
import 'package:verdis_wallet/core/security/secure_storage.dart';
import '../domain/wallet_repository.dart';

/// SR25519-based wallet repository using polkadart_keyring.
/// Replaces Ed25519 derivation - now matches the web wallet's crypto scheme.
class WalletRepositoryImpl implements WalletRepository {

  WalletRepositoryImpl(this._secureStorage);
  final SecureStorageHelper _secureStorage;

  static const String _mnemonicKey = 'verdis_mnemonic';
  static const int _ss58Format = 909; // Verdis network prefix

  @override
  Future<String> generateMnemonic() async {
    return bip39.generateMnemonic();
  }

  @override
  Future<bool> validateMnemonic(String mnemonic) async {
    final cleaned = mnemonic.trim().replaceAll(RegExp(r'\s+'), ' ');
    if (cleaned.isEmpty) return false;
    final words = cleaned.split(' ');
    if (words.length != 12 && words.length != 24) return false;
    return bip39.validateMnemonic(cleaned);
  }

  @override
  Future<Map<String, String>> deriveKeypair(String mnemonic) async {
    final cleaned = mnemonic.trim().replaceAll(RegExp(r'\s+'), ' ');

    // Derive SR25519 keypair from mnemonic (matches @polkadot/keyring addFromMnemonic)
    final keyPair = KeyPair.sr25519;
    keyPair.ss58Format = _ss58Format;
    await keyPair.fromMnemonic(cleaned);

    final address = keyPair.address;
    final publicKeyBytes = keyPair.publicKey.bytes;
    final publicKeyHex = HEX.encode(publicKeyBytes);

    // For SR25519, the private key is the secret key bytes
    final privateKeyHex = HEX.encode(keyPair.bytes());

    return {
      'mnemonic': cleaned,
      'privateKey': privateKeyHex,
      'publicKey': publicKeyHex,
      'address': address,
    };
  }

  @override
  Future<Map<String, String>> importFromMnemonic(String mnemonic) async {
    final isValid = await validateMnemonic(mnemonic);
    if (!isValid) {
      throw Exception('Invalid seed phrase. Please verify your 12 or 24 words.');
    }
    return deriveKeypair(mnemonic);
  }

  /// Store wallet with encrypted mnemonic.
  /// The mnemonic is encrypted using the user's PIN as the encryption key.
  /// Private key is NOT stored separately - derived from mnemonic on demand.
  @override
  Future<void> storeWallet({
    required String mnemonic,
    required String privateKey,
    required String publicKey,
    required String address,
    String? pin,
  }) async {
    // Store mnemonic encrypted with PIN if available
    if (pin != null && pin.isNotEmpty) {
      await _secureStorage.storeMnemonicEncrypted(mnemonic, pin);
    } else {
      // Fallback to legacy storage during onboarding before PIN is set
      await _secureStorage.write(_mnemonicKey, mnemonic);
    }
    // Store public key and address (not secrets, but useful for display)
    await _secureStorage.storePublicKey(publicKey);
    await _secureStorage.write(AppConstants.walletKey, address);
    await _secureStorage.write(AppConstants.onboardingCompleteKey, 'true');
    // Migrate: remove old plaintext mnemonic and private key
    await _secureStorage.delete('wallet_mnemonic');
    await _secureStorage.delete('wallet_private_key');
  }

  @override
  Future<Map<String, String>?> loadWallet({String? pin}) async {
    final publicKey = await _secureStorage.getPublicKey();
    final address = await _secureStorage.read(AppConstants.walletKey);

    if (address == null) return null;

    String? mnemonic;
    String? privateKey;

    // Try encrypted mnemonic first (new secure path)
    if (pin != null && pin.isNotEmpty) {
      mnemonic = await _secureStorage.getMnemonicEncrypted(pin);
      if (mnemonic != null) {
        // Derive private key on demand from decrypted mnemonic
        final keypair = await deriveKeypair(mnemonic);
        privateKey = keypair['privateKey'];
      }
    }

    // Fallback to legacy storage (migration path)
    if (mnemonic == null) {
      mnemonic = await _secureStorage.read(_mnemonicKey);
      privateKey = await _secureStorage.getPrivateKey();
    }

    if (mnemonic == null && privateKey == null) return null;

    return {
      if (mnemonic != null) 'mnemonic': mnemonic,
      if (privateKey != null) 'privateKey': privateKey,
      if (publicKey != null) 'publicKey': publicKey,
      'address': address,
    };
  }

  @override
  Future<void> deleteWallet() async {
    await _secureStorage.clearWallet();
    await _secureStorage.delete(_mnemonicKey);
    await _secureStorage.delete(AppConstants.walletKey);
    await _secureStorage.delete(AppConstants.onboardingCompleteKey);
  }

  @override
  Future<String> hashPin(String pin) async {
    return WalletCrypto.hashPin(pin);
  }

  @override
  Future<void> savePinHash(String pinHash) async {
    await _secureStorage.storePinHash(pinHash);
  }

  @override
  Future<bool> verifyPin(String pin) async {
    final storedHash = await _secureStorage.getPinHash();
    if (storedHash == null) return false;
    return WalletCrypto.verifyPin(pin, storedHash);
  }

  @override
  Future<bool> hasWallet() async {
    return await _secureStorage.hasWallet();
  }

  @override
  Future<void> setBiometricEnabled(bool enabled) async {
    await _secureStorage.setBiometricEnabled(enabled);
  }

  @override
  Future<bool> isBiometricEnabled() async {
    return await _secureStorage.isBiometricEnabled();
  }
}
