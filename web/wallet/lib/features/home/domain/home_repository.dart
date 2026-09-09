import 'package:verdis_wallet/shared/models/wallet_models.dart';

/// Data class representing blockchain network status details
class NetworkStatusData {

  const NetworkStatusData({
    required this.blockHeight,
    required this.peersCount,
    required this.epochProgress,
    this.currentEpoch = 42,
    required this.validatorCount,
    required this.consensusInfo,
    this.isConnected = true,
  });
  final int blockHeight;
  final int peersCount;
  final double epochProgress; // 0.0 to 1.0
  final int currentEpoch;
  final int validatorCount;
  final String consensusInfo;
  final bool isConnected;
}

/// Data class representing staking summary for the current user account
class StakingSummaryData { // e.g., 0.142 for 14.2%

  const StakingSummaryData({
    required this.totalStaked,
    required this.activeValidators,
    required this.rewardsEarned,
    required this.apyEstimate,
  });
  final int totalStaked; // In base units (planck/VRDX)
  final int activeValidators;
  final int rewardsEarned;
  final double apyEstimate;
}

/// Domain repository interface for the Home feature
abstract class HomeRepository {
  /// Get total account balance in base units
  Future<int> getBalance(String address);

  /// Get recent transaction history for address
  Future<List<TransactionRecord>> getRecentTransactions(String address, {int limit = 5});

  /// Get staking overview summary
  Future<StakingSummaryData> getStakingSummary(String address);

  /// Get network health and consensus status
  Future<NetworkStatusData> getNetworkStatus();

  /// Get token balances associated with the account
  Future<List<TokenBalance>> getTokenBalances(String address);

  /// Get total count of NFTs owned by address
  Future<int> getNftCount(String address);

  /// Get list of NFT assets for preview
  Future<List<NftAsset>> getNfts(String address, {int limit = 4});

  /// Get 7-day balance history for graph display
  Future<List<double>> get7DayBalanceHistory(String address);
}
