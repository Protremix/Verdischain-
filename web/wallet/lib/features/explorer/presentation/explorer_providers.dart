import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/network/rpc_client.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import '../data/explorer_repository_impl.dart';
import '../domain/explorer_repository.dart';

/// Provider for the Explorer Repository
final explorerRepositoryProvider = Provider<ExplorerRepository>((ref) {
  final rpcClient = ref.watch(rpcClientProvider);
  return ExplorerRepositoryImpl(rpcClient);
});

/// Network Info Provider
final networkInfoProvider = FutureProvider<NetworkInfoData>((ref) async {
  final repository = ref.watch(explorerRepositoryProvider);
  return repository.getNetworkInfo();
});

/// Blocks Provider (Supports infinite scroll / pagination)
class BlocksNotifier extends StateNotifier<AsyncValue<List<BlockInfo>>> {

  BlocksNotifier(this._repository) : super(const AsyncValue.loading()) {
    loadInitial();
  }
  final ExplorerRepository _repository;
  int _currentPage = 0;
  bool _hasMore = true;
  bool _isLoadingMore = false;

  Future<void> loadInitial() async {
    state = const AsyncValue.loading();
    try {
      _currentPage = 0;
      final blocks = await _repository.getLatestBlocks(page: 0, limit: 20);
      _hasMore = blocks.length >= 20;
      state = AsyncValue.data(blocks);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> loadMore() async {
    if (!_hasMore || _isLoadingMore) return;
    final currentBlocks = state.value;
    if (currentBlocks == null) return;

    _isLoadingMore = true;
    try {
      _currentPage++;
      final newBlocks = await _repository.getLatestBlocks(page: _currentPage, limit: 20);
      if (newBlocks.isEmpty) {
        _hasMore = false;
      } else {
        _hasMore = newBlocks.length >= 20;
        state = AsyncValue.data([...currentBlocks, ...newBlocks]);
      }
    } catch (_) {
      _currentPage--;
    } finally {
      _isLoadingMore = false;
    }
  }

  Future<void> refresh() async {
    await loadInitial();
  }

  bool get hasMore => _hasMore;
  bool get isLoadingMore => _isLoadingMore;
}

final blocksProvider = StateNotifierProvider<BlocksNotifier, AsyncValue<List<BlockInfo>>>((ref) {
  final repository = ref.watch(explorerRepositoryProvider);
  return BlocksNotifier(repository);
});

/// Transactions Provider
class TxsNotifier extends StateNotifier<AsyncValue<List<TransactionRecord>>> {

  TxsNotifier(this._repository) : super(const AsyncValue.loading()) {
    loadInitial();
  }
  final ExplorerRepository _repository;
  int _currentPage = 0;

  Future<void> loadInitial() async {
    state = const AsyncValue.loading();
    try {
      _currentPage = 0;
      final txs = await _repository.getLatestTransactions(page: 0, limit: 20);
      state = AsyncValue.data(txs);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> loadMore() async {
    final current = state.value;
    if (current == null) return;
    try {
      _currentPage++;
      final newTxs = await _repository.getLatestTransactions(page: _currentPage, limit: 20);
      if (newTxs.isNotEmpty) {
        state = AsyncValue.data([...current, ...newTxs]);
      }
    } catch (_) {
      _currentPage--;
    }
  }

  Future<void> refresh() async {
    await loadInitial();
  }
}

final txsProvider = StateNotifierProvider<TxsNotifier, AsyncValue<List<TransactionRecord>>>((ref) {
  final repository = ref.watch(explorerRepositoryProvider);
  return TxsNotifier(repository);
});

/// Validator Sort Criteria
enum ValidatorSortBy { score, stake }

final validatorSortProvider = StateProvider<ValidatorSortBy>((ref) => ValidatorSortBy.score);

/// Validators Provider (sorted based on sort criteria)
final validatorsProvider = FutureProvider<List<ValidatorInfo>>((ref) async {
  final repository = ref.watch(explorerRepositoryProvider);
  final sortBy = ref.watch(validatorSortProvider);

  final list = await repository.getValidators();
  final sortedList = List<ValidatorInfo>.from(list);

  if (sortBy == ValidatorSortBy.score) {
    sortedList.sort((a, b) => b.greenScore.compareTo(a.greenScore));
  } else {
    sortedList.sort((a, b) => b.stake.compareTo(a.stake));
  }

  return sortedList;
});

/// Search Query State
final searchQueryProvider = StateProvider<String>((ref) => '');

/// Search Results Provider
final searchProvider = FutureProvider<SearchResultData?>((ref) async {
  final query = ref.watch(searchQueryProvider).trim();
  if (query.isEmpty) return null;

  final repository = ref.watch(explorerRepositoryProvider);
  return repository.search(query);
});
