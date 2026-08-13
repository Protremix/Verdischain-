import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/network/rpc_client.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import '../data/home_repository_impl.dart';
import '../domain/home_repository.dart';

/// Active wallet address provider
final selectedAddressProvider = StateProvider<String>((ref) {
  return '0x71C7656EC7ab88b098defB751B7401B5f6d8976F';
});

/// Home Repository Provider
final homeRepositoryProvider = Provider<HomeRepository>((ref) {
  final rpcClient = ref.watch(rpcClientProvider);
  return HomeRepositoryImpl(rpcClient);
});

/// Bottom navigation bar index provider
final bottomNavIndexProvider = StateProvider<int>((ref) => 0);

/// Balance Provider
final balanceProvider = FutureProvider<int>((ref) async {
  final repo = ref.watch(homeRepositoryProvider);
  final address = ref.watch(selectedAddressProvider);
  return repo.getBalance(address);
});

/// 7-day Balance Chart History Provider
final balanceHistoryProvider = FutureProvider<List<double>>((ref) async {
  final repo = ref.watch(homeRepositoryProvider);
  final address = ref.watch(selectedAddressProvider);
  return repo.get7DayBalanceHistory(address);
});

/// Recent Transactions Provider
final recentTransactionsProvider = FutureProvider<List<TransactionRecord>>((ref) async {
  final repo = ref.watch(homeRepositoryProvider);
  final address = ref.watch(selectedAddressProvider);
  return repo.getRecentTransactions(address, limit: 5);
});

/// Network Status Provider
final networkStatusProvider = FutureProvider<NetworkStatusData>((ref) async {
  final repo = ref.watch(homeRepositoryProvider);
  return repo.getNetworkStatus();
});

/// Staking Summary Provider
final stakingSummaryProvider = FutureProvider<StakingSummaryData>((ref) async {
  final repo = ref.watch(homeRepositoryProvider);
  final address = ref.watch(selectedAddressProvider);
  return repo.getStakingSummary(address);
});

/// Token Balances Provider
final tokenBalancesProvider = FutureProvider<List<TokenBalance>>((ref) async {
  final repo = ref.watch(homeRepositoryProvider);
  final address = ref.watch(selectedAddressProvider);
  return repo.getTokenBalances(address);
});

/// NFT Assets Provider
final nftOverviewProvider = FutureProvider<List<NftAsset>>((ref) async {
  final repo = ref.watch(homeRepositoryProvider);
  final address = ref.watch(selectedAddressProvider);
  return repo.getNfts(address, limit: 4);
});

/// Combined Home Data Bundle for full dashboard refresh
class HomeDataBundle {

  const HomeDataBundle({
    required this.balance,
    required this.balanceHistory,
    required this.recentTransactions,
    required this.networkStatus,
    required this.stakingSummary,
    required this.tokenBalances,
    required this.nfts,
  });
  final int balance;
  final List<double> balanceHistory;
  final List<TransactionRecord> recentTransactions;
  final NetworkStatusData networkStatus;
  final StakingSummaryData stakingSummary;
  final List<TokenBalance> tokenBalances;
  final List<NftAsset> nfts;
}

/// Home Data Provider aggregating all home information
final homeDataProvider = FutureProvider<HomeDataBundle>((ref) async {
  final repo = ref.watch(homeRepositoryProvider);
  final address = ref.watch(selectedAddressProvider);

  final results = await Future.wait([
    repo.getBalance(address),
    repo.get7DayBalanceHistory(address),
    repo.getRecentTransactions(address, limit: 5),
    repo.getNetworkStatus(),
    repo.getStakingSummary(address),
    repo.getTokenBalances(address),
    repo.getNfts(address, limit: 4),
  ]);

  return HomeDataBundle(
    balance: results[0] as int,
    balanceHistory: results[1] as List<double>,
    recentTransactions: results[2] as List<TransactionRecord>,
    networkStatus: results[3] as NetworkStatusData,
    stakingSummary: results[4] as StakingSummaryData,
    tokenBalances: results[5] as List<TokenBalance>,
    nfts: results[6] as List<NftAsset>,
  );
});
