import 'package:flutter_test/flutter_test.dart';
import 'package:verdis_wallet/core/config/network_config.dart';

void main() {
  group('NetworkConfig', () {
    test('should have correct RPC URL', () {
      expect(NetworkConfig.rpcUrl, 'https://verdischain.com/rpc');
    });

    test('should have correct WebSocket URL', () {
      expect(NetworkConfig.wsUrl, 'wss://verdischain.com/rpc');
    });

    test('should have correct chain info', () {
      expect(NetworkConfig.chainName, 'Verdis');
      expect(NetworkConfig.chainId, 909);
      expect(NetworkConfig.tokenSymbol, 'VRDX');
      expect(NetworkConfig.decimals, 9);
    });

    test('should have correct tokenomics', () {
      expect(NetworkConfig.totalSupply, 100000000000); // 100B
      expect(NetworkConfig.circulatingSupply, 15000000000); // 15B at TGE
    });

    test('should have correct consensus config', () {
      expect(NetworkConfig.consensus, 'BABE/GRANDPA + DPoS');
      expect(NetworkConfig.validatorCount, 21);
    });
  });

  group('AppConstants', () {
    test('should have correct app info', () {
      expect(AppConstants.appName, 'Verdis Wallet');
      expect(AppConstants.appVersion, '2.1.11');
    });

    test('should have correct security constants', () {
      expect(AppConstants.pinLength, 6);
      expect(AppConstants.sessionTimeoutMinutes, 2);
      expect(AppConstants.autoLockMinutes, 1);
    });

    test('should have correct storage keys', () {
      expect(AppConstants.walletKey, 'verdis_wallet');
      expect(AppConstants.pinHashKey, 'verdis_pin_hash');
      expect(AppConstants.onboardingCompleteKey, 'verdis_onboarding');
    });
  });
}
