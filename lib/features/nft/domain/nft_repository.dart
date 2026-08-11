import 'package:flutter/foundation.dart';

/// Attribute / Trait metadata for an NFT asset
@immutable
class NftAttributeModel {

  const NftAttributeModel({
    required this.traitType,
    required this.value,
    this.rarityPercent,
  });

  factory NftAttributeModel.fromJson(Map<String, dynamic> json) =>
      NftAttributeModel(
        traitType: json['traitType'] as String? ?? 'Trait',
        value: json['value'] as String? ?? '',
        rarityPercent: (json['rarityPercent'] as num?)?.toDouble(),
      );
  final String traitType;
  final String value;
  final double? rarityPercent;

  Map<String, dynamic> toJson() => {
        'traitType': traitType,
        'value': value,
        'rarityPercent': rarityPercent,
      };
}

/// Collection metadata model for NFTs
@immutable
class NftCollectionModel {

  const NftCollectionModel({
    required this.id,
    required this.name,
    required this.symbol,
    required this.description,
    required this.imageUrl,
    this.bannerUrl,
    this.itemCount = 0,
    this.ownerCount = 0,
    this.floorPrice = 0.0,
    this.totalVolume = 0.0,
  });

  factory NftCollectionModel.fromJson(Map<String, dynamic> json) =>
      NftCollectionModel(
        id: json['id'] as String,
        name: json['name'] as String,
        symbol: json['symbol'] as String,
        description: json['description'] as String? ?? '',
        imageUrl: json['imageUrl'] as String? ?? '',
        bannerUrl: json['bannerUrl'] as String?,
        itemCount: (json['itemCount'] as num?)?.toInt() ?? 0,
        ownerCount: (json['ownerCount'] as num?)?.toInt() ?? 0,
        floorPrice: (json['floorPrice'] as num?)?.toDouble() ?? 0.0,
        totalVolume: (json['totalVolume'] as num?)?.toDouble() ?? 0.0,
      );
  final String id;
  final String name;
  final String symbol;
  final String description;
  final String imageUrl;
  final String? bannerUrl;
  final int itemCount;
  final int ownerCount;
  final double floorPrice;
  final double totalVolume;

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'symbol': symbol,
        'description': description,
        'imageUrl': imageUrl,
        'bannerUrl': bannerUrl,
        'itemCount': itemCount,
        'ownerCount': ownerCount,
        'floorPrice': floorPrice,
        'totalVolume': totalVolume,
      };
}

/// Single NFT asset model
@immutable
class NftAssetModel {

  const NftAssetModel({
    required this.collectionId,
    required this.collectionName,
    required this.assetId,
    required this.name,
    required this.description,
    required this.imageUrl,
    required this.ownerAddress,
    required this.creatorAddress,
    this.attributes = const [],
    this.isTransferable = true,
    this.rarityScore,
    this.rarityRank,
    this.mintDate,
  });

  factory NftAssetModel.fromJson(Map<String, dynamic> json) => NftAssetModel(
        collectionId: json['collectionId'] as String,
        collectionName: json['collectionName'] as String? ?? 'Collection',
        assetId: json['assetId'] as String,
        name: json['name'] as String,
        description: json['description'] as String? ?? '',
        imageUrl: json['imageUrl'] as String? ?? '',
        ownerAddress: json['ownerAddress'] as String? ?? '',
        creatorAddress: json['creatorAddress'] as String? ?? '',
        attributes: (json['attributes'] as List<dynamic>?)
                ?.map((e) => NftAttributeModel.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
        isTransferable: json['isTransferable'] as bool? ?? true,
        rarityScore: (json['rarityScore'] as num?)?.toDouble(),
        rarityRank: (json['rarityRank'] as num?)?.toInt(),
        mintDate: json['mintDate'] != null
            ? DateTime.tryParse(json['mintDate'] as String)
            : null,
      );
  final String collectionId;
  final String collectionName;
  final String assetId;
  final String name;
  final String description;
  final String imageUrl;
  final String ownerAddress;
  final String creatorAddress;
  final List<NftAttributeModel> attributes;
  final bool isTransferable;
  final double? rarityScore;
  final int? rarityRank;
  final DateTime? mintDate;

  Map<String, dynamic> toJson() => {
        'collectionId': collectionId,
        'collectionName': collectionName,
        'assetId': assetId,
        'name': name,
        'description': description,
        'imageUrl': imageUrl,
        'ownerAddress': ownerAddress,
        'creatorAddress': creatorAddress,
        'attributes': attributes.map((a) => a.toJson()).toList(),
        'isTransferable': isTransferable,
        'rarityScore': rarityScore,
        'rarityRank': rarityRank,
        'mintDate': mintDate?.toIso8601String(),
      };
}

/// Transaction / Activity record for NFTs
@immutable
class NftActivityModel {

  const NftActivityModel({
    required this.id,
    required this.collectionId,
    required this.assetId,
    required this.assetName,
    required this.type,
    required this.from,
    required this.to,
    this.price,
    required this.timestamp,
    required this.txHash,
  });
  final String id;
  final String collectionId;
  final String assetId;
  final String assetName;
  final String type; // 'transfer', 'mint', 'sale', 'list'
  final String from;
  final String to;
  final double? price;
  final DateTime timestamp;
  final String txHash;
}

/// Sorting options for NFT gallery
enum NftSortOption {
  recentlyMinted,
  nameAsc,
  rarityRankAsc,
  assetIdAsc,
}

/// NFT Repository abstract interface
abstract class NftRepository {
  /// Fetch NFT collections owned or existing on chain
  Future<List<NftCollectionModel>> getNftCollections({String? ownerAddress});

  /// Fetch list of NFT assets for owner or specific collection
  Future<List<NftAssetModel>> getNftAssets({
    String? ownerAddress,
    String? collectionId,
  });

  /// Fetch single NFT metadata by collection ID and asset ID
  Future<NftAssetModel?> getNftMetadata(
    String collectionId,
    String assetId,
  );

  /// Fetch history / activity logs for NFT collections or assets
  Future<List<NftActivityModel>> getNftActivity({
    String? collectionId,
    String? assetId,
  });

  /// Transfer NFT to recipient address on chain
  Future<String> transferNft({
    required String collectionId,
    required String assetId,
    required String recipient,
    required String senderAddress,
  });
}
