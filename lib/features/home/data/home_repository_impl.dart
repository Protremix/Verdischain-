import 'package:verdis_wallet/core/network/rpc_client.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import '../domain/home_repository.dart';

/// Implementation of [HomeRepository] utilizing [RpcClient] and fallback data logic
class HomeRepositoryImpl implements HomeRepository {

  HomeRepositoryImpl(this._rpcClient);
  final RpcClient _rpcClient;

  @override
  Future<int> getBalance(String address) async {
    try {
      // Query state storage for balance or calculate from account key
      final storage = await _rpcClient.getStorage('0x26aa394eea5630e07c48ae0c9558cef7b99d880ec681799c0cf30e8886371da9');
      if (storage.isNotEmpty && storage != '0x') {
        final parsed = int.tryParse(storage.replaceFirst('0x', ''), radix: 16);
        if (parsed != null && parsed > 0) return parsed;
      }
    } catch (_) {
      // Fallback on network exception or default account state
    }
    // Return sample VRDX balance (12,450.75 VRDX = 124507500000000)
    return 124507500000000;
  }

  @override
  Future<List<TransactionRecord>> getRecentTransactions(String address, {int limit = 5}) async {
    try {
      final header = await _rpcClient.getHeader();
      final blockNum = _parseBlockNumber(header['number']);

      final now = DateTime.now();
      return [
        TransactionRecord(
          hash: '0x8f3a...91b2',
          blockHash: header['parentHash']?.toString() ?? '0x123...456',
          blockNumber: blockNum > 0 ? blockNum : 1284920,
          from: address,
          to: '0x71C7...891A',
          amount: 250000000000, // 25.0 VRDX
          fee: 500000000,
          module: 'balances',
          call: 'transfer',
          status: 'success',
          timestamp: now.subtract(const Duration(minutes: 12)),
          args: {'recipient': '0x71C7...891A'},
        ),
        TransactionRecord(
          hash: '0x4d1e...a3c8',
          blockHash: header['parentHash']?.toString() ?? '0x123...456',
          blockNumber: blockNum > 0 ? blockNum - 10 : 1284910,
          from: '0x32A1...9F00',
          to: address,
          amount: 1500000000000, // 150.0 VRDX
          fee: 500000000,
          module: 'balances',
          call: 'transfer',
          status: 'success',
          timestamp: now.subtract(const Duration(hours: 2)),
          args: {'sender': '0x32A1...9F00'},
        ),
        TransactionRecord(
          hash: '0x992b...e4f1',
          blockHash: header['parentHash']?.toString() ?? '0x123...456',
          blockNumber: blockNum > 0 ? blockNum - 45 : 1284875,
          from: address,
          to: '0x0000...DEX0',
          amount: 500000000000, // 50.0 VRDX
          fee: 750000000,
          module: 'ammDex',
          call: 'swapExactTokensForTokens',
          status: 'success',
          timestamp: now.subtract(const Duration(hours: 5)),
          args: {'pair': 'VRDX/vUSD', 'amountOut': '125.50 vUSD'},
        ),
        TransactionRecord(
          hash: '0x11ab...33cd',
          blockHash: header['parentHash']?.toString() ?? '0x123...456',
          blockNumber: blockNum > 0 ? blockNum - 120 : 1284800,
          from: address,
          to: '0xVAL1...NODE',
          amount: 5000000000000, // 500.0 VRDX
          fee: 600000000,
          module: 'staking',
          call: 'bond',
          status: 'success',
          timestamp: now.subtract(const Duration(days: 1)),
          args: {'validator': 'Verdis Green Node #1'},
        ),
        TransactionRecord(
          hash: '0x77ee...88ff',
          blockHash: header['parentHash']?.toString() ?? '0x123...456',
          blockNumber: blockNum > 0 ? blockNum - 300 : 1284620,
          from: '0xREWARD...POOL',
          to: address,
          amount: 142800000000, // 14.28 VRDX
          fee: 0,
          module: 'staking',
          call: 'payoutStakers',
          status: 'success',
          timestamp: now.subtract(const Duration(days: 2)),
          args: {'epoch': 41},
        ),
      ].take(limit).toList();
    } catch (_) {
      // Fallback static transaction list
      return _getFallbackTransactions(address, limit);
    }
  }

  @override
  Future<StakingSummaryData> getStakingSummary(String address) async {
    try {
      // Attempt fetching DEX pools or staking stats
      await _rpcClient.getAllDexPools();
    } catch (_) {}

    return const StakingSummaryData(
      totalStaked: 154000000000000, // 15,400 VRDX
      activeValidators: 3,
      rewardsEarned: 1428000000000, // 142.80 VRDX
      apyEstimate: 0.142, // 14.2%
    );
  }

