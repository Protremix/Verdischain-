import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:verdis_wallet/core/network/rpc_client.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import '../domain/home_repository.dart';

/// Real RPC-backed home repository — no hardcoded/demo data.
class HomeRepositoryImpl implements HomeRepository {

  HomeRepositoryImpl(this._rpcClient);
  final RpcClient _rpcClient;

  static const String _txRelayUrl = 'https://verdischain.com/api/tx-relay';

  @override
  Future<int> getBalance(String address) async {
    if (address.isEmpty) return 0;

    // Try TX Relay balance endpoint (uses Substrate query internally)
    try {
      final response = await http.post(
        Uri.parse(_txRelayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'action': 'balance', 'address': address}),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['ok'] == true) {
          final balance = data['data']?['balance'];
          if (balance is int) return balance;
          if (balance is String) return int.tryParse(balance) ?? 0;
        }
      }
    } catch (_) {}

    return 0;
  }

  @override
  Future<List<TransactionRecord>> getRecentTransactions(String address, {int limit = 5}) async {
    // No fake transactions — return empty list until real tx history API is available
    return [];
  }

  @override
  Future<StakingSummaryData> getStakingSummary(String address) async {
    // Query TX Relay for real validator/staking data
    try {
      final response = await http.post(
        Uri.parse(_txRelayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'action': 'validators'}),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['ok'] == true) {
          final validators = data['data']?['validators'] as List<dynamic>? ?? [];
          int activeCount = 0;
          int totalStaked = 0;
          for (final v in validators) {
            final vMap = v as Map<String, dynamic>;
            if (vMap['isActive'] == true) activeCount++;
            totalStaked += (vMap['stake'] as num? ?? 0).toInt();
          }
          return StakingSummaryData(
            totalStaked: totalStaked,
            activeValidators: activeCount,
            rewardsEarned: 0,
            apyEstimate: 0.0,
          );
        }
      }
    } catch (_) {}

    return const StakingSummaryData(
      totalStaked: 0,
      activeValidators: 0,
      rewardsEarned: 0,
      apyEstimate: 0.0,
    );
  }

  @override
  Future<NetworkStatusData> getNetworkStatus() async {
    int blockHeight = 0;
    int peers = 0;
    bool isSyncing = false;
    int validatorCount = 0;

    // 1. Get current block height
    try {
      final header = await _rpcClient.getHeader();
      final parsedNum = _parseBlockNumber(header['number']);
      if (parsedNum > 0) blockHeight = parsedNum;
    } catch (_) {}

    // 2. Get peer count and sync status from system_health
    try {
      final health = await _rpcClient.getHealth();
      if (health.containsKey('peers')) {
        peers = (health['peers'] as num).toInt();
      }
      if (health.containsKey('isSyncing')) {
        isSyncing = health['isSyncing'] as bool;
      }
    } catch (_) {}

    // 3. Get validator count from TX Relay
    try {
      final response = await http.post(
        Uri.parse(_txRelayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'action': 'validators'}),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['ok'] == true) {
          final validators = data['data']?['validators'] as List<dynamic>?;
          if (validators != null) {
            validatorCount = validators.length;
          }
        }
      }
    } catch (_) {}

    // 4. Calculate epoch progress — actual EpochDuration is 20 blocks
    const epochDuration = 20;
    final epochProgress = blockHeight > 0 ? (blockHeight % epochDuration) / epochDuration.toDouble() : 0.0;
    final currentEpoch = blockHeight > 0 ? (blockHeight / epochDuration).floor() : 0;

    // Node is connected if it has a block height and is not actively syncing
    // (or if it is syncing but already has blocks — initial sync in progress)
    final isConnected = blockHeight > 0;

    return NetworkStatusData(
      blockHeight: blockHeight,
      peersCount: peers,
      epochProgress: epochProgress,
      currentEpoch: currentEpoch,
      validatorCount: validatorCount,
      consensusInfo: 'BABE/GRANDPA + DPoS',
      isConnected: isConnected,
      isSyncing: isSyncing,
    );
  }

  @override
  Future<List<TokenBalance>> getTokenBalances(String address) async {
    // No fake tokens — return empty list
    return [];
  }

  @override
  Future<int> getNftCount(String address) async {
    return 0;
  }

  @override
  Future<List<NftAsset>> getNfts(String address, {int limit = 4}) async {
    // No fake NFTs — return empty list
    return [];
  }

  @override
  Future<List<double>> get7DayBalanceHistory(String address) async {
    // Show current balance as a flat line — no historical price API available yet
    if (address.isEmpty) return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
    final balance = await getBalance(address);
    final vrdxBalance = balance / 1e9;
    return List.filled(7, vrdxBalance);
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
}
