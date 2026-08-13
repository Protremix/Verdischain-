import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/network/rpc_client.dart';
import '../../tokens/presentation/tokens_providers.dart';
import '../data/nft_repository_impl.dart';
import '../domain/nft_repository.dart';

/// Provider for NftRepository
final nftRepositoryProvider = Provider<NftRepository>((ref) {
  final rpcClient = ref.watch(rpcClientProvider);
  return NftRepositoryImpl(rpcClient);
});

/// Search Query for NFTs
final nftSearchQueryProvider = StateProvider<String>((ref) => '');

/// Selected Collection Filter (null = show all)
final nftSelectedCollectionFilterProvider = StateProvider<String?>((ref) => null);

/// Sort Option for NFT assets
final nftSortOptionProvider = StateProvider<NftSortOption>(
  (ref) => NftSortOption.recentlyMinted,
);

/// Collections List Provider
final nftCollectionsProvider =
    FutureProvider.autoDispose<List<NftCollectionModel>>((ref) async {
  final repo = ref.watch(nftRepositoryProvider);
  final owner = ref.watch(userWalletAddressProvider);
  return repo.getNftCollections(ownerAddress: owner);
});

/// All User NFT Assets Provider
final nftAssetsProvider =
    FutureProvider.autoDispose<List<NftAssetModel>>((ref) async {
  final repo = ref.watch(nftRepositoryProvider);
  final owner = ref.watch(userWalletAddressProvider);
  return repo.getNftAssets(ownerAddress: owner);
});

/// Filtered & Sorted NFT Assets Provider
final filteredNftAssetsProvider = Provider.autoDispose<AsyncValue<List<NftAssetModel>>>((ref) {
  final assetsAsync = ref.watch(nftAssetsProvider);
  final query = ref.watch(nftSearchQueryProvider).trim().toLowerCase();
  final collectionFilter = ref.watch(nftSelectedCollectionFilterProvider);
  final sortOption = ref.watch(nftSortOptionProvider);

  return assetsAsync.whenData((assets) {
    // 1. Filter by collection & search text
    final list = assets.where((asset) {
      if (collectionFilter != null && asset.collectionId != collectionFilter) {
        return false;
      }
      if (query.isEmpty) return true;
      return asset.name.toLowerCase().contains(query) ||
          asset.collectionName.toLowerCase().contains(query) ||
          asset.assetId.toLowerCase().contains(query);
    }).toList();

    // 2. Apply sorting
    switch (sortOption) {
      case NftSortOption.recentlyMinted:
        list.sort((a, b) {
          final dateA = a.mintDate ?? DateTime(2020);
          final dateB = b.mintDate ?? DateTime(2020);
          return dateB.compareTo(dateA);
        });
        break;
      case NftSortOption.nameAsc:
        list.sort((a, b) => a.name.toLowerCase().compareTo(b.name.toLowerCase()));
        break;
      case NftSortOption.rarityRankAsc:
        list.sort((a, b) {
          final rankA = a.rarityRank ?? 999999;
          final rankB = b.rarityRank ?? 999999;
          return rankA.compareTo(rankB);
        });
        break;
      case NftSortOption.assetIdAsc:
        list.sort((a, b) => a.assetId.compareTo(b.assetId));
        break;
    }

    return list;
  });
});

/// Family Provider for Single NFT Detail
final nftDetailProvider = FutureProvider.family.autoDispose<NftAssetModel?,
    ({String collectionId, String assetId})>((ref, arg) async {
  final repo = ref.watch(nftRepositoryProvider);
  return repo.getNftMetadata(arg.collectionId, arg.assetId);
});

/// NFT Global Activity / History Provider
final nftActivityProvider =
    FutureProvider.autoDispose<List<NftActivityModel>>((ref) async {
  final repo = ref.watch(nftRepositoryProvider);
  return repo.getNftActivity();
});

/// State for Transfer NFT operation
class NftTransferState {

  const NftTransferState({
    this.isLoading = false,
    this.txHash,
    this.errorMessage,
  });
  final bool isLoading;
  final String? txHash;
  final String? errorMessage;

  NftTransferState copyWith({
    bool? isLoading,
    String? txHash,
    String? errorMessage,
  }) {
    return NftTransferState(
      isLoading: isLoading ?? this.isLoading,
      txHash: txHash ?? this.txHash,
      errorMessage: errorMessage,
    );
  }
}

class NftTransferNotifier extends StateNotifier<NftTransferState> {

  NftTransferNotifier(this._repository, this._ref)
      : super(const NftTransferState());
  final NftRepository _repository;
  final Ref _ref;

  Future<bool> transferNft({
    required String collectionId,
    required String assetId,
    required String recipient,
  }) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final sender = _ref.read(userWalletAddressProvider);
      final hash = await _repository.transferNft(
        collectionId: collectionId,
        assetId: assetId,
        recipient: recipient,
        senderAddress: sender,
      );

      _ref.invalidate(nftAssetsProvider);
      state = NftTransferState(isLoading: false, txHash: hash);
      return true;
    } catch (e) {
      state = NftTransferState(
        isLoading: false,
        errorMessage: 'Failed to complete NFT transfer: $e',
      );
      return false;
    }
  }
}

final nftTransferNotifierProvider =
    StateNotifierProvider.autoDispose<NftTransferNotifier, NftTransferState>((ref) {
  final repo = ref.watch(nftRepositoryProvider);
  return NftTransferNotifier(repo, ref);
});