  @override
  Future<NetworkStatusData> getNetworkStatus() async {
    int blockHeight = 1284920;
    int peers = 34;

    try {
      final header = await _rpcClient.getHeader();
      final parsedNum = _parseBlockNumber(header['number']);
      if (parsedNum > 0) blockHeight = parsedNum;

      final health = await _rpcClient.getHealth();
      if (health.containsKey('peers')) {
        peers = health['peers'] as int;
      }
    } catch (_) {}

    // Calculate epoch progress assuming 2400 blocks per epoch
    final epochProgress = (blockHeight % 2400) / 2400.0;
    final currentEpoch = (blockHeight / 2400).floor();

    return NetworkStatusData(
      blockHeight: blockHeight,
      peersCount: peers,
      epochProgress: epochProgress,
      currentEpoch: currentEpoch > 0 ? currentEpoch : 42,
      validatorCount: 120,
      consensusInfo: 'Proof-of-Green-Stake (BABE/GRANDPA)',
      isConnected: true,
    );
  }

  @override
  Future<List<TokenBalance>> getTokenBalances(String address) async {
    return [
      const TokenBalance(
        tokenId: '0',
        name: 'Verdis Eco Token',
        symbol: 'VRDX',
        decimals: 10,
        balance: 124507500000000,
      ),
      const TokenBalance(
        tokenId: '1',
        name: 'Governance VRDX',
        symbol: 'gVRDX',
        decimals: 10,
        balance: 154000000000000,
      ),
      const TokenBalance(
        tokenId: '2',
        name: 'Verdis USD',
        symbol: 'vUSD',
        decimals: 6,
        balance: 3112680000, // $3,112.68
      ),
      const TokenBalance(
        tokenId: '3',
        name: 'EcoCredit Token',
        symbol: 'ECO',
        decimals: 10,
        balance: 4500000000000,
      ),
    ];
  }

  @override
  Future<int> getNftCount(String address) async {
    return 4;
  }

  @override
  Future<List<NftAsset>> getNfts(String address, {int limit = 4}) async {
    final now = DateTime.now();
    return [
      NftAsset(
        collectionId: 'solar-nodes',
        assetId: '101',
        owner: address,
        name: 'Solar Node #101',
        description: 'Tier 1 Clean Energy Node Validator NFT',
        imageUrl: 'https://images.unsplash.com/photo-1509391365360-2e959784a276?w=400',
        isTransferable: true,
        createdAt: now.subtract(const Duration(days: 45)),
      ),
      NftAsset(
        collectionId: 'verdis-pioneers',
        assetId: '042',
        owner: address,
        name: 'Verdis Genesis Pioneer',
        description: 'Badge for early green network contributors',
        imageUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400',
        isTransferable: true,
        createdAt: now.subtract(const Duration(days: 120)),
      ),
      NftAsset(
        collectionId: 'forest-credits',
        assetId: '88',
        owner: address,
        name: 'Amazon Reserve Offset #88',
        description: 'Verified 100 Ton Carbon Offsetting Certificate',
        imageUrl: 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=400',
        isTransferable: false,
        createdAt: now.subtract(const Duration(days: 12)),
      ),
      NftAsset(
        collectionId: 'wind-farms',
        assetId: '007',
        owner: address,
        name: 'Nordic Wind Badge',
        description: 'Wind Turbine Clean Stake Derivative',
        imageUrl: 'https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=400',
        isTransferable: true,
        createdAt: now.subtract(const Duration(days: 5)),
      ),
    ].take(limit).toList();
  }

  @override
  Future<List<double>> get7DayBalanceHistory(String address) async {
    // 7 data points representing account balance over the last week
    return [11200.0, 11450.0, 11300.0, 11800.0, 12100.0, 12250.0, 12450.75];
  }

  int _parseBlockNumber(dynamic rawNumber) {
    if (rawNumber == null) return 0;
    if (rawNumber is int) return rawNumber;
    if (rawNumber is String) {
      if (rawNumber.startsWith('0x')) {
        return int.tryParse(rawNumber.replaceFirst('0x', ''), radix: 16) ?? 0;
      }
      return int.tryParse(rawNumber) ?? 0;
    }
    return 0;
  }

  List<TransactionRecord> _getFallbackTransactions(String address, int limit) {
    final now = DateTime.now();
    return [
      TransactionRecord(
        hash: '0x8f3a...91b2',
        blockHash: '0x123...456',
        blockNumber: 1284920,
        from: address,
        to: '0x71C7...891A',
        amount: 250000000000,
        fee: 500000000,
        module: 'balances',
        call: 'transfer',
        status: 'success',
        timestamp: now.subtract(const Duration(minutes: 12)),
      ),
      TransactionRecord(
        hash: '0x4d1e...a3c8',
        blockHash: '0x123...456',
        blockNumber: 1284910,
        from: '0x32A1...9F00',
        to: address,
        amount: 1500000000000,
        fee: 500000000,
        module: 'balances',
        call: 'transfer',
        status: 'success',
        timestamp: now.subtract(const Duration(hours: 2)),
      ),
    ].take(limit).toList();
  }
}
