import 'package:flutter/foundation.dart';

/// Represents a fungible token on the Verdis network or imported custom token
@immutable
class TokenModel {

  const TokenModel({
    required this.id,
    required this.name,
    required this.symbol,
    required this.decimals,
    required this.balance,
    this.usdPrice = 0.0,
    this.change24h = 0.0,
    this.supply = 0.0,
    this.holderCount = 0,
    this.isCustom = false,
    this.iconUrl,
    this.gradientColors = const [0xFF00FF88, 0xFF00E676],
    this.contractAddress,
    this.isFrozen = false,
    this.lastUpdated,
  });

  factory TokenModel.fromJson(Map<String, dynamic> json) {
    return TokenModel(
      id: json['id'] as String,
      name: json['name'] as String,
      symbol: json['symbol'] as String,
      decimals: (json['decimals'] as num?)?.toInt() ?? 9,  // Verdis uses 9 decimals
      balance: (json['balance'] as num?)?.toDouble() ?? 0.0,
      usdPrice: (json['usdPrice'] as num?)?.toDouble() ?? 0.0,
      change24h: (json['change24h'] as num?)?.toDouble() ?? 0.0,
      supply: (json['supply'] as num?)?.toDouble() ?? 0.0,
      holderCount: (json['holderCount'] as num?)?.toInt() ?? 0,
      isCustom: json['isCustom'] as bool? ?? false,
      iconUrl: json['iconUrl'] as String?,
      gradientColors: (json['gradientColors'] as List<dynamic>?)
              ?.map((e) => (e as num).toInt())
              .toList() ??
          const [0xFF00FF88, 0xFF00E676],
      contractAddress: json['contractAddress'] as String?,
      isFrozen: json['isFrozen'] as bool? ?? false,
      lastUpdated: json['lastUpdated'] != null
          ? DateTime.tryParse(json['lastUpdated'] as String)
          : null,
    );
  }
  final String id;
  final String name;
  final String symbol;
  final int decimals;
  final double balance;
  final double usdPrice;
  final double change24h;
  final double supply;
  final int holderCount;
  final bool isCustom;
  final String? iconUrl;
  final List<int> gradientColors;
  final String? contractAddress;
  final bool isFrozen;
  final DateTime? lastUpdated;

  double get usdValue => balance * usdPrice;

  TokenModel copyWith({
    String? id,
    String? name,
    String? symbol,
    int? decimals,
    double? balance,
    double? usdPrice,
    double? change24h,
    double? supply,
    int? holderCount,
    bool? isCustom,
    String? iconUrl,
    List<int>? gradientColors,
    String? contractAddress,
    bool? isFrozen,
    DateTime? lastUpdated,
  }) {
    return TokenModel(
      id: id ?? this.id,
      name: name ?? this.name,
      symbol: symbol ?? this.symbol,
      decimals: decimals ?? this.decimals,
      balance: balance ?? this.balance,
      usdPrice: usdPrice ?? this.usdPrice,
      change24h: change24h ?? this.change24h,
      supply: supply ?? this.supply,
      holderCount: holderCount ?? this.holderCount,
      isCustom: isCustom ?? this.isCustom,
      iconUrl: iconUrl ?? this.iconUrl,
      gradientColors: gradientColors ?? this.gradientColors,
      contractAddress: contractAddress ?? this.contractAddress,
      isFrozen: isFrozen ?? this.isFrozen,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'symbol': symbol,
      'decimals': decimals,
      'balance': balance,
      'usdPrice': usdPrice,
      'change24h': change24h,
      'supply': supply,
      'holderCount': holderCount,
      'isCustom': isCustom,
      'iconUrl': iconUrl,
      'gradientColors': gradientColors,
      'contractAddress': contractAddress,
      'isFrozen': isFrozen,
      'lastUpdated': lastUpdated?.toIso8601String(),
    };
  }
}

/// Token transfer transaction history record
@immutable
class TokenTransferHistory {

  const TokenTransferHistory({
    required this.id,
    required this.tokenId,
    required this.type,
    required this.amount,
    required this.counterparty,
    required this.timestamp,
    required this.status,
    required this.hash,
  });
  final String id;
  final String tokenId;
  final String type; // 'send' or 'receive'
  final double amount;
  final String counterparty;
  final DateTime timestamp;
  final String status; // 'confirmed', 'pending', 'failed'
  final String hash;
}

/// Price historical point for charts
@immutable
class TokenPricePoint {

  const TokenPricePoint({
    required this.timestamp,
    required this.price,
  });
  final DateTime timestamp;
  final double price;
}

/// Sorting options for token lists
enum TokenSortOption {
  valueDesc,
  valueAsc,
  nameAsc,
  changeDesc,
  balanceDesc,
}

/// Token repository abstract interface
abstract class TokenRepository {
  /// Fetch all token balances for a given wallet address
  Future<List<TokenModel>> getTokenBalances(String walletAddress);

  /// Fetch single token metadata by token ID or address
  Future<TokenModel?> getTokenMetadata(String tokenId);

  /// Fetch transfer transaction history for a token
  Future<List<TokenTransferHistory>> getTokenHistory(
    String tokenId,
    String walletAddress,
  );

  /// Fetch price history data for price chart
  Future<List<TokenPricePoint>> getTokenPriceChart(
    String tokenId, {
    String timeframe = '7d',
  });

  /// Import a custom token by contract address or token ID
  Future<TokenModel> importToken(String tokenIdOrAddress, String walletAddress);

  /// Transfer token to another address
  Future<String> transferToken({
    required String tokenId,
    required String recipient,
    required double amount,
    required String senderAddress,
  });
}
