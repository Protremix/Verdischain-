import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:convert';
import 'dart:typed_data';
import 'package:crypto/crypto.dart';
import 'package:cryptography/cryptography.dart' as pc;
import 'package:hex/hex.dart';

final secureStorageProvider = Provider<SecureStorageHelper>((ref) {
  return SecureStorageHelper();
});

class SecureStorageHelper {
  SecureStorageHelper() : _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: false,
      resetOnError: true,
    ),
  );
  final FlutterSecureStorage _storage;

  // PBKDF2 for mnemonic encryption (separate from PIN hash)
  static final pc.Pbkdf2 _mnemonicPbkdf2 = pc.Pbkdf2(
    macAlgorithm: pc.Hmac.sha256(),
    iterations: 100000,
    bits: 256,
  );
  static final pc.AesGcm _aesGcm = pc.AesGcm.with256bits();

  // ===== MNEMONIC (encrypted with PIN-derived key) =====

  /// Store mnemonic encrypted with a key derived from the user's PIN.
  /// This adds a second layer: even if secure storage is compromised,
  /// the mnemonic cannot be decrypted without the PIN.
  Future<void> storeMnemonicEncrypted(String mnemonic, String pin) async {
    final salt = _generateRandomBytes(16);
    final nonce = _generateRandomBytes(12);
    final key = await _deriveKey(pin, salt);
    final secretBox = await _aesGcm.encrypt(
      utf8.encode(mnemonic),
      secretKey: key,
      nonce: nonce,
    );
    final combined = base64Encode(Uint8List.fromList(
      [...secretBox.cipherText, ...secretBox.mac.bytes],
    ));
    await _storage.write(key: 'enc_mnemonic', value: jsonEncode({
      'ciphertext': combined,
      'salt': base64Encode(salt),
      'iv': base64Encode(nonce),
    }));
  }

  /// Decrypt mnemonic using PIN. Returns null if PIN is wrong.
  Future<String?> getMnemonicEncrypted(String pin) async {
    final stored = await _storage.read(key: 'enc_mnemonic');
    if (stored == null) return null;
    try {
      final data = jsonDecode(stored) as Map<String, dynamic>;
      final salt = base64Decode(data['salt'] as String);
      final iv = base64Decode(data['iv'] as String);
      final combined = base64Decode(data['ciphertext'] as String);
      final cipherText = combined.sublist(0, combined.length - 16);
      final mac = combined.sublist(combined.length - 16);
      final key = await _deriveKey(pin, salt);
      final secretBox = pc.SecretBox(
        Uint8List.fromList(cipherText),
        nonce: Uint8List.fromList(iv),
        mac: pc.Mac(Uint8List.fromList(mac)),
      );
      final plaintext = await _aesGcm.decrypt(
        secretBox,
        secretKey: key,
      );
      return utf8.decode(plaintext);
    } catch (_) {
      return null; // Wrong PIN or corrupted data
    }
  }

  Future<bool> hasEncryptedMnemonic() async {
    final stored = await _storage.read(key: 'enc_mnemonic');
    return stored != null && stored.isNotEmpty;
  }

  Future<void> deleteEncryptedMnemonic() async {
    await _storage.delete(key: 'enc_mnemonic');
  }

  // ===== Legacy plaintext mnemonic (for migration) =====

  Future<void> storeMnemonic(String mnemonic) async {
    await _storage.write(key: 'wallet_mnemonic', value: mnemonic);
  }

  Future<String?> getMnemonic() async {
    return await _storage.read(key: 'wallet_mnemonic');
  }

  // ===== Private key (kept for tx signing, derived from mnemonic on demand) =====

  Future<void> storePrivateKey(String privateKey) async {
    await _storage.write(key: 'wallet_private_key', value: privateKey);
  }

  Future<String?> getPrivateKey() async {
    return await _storage.read(key: 'wallet_private_key');
  }

  Future<void> storePublicKey(String publicKey) async {
    await _storage.write(key: 'wallet_public_key', value: publicKey);
  }

  Future<String?> getPublicKey() async {
    return await _storage.read(key: 'wallet_public_key');
  }

  Future<void> storePinHash(String pinHash) async {
    await _storage.write(key: 'wallet_pin_hash', value: pinHash);
  }

  Future<String?> getPinHash() async {
    return await _storage.read(key: 'wallet_pin_hash');
  }

  Future<void> setBiometricEnabled(bool enabled) async {
    await _storage.write(key: 'biometric_enabled', value: enabled.toString());
  }

  Future<bool> isBiometricEnabled() async {
    final value = await _storage.read(key: 'biometric_enabled');
    return value == 'true';
  }

  // Email recovery
  Future<String?> getRecoveryEmail() async {
    return await _storage.read(key: 'recovery_email');
  }

  Future<void> setRecoveryEmail(String email) async {
    await _storage.write(key: 'recovery_email', value: email);
  }

  // Wallet address
  Future<String?> getWalletAddress() async {
    return await _storage.read(key: 'verdis_wallet_address') ??
        await _storage.read(key: 'wallet_address');
  }

  Future<void> storeWalletAddress(String address) async {
    await _storage.write(key: 'verdis_wallet_address', value: address);
  }

  Future<bool> hasWallet() async {
    final mnemonic = await getMnemonic();
    final encMnemonic = await hasEncryptedMnemonic();
    final storedMnemonic = await read('verdis_mnemonic');
    final walletAddress = await read('verdis_wallet_address');
    final walletKey = await read('verdis_wallet');
    final onboarding = await read('verdis_onboarding');
    return (mnemonic != null && mnemonic.isNotEmpty) ||
           encMnemonic ||
           (storedMnemonic != null && storedMnemonic.isNotEmpty) ||
           (walletAddress != null && walletAddress.isNotEmpty) ||
           (walletKey != null && walletKey.isNotEmpty) ||
           (onboarding == 'true');
  }

  Future<void> clearWallet() async {
    await _storage.delete(key: 'wallet_mnemonic');
    await _storage.delete(key: 'wallet_private_key');
    await _storage.delete(key: 'wallet_public_key');
    await _storage.delete(key: 'wallet_pin_hash');
    await _storage.delete(key: 'biometric_enabled');
    await _storage.delete(key: 'recovery_email');
    await _storage.delete(key: 'enc_mnemonic');
  }

  Future<void> write(String key, String value) async {
    await _storage.write(key: key, value: value);
  }

  Future<String?> read(String key) async {
    return await _storage.read(key: key);
  }

  Future<void> delete(String key) async {
    await _storage.delete(key: key);
  }

  // ===== Internal helpers =====

  Uint8List _generateRandomBytes(int length) {
    final random = DateTime.now().microsecondsSinceEpoch;
    final bytes = <int>[];
    var seed = random;
    for (var i = 0; i < length; i++) {
      seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF;
      bytes.add(seed & 0xFF);
    }
    return Uint8List.fromList(bytes);
  }

  Future<pc.SecretKey> _deriveKey(String pin, List<int> salt) async {
    final secretKey = pc.SecretKey(utf8.encode(pin));
    return _mnemonicPbkdf2.deriveKey(secretKey: secretKey, nonce: salt);
  }
}
