import 'package:flutter_test/flutter_test.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';

void main() {
  group('WalletAccount', () {
    test('should serialize to JSON correctly', () {
      final account = WalletAccount(
        address: '5GrwvaEFPP...test',
        publicKey: '0xabc123',
        name: 'Test Wallet',
        balance: 1000000000,
        lockedBalance: 50000,
        stakedBalance: 200000,
      );

      final json = account.toJson();

      expect(json['address'], '5GrwvaEFPP...test');
      expect(json['publicKey'], '0xabc123');
      expect(json['name'], 'Test Wallet');
      expect(json['balance'], 1000000000);
      expect(json['lockedBalance'], 50000);
      expect(json['stakedBalance'], 200000);
    });

    test('should deserialize from JSON correctly', () {
      final json = {
        'address': '5GrwvaEFPP...test2',
        'publicKey': '0xdef456',
        'name': 'Imported Wallet',
        'balance': 500000000,
      };

      final account = WalletAccount.fromJson(json);

      expect(account.address, '5GrwvaEFPP...test2');
      expect(account.publicKey, '0xdef456');
      expect(account.name, 'Imported Wallet');
      expect(account.balance, 500000000);
      expect(account.lockedBalance, 0); // default
      expect(account.stakedBalance, 0); // default
    });

    test('should handle null optionals in fromJson', () {
      final json = {
        'address': '5GrwvaEFPP...test3',
        'publicKey': '0x123',
      };

      final account = WalletAccount.fromJson(json);

      expect(account.address, '5GrwvaEFPP...test3');
      expect(account.name, isNull);
      expect(account.balance, 0);
      expect(account.proxyAddress, isNull);
    });
  });

  group('TokenBalance', () {
    test('should create with all fields', () {
      const token = TokenBalance(
        tokenId: '1',
        name: 'Eco Token',
        symbol: 'ECO',
        decimals: 9,
        balance: 1000000000,
      );

      expect(token.tokenId, '1');
      expect(token.symbol, 'ECO');
      expect(token.decimals, 9);
      expect(token.balance, 1000000000);
      expect(token.isFrozen, false);
    });
  });

  group('TransactionRecord', () {
    test('should create transaction record correctly', () {
      final tx = TransactionRecord(
        hash: '0xabc',
        blockHash: '0xdef',
        blockNumber: 12345,
        from: '5GrwvaEFPP...sender',
        to: '5GrwvaEFPP...receiver',
        amount: 1000000000,
        fee: 1000000,
        module: 'balances',
        call: 'transfer',
        status: 'success',
      );

      expect(tx.hash, '0xabc');
      expect(tx.blockNumber, 12345);
      expect(tx.amount, 1000000000);
      expect(tx.module, 'balances');
      expect(tx.call, 'transfer');
      expect(tx.status, 'success');
    });
  });

  group('ValidatorInfo', () {
    test('should create validator with defaults', () {
      const validator = ValidatorInfo(
        address: '5GrwvaEFPP...validator',
        name: 'Validator Alpha',
        stake: 10000000000,
        greenScore: 5,
        energySource: 'solar',
      );

      expect(validator.address, '5GrwvaEFPP...validator');
      expect(validator.greenScore, 5);
      expect(validator.energySource, 'solar');
      expect(validator.commission, 0);
      expect(validator.isActive, true);
    });
  });

  group('DexPool', () {
    test('should serialize/deserialize with snake_case keys', () {
      final json = {
        'pool_id': 1,
        'token_a': 'VRDX',
        'token_b': 'ECO',
        'reserve_a': 500000000000,
        'reserve_b': 100000000000,
        'fee_rate': 0.003,
      };

      final pool = DexPool.fromJson(json);

      expect(pool.poolId, 1);
      expect(pool.tokenA, 'VRDX');
      expect(pool.tokenB, 'ECO');
      expect(pool.reserveA, 500000000000);
      expect(pool.reserveB, 100000000000);
      expect(pool.feeRate, 0.003);
    });

    test('should handle camelCase keys too', () {
      final json = {
        'poolId': 2,
        'tokenA': 'VRDX',
        'tokenB': 'CARBON',
        'reserveA': 300000000000,
        'reserveB': 100000000000,
      };

      final pool = DexPool.fromJson(json);

      expect(pool.poolId, 2);
      expect(pool.tokenB, 'CARBON');
      expect(pool.reserveA, 300000000000);
    });
  });

  group('StakingPosition', () {
    test('should create with active status by default', () {
      final position = StakingPosition(
        validatorAddress: '5GrwvaEFPP...validator',
        amount: 50000000000,
        rewards: 1000000000,
        stakedAt: DateTime(2026, 8, 19),
      );

      expect(position.validatorAddress, '5GrwvaEFPP...validator');
      expect(position.amount, 50000000000);
      expect(position.rewards, 1000000000);
      expect(position.status, StakingStatus.active);
    });
  });

  group('BlockInfo', () {
    test('should create with extrinsics list', () {
      const block = BlockInfo(
        hash: '0xblock123',
        number: 668,
        parentHash: '0xparent',
        timestamp: 1724089200,
        validator: '5GrwvaEFPP...validator',
        extrinsicCount: 3,
      );

      expect(block.number, 668);
      expect(block.extrinsicCount, 3);
      expect(block.extrinsics, isEmpty);
    });
  });
}
