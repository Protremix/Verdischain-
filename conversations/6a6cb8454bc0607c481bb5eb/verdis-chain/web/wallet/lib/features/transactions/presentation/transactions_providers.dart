import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:verdis_wallet/core/network/rpc_client.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import '../data/transaction_repository_impl.dart';
import '../domain/transaction_repository.dart';

/// User's current primary wallet address
final userWalletAddressProvider = StateProvider<String>((ref) {
  return 'verdis1q83f7k94a9z2m3v4x5y6z7w8v9u0a1b2c3d4e5f';
});

/// User's current available VRDX balance
final userWalletBalanceProvider = StateProvider<double>((ref) {
  return 1250.75;
});

/// Transaction repository provider
final transactionRepositoryProvider = Provider<TransactionRepository>((ref) {
  final rpc = ref.watch(rpcClientProvider);
  final address = ref.watch(userWalletAddressProvider);
  return TransactionRepositoryImpl(rpc, userAddress: address);
});

/// Selected filter tab for transaction history
final selectedFilterProvider = StateProvider<String>((ref) => 'All');

/// Selected fee speed option ('slow' | 'standard' | 'fast')
final selectedFeeSpeedProvider = StateProvider<String>((ref) => 'standard');

/// Fee estimate provider
final feeEstimateProvider =
    FutureProvider.family<double, Map<String, dynamic>>((ref, params) async {
  final repo = ref.watch(transactionRepositoryProvider);
  final recipient = params['recipient'] as String? ?? '';
  final amount = (params['amount'] as num?)?.toDouble() ?? 0.0;
  final speed = params['speed'] as String? ?? 'standard';

  return repo.estimateFee(
    recipient: recipient,
    amount: amount,
    speed: speed,
  );
});

/// Transaction history notifier
class TransactionHistoryNotifier
    extends StateNotifier<AsyncValue<List<TransactionRecord>>> {

  TransactionHistoryNotifier(this._repository, this._filter)
      : super(const AsyncValue.loading()) {
    fetchHistory();
  }
  final TransactionRepository _repository;
  final String _filter;
  int _currentPage = 1;
  bool _hasMore = true;

  bool get hasMore => _hasMore;

  Future<void> fetchHistory({bool isRefresh = false}) async {
    if (isRefresh) {
      _currentPage = 1;
      _hasMore = true;
      state = const AsyncValue.loading();
    }

    try {
      final items = await _repository.getTransactionHistory(
        filter: _filter,
        page: _currentPage,
        limit: 20,
      );

      if (items.length < 20) {
        _hasMore = false;
      }

      if (isRefresh || state.value == null) {
        state = AsyncValue.data(items);
      } else {
        final current = state.value!;
        state = AsyncValue.data([...current, ...items]);
      }
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> loadMore() async {
    if (!_hasMore || state.isLoading) return;
    _currentPage++;
    await fetchHistory(isRefresh: false);
  }
}

/// Provider for transaction history list
final transactionHistoryProvider = StateNotifierProvider<
    TransactionHistoryNotifier, AsyncValue<List<TransactionRecord>>>((ref) {
  final repo = ref.watch(transactionRepositoryProvider);
  final filter = ref.watch(selectedFilterProvider);
  return TransactionHistoryNotifier(repo, filter);
});

/// Provider for single transaction detail
final transactionDetailProvider =
    FutureProvider.family<TransactionRecord?, String>((ref, txHash) async {
  final repo = ref.watch(transactionRepositoryProvider);
  return repo.getTransactionDetail(txHash);
});

/// State representation for Send Transaction flow
class SendTransactionState {

  const SendTransactionState({
    this.isSubmitting = false,
    this.txHash,
    this.blockNumber,
    this.errorMessage,
    this.isSuccess = false,
  });
  final bool isSubmitting;
  final String? txHash;
  final int? blockNumber;
  final String? errorMessage;
  final bool isSuccess;

  SendTransactionState copyWith({
    bool? isSubmitting,
    String? txHash,
    int? blockNumber,
    String? errorMessage,
    bool? isSuccess,
  }) {
    return SendTransactionState(
      isSubmitting: isSubmitting ?? this.isSubmitting,
      txHash: txHash ?? this.txHash,
      blockNumber: blockNumber ?? this.blockNumber,
      errorMessage: errorMessage ?? this.errorMessage,
      isSuccess: isSuccess ?? this.isSuccess,
    );
  }
}

/// StateNotifier handling transfer submission logic
class SendTransactionNotifier extends StateNotifier<SendTransactionState> {

  SendTransactionNotifier(this._repository, this._ref)
      : super(const SendTransactionState());
  final TransactionRepository _repository;
  final Ref _ref;

  Future<bool> sendTransfer({
    required String recipient,
    required double amount,
    required String speed,
  }) async {
    state = state.copyWith(
      isSubmitting: true,
      errorMessage: null,
      isSuccess: false,
    );

    try {
      final txHash = await _repository.sendTransfer(
        recipient: recipient,
        amount: amount,
        feeLevel: speed,
      );

      // Deduct balance locally for instant feedback
      final currentBal = _ref.read(userWalletBalanceProvider);
      final fee = await _repository.estimateFee(
        recipient: recipient,
        amount: amount,
        speed: speed,
      );
      final newBal = (currentBal - amount - fee).clamp(0.0, double.infinity);
      _ref.read(userWalletBalanceProvider.notifier).state = newBal;

      // Refresh transaction history
      await _ref.read(transactionHistoryProvider.notifier).fetchHistory(isRefresh: true);

      state = SendTransactionState(
        isSubmitting: false,
        txHash: txHash,
        blockNumber: 1284525,
        isSuccess: true,
      );
      return true;
    } catch (e) {
      state = SendTransactionState(
        isSubmitting: false,
        errorMessage: e.toString().replaceAll('Exception: ', ''),
        isSuccess: false,
      );
      return false;
    }
  }

  void reset() {
    state = const SendTransactionState();
  }
}

/// Provider for Send Transaction controller
final sendTransactionProvider =
    StateNotifierProvider<SendTransactionNotifier, SendTransactionState>((ref) {
  final repo = ref.watch(transactionRepositoryProvider);
  return SendTransactionNotifier(repo, ref);
});
