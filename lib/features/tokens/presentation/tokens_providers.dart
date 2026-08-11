import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/network/rpc_client.dart';
import '../data/token_repository_impl.dart';
import '../domain/token_repository.dart';

/// Provider for TokenRepository
final tokenRepositoryProvider = Provider<TokenRepository>((ref) {
  final rpcClient = ref.watch(rpcClientProvider);
  return TokenRepositoryImpl(rpcClient);
});

/// Current wallet address provider
final userWalletAddressProvider = StateProvider<String>((ref) {
  return '0x7e8f9d0c1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d';
});

/// Token Search Query Provider
final tokenSearchQueryProvider = StateProvider<String>((ref) => '');

/// Token Sort Option Provider
final tokenSortOptionProvider = StateProvider<TokenSortOption>(
  (ref) => TokenSortOption.valueDesc,
);

/// All token balances provider (AsyncNotifier or FutureProvider)
final tokenListProvider =
    FutureProvider.autoDispose<List<TokenModel>>((ref) async {
  final repo = ref.watch(tokenRepositoryProvider);
  final address = ref.watch(userWalletAddressProvider);
  return repo.getTokenBalances(address);
});

/// Filtered & Sorted "My Tokens" List Provider
final filteredTokensProvider = Provider.autoDispose<AsyncValue<List<TokenModel>>>((ref) {
  final tokensAsync = ref.watch(tokenListProvider);
  final query = ref.watch(tokenSearchQueryProvider).trim().toLowerCase();
  final sortOption = ref.watch(tokenSortOptionProvider);

  return tokensAsync.whenData((tokens) {
    // 1. Filter out custom tokens for "My Tokens" tab, and apply search query
    final filtered = tokens.where((token) {
      if (token.isCustom) return false; // Non-custom tokens in "My Tokens"
      if (query.isEmpty) return true;
      return token.name.toLowerCase().contains(query) ||
          token.symbol.toLowerCase().contains(query) ||
          token.id.toLowerCase().contains(query);
    }).toList();

    // 2. Sort tokens
    switch (sortOption) {
      case TokenSortOption.valueDesc:
        filtered.sort((a, b) => b.usdValue.compareTo(a.usdValue));
        break;
      case TokenSortOption.valueAsc:
        filtered.sort((a, b) => a.usdValue.compareTo(b.usdValue));
        break;
      case TokenSortOption.nameAsc:
        filtered.sort((a, b) => a.name.toLowerCase().compareTo(b.name.toLowerCase()));
        break;
      case TokenSortOption.changeDesc:
        filtered.sort((a, b) => b.change24h.compareTo(a.change24h));
        break;
      case TokenSortOption.balanceDesc:
        filtered.sort((a, b) => b.balance.compareTo(a.balance));
        break;
    }

    return filtered;
  });
});

/// Filtered Custom Tokens List Provider
final customTokensProvider = Provider.autoDispose<AsyncValue<List<TokenModel>>>((ref) {
  final tokensAsync = ref.watch(tokenListProvider);
  final query = ref.watch(tokenSearchQueryProvider).trim().toLowerCase();

  return tokensAsync.whenData((tokens) {
    return tokens.where((token) {
      if (!token.isCustom) return false;
      if (query.isEmpty) return true;
      return token.name.toLowerCase().contains(query) ||
          token.symbol.toLowerCase().contains(query) ||
          (token.contractAddress?.toLowerCase().contains(query) ?? false);
    }).toList();
  });
});

/// Family Provider for Token Detail
final tokenDetailProvider = FutureProvider.family.autoDispose<TokenModel?, String>(
  (ref, tokenId) async {
    final repo = ref.watch(tokenRepositoryProvider);
    return repo.getTokenMetadata(tokenId);
  },
);

/// Family Provider for Token History
final tokenHistoryProvider =
    FutureProvider.family.autoDispose<List<TokenTransferHistory>, String>(
  (ref, tokenId) async {
    final repo = ref.watch(tokenRepositoryProvider);
    final address = ref.watch(userWalletAddressProvider);
    return repo.getTokenHistory(tokenId, address);
  },
);

/// Family Provider for Price Chart points
final tokenPriceChartProvider = FutureProvider.family
    .autoDispose<List<TokenPricePoint>, String>((ref, tokenId) async {
  final repo = ref.watch(tokenRepositoryProvider);
  return repo.getTokenPriceChart(tokenId, timeframe: '7d');
});

/// State notifier for Import Token Flow
class ImportTokenState {

  const ImportTokenState({
    this.isLoading = false,
    this.previewToken,
    this.errorMessage,
    this.isSuccess = false,
  });
  final bool isLoading;
  final TokenModel? previewToken;
  final String? errorMessage;
  final bool isSuccess;

  ImportTokenState copyWith({
    bool? isLoading,
    TokenModel? previewToken,
    String? errorMessage,
    bool? isSuccess,
  }) {
    return ImportTokenState(
      isLoading: isLoading ?? this.isLoading,
      previewToken: previewToken,
      errorMessage: errorMessage,
      isSuccess: isSuccess ?? this.isSuccess,
    );
  }
}

class ImportTokenNotifier extends StateNotifier<ImportTokenState> {

  ImportTokenNotifier(this._repository, this._walletAddress, this._ref)
      : super(const ImportTokenState());
  final TokenRepository _repository;
  final String _walletAddress;
  final Ref _ref;

  Future<void> fetchTokenMetadata(String input) async {
    if (input.trim().isEmpty) {
      state = const ImportTokenState();
      return;
    }

    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final token = await _repository.importToken(input, _walletAddress);
      state = ImportTokenState(
        isLoading: false,
        previewToken: token,
      );
    } catch (e) {
      state = const ImportTokenState(
        isLoading: false,
        errorMessage: 'Failed to fetch token metadata. Verify the ID or address.',
      );
    }
  }

  Future<bool> confirmImport() async {
    if (state.previewToken == null) return false;

    state = state.copyWith(isLoading: true);
    try {
      // Invalidate token list so UI refreshes
      _ref.invalidate(tokenListProvider);
      state = state.copyWith(isLoading: false, isSuccess: true);
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Failed to add token to wallet.',
      );
      return false;
    }
  }

  void reset() {
    state = const ImportTokenState();
  }
}

final importTokenNotifierProvider = StateNotifierProvider.autoDispose<
    ImportTokenNotifier, ImportTokenState>((ref) {
  final repo = ref.watch(tokenRepositoryProvider);
  final address = ref.watch(userWalletAddressProvider);
  return ImportTokenNotifier(repo, address, ref);
});
