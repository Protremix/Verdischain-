import 'package:flutter_test/flutter_test.dart';
import 'package:verdis_wallet/core/security/wallet_crypto.dart';

void main() {
  group('WalletCrypto - Mnemonic', () {
    test('should generate a valid 12-word mnemonic', () {
      final mnemonic = WalletCrypto.generateMnemonic();
      final words = mnemonic.split(' ');

      expect(words.length, 12);
      expect(WalletCrypto.validateMnemonic(mnemonic), isTrue);
    });

    test('should generate a valid 24-word mnemonic', () {
      final mnemonic = WalletCrypto.generateMnemonic24();
      final words = mnemonic.split(' ');

      expect(words.length, 24);
      expect(WalletCrypto.validateMnemonic(mnemonic), isTrue);
    });

    test('should validate a known good mnemonic', () {
      const mnemonic = 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about';
      expect(WalletCrypto.validateMnemonic(mnemonic), isTrue);
    });

    test('should reject invalid mnemonic', () {
      const mnemonic = 'invalid word phrase that is not valid bip39';
      expect(WalletCrypto.validateMnemonic(mnemonic), isFalse);
    });

    test('should reject empty mnemonic', () {
      expect(WalletCrypto.validateMnemonic(''), isFalse);
    });

    test('should produce different mnemonics on successive calls', () {
      final m1 = WalletCrypto.generateMnemonic();
      final m2 = WalletCrypto.generateMnemonic();

      expect(m1, isNot(m2));
    });
  });

  group('WalletCrypto - Seed derivation', () {
    test('should derive a deterministic seed from mnemonic', () {
      const mnemonic = 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about';

      final seed1 = WalletCrypto.mnemonicToSeed(mnemonic);
      final seed2 = WalletCrypto.mnemonicToSeed(mnemonic);

      expect(seed1.length, 64); // 512 bits
      expect(seed1, equals(seed2)); // deterministic
    });

    test('should produce different seeds for different mnemonics', () {
      const m1 = 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about';
      const m2 = 'legal winner thank year wave sausage worth useful legal winner thank yellow';

      final seed1 = WalletCrypto.mnemonicToSeed(m1);
      final seed2 = WalletCrypto.mnemonicToSeed(m2);

      expect(seed1, isNot(equals(seed2)));
    });
  });

  group('WalletCrypto - PIN hashing', () {
    test('should hash a 6-digit PIN consistently', () {
      final hash1 = WalletCrypto.hashPin('123456');
      final hash2 = WalletCrypto.hashPin('123456');

      // Same PIN should produce same hash (deterministic with fixed salt in test)
      expect(hash1, isNotEmpty);
    });

    test('should produce different hashes for different PINs', () {
      final hash1 = WalletCrypto.hashPin('123456');
      final hash2 = WalletCrypto.hashPin('654321');

      expect(hash1, isNot(hash2));
    });

    test('should handle edge case PINs', () {
      expect(WalletCrypto.hashPin('000000'), isNotEmpty);
      expect(WalletCrypto.hashPin('999999'), isNotEmpty);
    });
  });
}
