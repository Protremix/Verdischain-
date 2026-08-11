import 'package:verdis_wallet/shared/models/wallet_models.dart';

/// Point record for daily rewards
class DailyRewardPoint {

  const DailyRewardPoint({
    required this.date,
    required this.amount,
  });

  factory DailyRewardPoint.fromJson(Map<String, dynamic> json) {
    return DailyRewardPoint(
      date: DateTime.parse(json['date'] as String),
      amount: (json['amount'] as num).toDouble(),
    );
  }
  final DateTime date;
  final double amount;

  Map<String, dynamic> toJson() => {
        'date': date.toIso8601String(),
        'amount': amount,
      };
}

/// Aggregated staking rewards
class StakingRewards {

  const StakingRewards({
    required this.totalRewards,
    required this.claimableRewards,
    required this.pendingRewards,
    required this.dailyBreakdown,
  });

  factory StakingRewards.fromJson(Map<String, dynamic> json) {
    return StakingRewards(
      totalRewards: (json['totalRewards'] as num).toDouble(),
      claimableRewards: (json['claimableRewards'] as num).toDouble(),
      pendingRewards: (json['pendingRewards'] as num).toDouble(),
      dailyBreakdown: (json['dailyBreakdown'] as List<dynamic>?)
              ?.map((e) => DailyRewardPoint.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
  final double totalRewards;
  final double claimableRewards;
  final double pendingRewards;
  final List<DailyRewardPoint> dailyBreakdown;

  Map<String, dynamic> toJson() => {
        'totalRewards': totalRewards,
        'claimableRewards': claimableRewards,
        'pendingRewards': pendingRewards,
        'dailyBreakdown': dailyBreakdown.map((e) => e.toJson()).toList(),
      };
}

/// Staking transaction history item
enum StakingHistoryType { stake, unstake, claimReward }

class StakingHistoryItem {

  const StakingHistoryItem({
    required this.id,
    required this.txHash,
    required this.type,
    required this.amount,
    required this.validatorAddress,
    required this.validatorName,
    required this.timestamp,
    this.status = 'Success',
  });

  factory StakingHistoryItem.fromJson(Map<String, dynamic> json) {
    return StakingHistoryItem(
      id: json['id'] as String,
      txHash: json['txHash'] as String,
      type: StakingHistoryType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => StakingHistoryType.stake,
      ),
      amount: json['amount'] as int,
      validatorAddress: json['validatorAddress'] as String,
      validatorName: json['validatorName'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      status: json['status'] as String? ?? 'Success',
    );
  }
  final String id;
  final String txHash;
  final StakingHistoryType type;
  final int amount;
  final String validatorAddress;
  final String validatorName;
  final DateTime timestamp;
  final String status;

  Map<String, dynamic> toJson() => {
        'id': id,
        'txHash': txHash,
        'type': type.name,
        'amount': amount,
        'validatorAddress': validatorAddress,
        'validatorName': validatorName,
        'timestamp': timestamp.toIso8601String(),
        'status': status,
      };
}

/// Green score detail breakdown for validator
class GreenScoreDetail {

  const GreenScoreDetail({
    required this.validatorAddress,
    required this.score,
    required this.energySource,
    required this.efficiencyRating,
    required this.co2SavedKg,
    required this.renewablePercentage,
    required this.lastVerified,
    this.certifications = const [],
  });

  factory GreenScoreDetail.fromJson(Map<String, dynamic> json) {
    return GreenScoreDetail(
      validatorAddress: json['validatorAddress'] as String,
      score: json['score'] as int,
      energySource: json['energySource'] as String,
      efficiencyRating: (json['efficiencyRating'] as num).toDouble(),
      co2SavedKg: (json['co2SavedKg'] as num).toDouble(),
      renewablePercentage: (json['renewablePercentage'] as num).toDouble(),
      lastVerified: DateTime.parse(json['lastVerified'] as String),
      certifications: (json['certifications'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
    );
  }
  final String validatorAddress;
  final int score;
  final String energySource;
  final double efficiencyRating;
  final double co2SavedKg;
  final double renewablePercentage;
  final DateTime lastVerified;
  final List<String> certifications;

  Map<String, dynamic> toJson() => {
        'validatorAddress': validatorAddress,
        'score': score,
        'energySource': energySource,
        'efficiencyRating': efficiencyRating,
        'co2SavedKg': co2SavedKg,
        'renewablePercentage': renewablePercentage,
        'lastVerified': lastVerified.toIso8601String(),
        'certifications': certifications,
      };
}

/// Staking Repository Interface
abstract class StakingRepository {
  /// Fetches all active and registered validators in the network
  Future<List<ValidatorInfo>> getValidators();

  /// Fetches detailed validator info by address
  Future<ValidatorInfo?> getValidatorDetail(String address);

  /// Submits a stake extrinsic for the given validator and amount
  Future<String> stake({
    required String validatorAddress,
    required int amount,
  });

  /// Submits an unstake extrinsic for the given validator and amount
  Future<String> unstake({
    required String validatorAddress,
    required int amount,
  });

  /// Fetches all active staking positions for the given account
  Future<List<StakingPosition>> getStakingPositions(String accountAddress);

  /// Fetches reward metrics and historical breakdown
  Future<StakingRewards> getRewards(String accountAddress);

  /// Fetches historical staking transactions
  Future<List<StakingHistoryItem>> getStakingHistory(String accountAddress);

  /// Fetches detailed green score audit metrics for a validator
  Future<GreenScoreDetail> getGreenScore(String validatorAddress);

  /// Claims all claimable rewards for account
  Future<String> claimRewards(String accountAddress);
}
