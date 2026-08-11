/// Verdis Wallet Models — Plain Dart classes (no Freezed dependency)
library;

class WalletAccount {

  const WalletAccount({
    required this.address,
    required this.publicKey,
    this.name,
    this.privateKey,
    this.balance = 0,
    this.lockedBalance = 0,
    this.stakedBalance = 0,
    this.proxyAddress,
    this.createdAt,
  });

  factory WalletAccount.fromJson(Map<String, dynamic> json) => WalletAccount(
    address: json['address'] ?? '',
    publicKey: json['publicKey'] ?? '',
    name: json['name'],
    balance: json['balance'] ?? 0,
    lockedBalance: json['lockedBalance'] ?? 0,
    stakedBalance: json['stakedBalance'] ?? 0,
    proxyAddress: json['proxyAddress'],
  );
  final String address;
  final String publicKey;
  final String? name;
  final String? privateKey;
  final int balance;
  final int lockedBalance;
  final int stakedBalance;
  final String? proxyAddress;
  final DateTime? createdAt;

  Map<String, dynamic> toJson() => {
    'address': address,
    'publicKey': publicKey,
    'name': name,
    'balance': balance,
    'lockedBalance': lockedBalance,
    'stakedBalance': stakedBalance,
    'proxyAddress': proxyAddress,
    'createdAt': createdAt?.toIso8601String(),
  };
}

class TokenBalance {

  const TokenBalance({
    required this.tokenId,
    required this.name,
    required this.symbol,
    required this.decimals,
    required this.balance,
    this.metadata,
    this.owner,
    this.isFrozen = false,
    this.createdAt,
  });
  final String tokenId;
  final String name;
  final String symbol;
  final int decimals;
  final int balance;
  final String? metadata;
  final String? owner;
  final bool isFrozen;
  final DateTime? createdAt;
}

class NftAsset {

  const NftAsset({
    required this.collectionId,
    required this.assetId,
    required this.owner,
    this.name,
    this.description,
    this.imageUrl,
    this.attributes,
    this.isTransferable = false,
    this.createdAt,
  });
  final String collectionId;
  final String assetId;
  final String owner;
  final String? name;
  final String? description;
  final String? imageUrl;
  final Map<String, dynamic>? attributes;
  final bool isTransferable;
  final DateTime? createdAt;
}

class TransactionRecord {

  const TransactionRecord({
    required this.hash,
    required this.blockHash,
    required this.blockNumber,
    required this.from,
    required this.to,
    required this.amount,
    required this.fee,
    required this.module,
    required this.call,
    required this.status,
    this.timestamp,
    this.args,
  });
  final String hash;
  final String blockHash;
  final int blockNumber;
  final String from;
  final String to;
  final int amount;
  final int fee;
  final String module;
  final String call;
  final String status;
  final DateTime? timestamp;
  final Map<String, dynamic>? args;
}

class ValidatorInfo {

  const ValidatorInfo({
    required this.address,
    required this.name,
    required this.stake,
    required this.greenScore,
    required this.energySource,
    this.commission = 0,
    this.totalStaked = 0,
    this.validatorCount = 0,
    this.isActive = true,
    this.registeredAt,
  });
  final String address;
  final String name;
  final int stake;
  final int greenScore;
  final String energySource;
  final int commission;
  final int totalStaked;
  final int validatorCount;
  final bool isActive;
  final DateTime? registeredAt;
}

class DexPool {

  const DexPool({
    required this.poolId,
    required this.tokenA,
    required this.tokenB,
    required this.reserveA,
    required this.reserveB,
    this.feeRate = 0.003,
    this.totalVolume24h = 0,
    this.swapCount24h = 0,
    this.createdAt,
  });

  factory DexPool.fromJson(Map<String, dynamic> json) => DexPool(
    poolId: json['poolId'] ?? json['pool_id'] ?? 0,
    tokenA: json['tokenA'] ?? json['token_a'] ?? '',
    tokenB: json['tokenB'] ?? json['token_b'] ?? '',
    reserveA: json['reserveA'] ?? json['reserve_a'] ?? 0,
    reserveB: json['reserveB'] ?? json['reserve_b'] ?? 0,
    feeRate: (json['feeRate'] ?? json['fee_rate'] ?? 0.003).toDouble(),
    totalVolume24h: json['totalVolume24h'] ?? json['total_volume_24h'] ?? 0,
    swapCount24h: json['swapCount24h'] ?? json['swap_count_24h'] ?? 0,
  );
  final int poolId;
  final String tokenA;
  final String tokenB;
  final int reserveA;
  final int reserveB;
  final double feeRate;
  final int totalVolume24h;
  final int swapCount24h;
  final DateTime? createdAt;
}

class StakingPosition {

  const StakingPosition({
    required this.validatorAddress,
    required this.amount,
    required this.rewards,
    required this.stakedAt,
    this.status = StakingStatus.active,
  });
  final String validatorAddress;
  final int amount;
  final int rewards;
  final DateTime stakedAt;
  final StakingStatus status;
}

enum StakingStatus { active, unlocking, withdrawn }

class BlockInfo {

  const BlockInfo({
    required this.hash,
    required this.number,
    required this.parentHash,
    required this.timestamp,
    required this.validator,
    this.extrinsicCount = 0,
    this.extrinsics = const [],
  });
  final String hash;
  final int number;
  final String parentHash;
  final int timestamp;
  final String validator;
  final int extrinsicCount;
  final List<ExtrinsicInfo> extrinsics;
}

class ExtrinsicInfo {

  const ExtrinsicInfo({
    required this.hash,
    required this.signer,
    required this.module,
    required this.call,
    required this.fee,
    required this.isSuccess,
    this.args,
  });
  final String hash;
  final String signer;
  final String module;
  final String call;
  final int fee;
  final bool isSuccess;
  final Map<String, dynamic>? args;
}
