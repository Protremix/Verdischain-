import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/network/rpc_client.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import '../data/staking_repository_impl.dart';
import '../domain/staking_repository.dart';

/// Repository Provider
final stakingRepositoryProvider = Provider<StakingRepository>((ref) {
  final rpcClient = ref.watch(rpcClientProvider);
  return StakingRepositoryImpl(rpcClient);
});

/// Current active wallet account address provider (default / mock)
final currentAccountAddressProvider = Provider<String>((ref) {
  return '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY';
});

/// Async validators provider
final validatorsProvider = FutureProvider<List<ValidatorInfo>>((ref) async {
  final repository = ref.watch(stakingRepositoryProvider);
  return repository.getValidators();
});

/// Async validator detail provider
final validatorDetailProvider =
    FutureProvider.family<ValidatorInfo?, String>((ref, address) async {
  final repository = ref.watch(stakingRepositoryProvider);
  return repository.getValidatorDetail(address);
});

/// Async staking positions provider
final stakingPositionsProvider =
    FutureProvider<List<StakingPosition>>((ref) async {
  final repository = ref.watch(stakingRepositoryProvider);
  final account = ref.watch(currentAccountAddressProvider);
  return repository.getStakingPositions(account);
});

/// Async rewards provider
final rewardsProvider = FutureProvider<StakingRewards>((ref) async {
  final repository = ref.watch(stakingRepositoryProvider);
  final account = ref.watch(currentAccountAddressProvider);
  return repository.getRewards(account);
});

/// Async staking history provider
final stakingHistoryProvider =
    FutureProvider<List<StakingHistoryItem>>((ref) async {
  final repository = ref.watch(stakingRepositoryProvider);
  final account = ref.watch(currentAccountAddressProvider);
  return repository.getStakingHistory(account);
});

/// Async green score detail provider for a validator address
final greenScoreProvider =
    FutureProvider.family<GreenScoreDetail, String>((ref, validatorAddress) async {
  final repository = ref.watch(stakingRepositoryProvider);
  return repository.getGreenScore(validatorAddress);
});

/// Validator sort options
enum ValidatorSortOption {
  greenScoreDesc,
  greenScoreAsc,
  stakeDesc,
  commissionAsc,
  nameAsc,
}

/// Search Query state provider
final validatorSearchQueryProvider = StateProvider<String>((ref) => '');

/// Green Score filter threshold state provider (0 to 100)
final validatorMinGreenScoreProvider = StateProvider<double>((ref) => 0.0);

/// Energy Source filter state provider (null = all)
final validatorEnergyFilterProvider = StateProvider<String?>((ref) => null);

/// Sort Option state provider
final validatorSortOptionProvider =
    StateProvider<ValidatorSortOption>((ref) => ValidatorSortOption.greenScoreDesc);

/// Filtered and sorted validators list provider
final filteredValidatorsProvider = Provider<AsyncValue<List<ValidatorInfo>>>((ref) {
  final validatorsAsync = ref.watch(validatorsProvider);
  final query = ref.watch(validatorSearchQueryProvider).trim().toLowerCase();
  final minScore = ref.watch(validatorMinGreenScoreProvider);
  final energyFilter = ref.watch(validatorEnergyFilterProvider);
  final sortOption = ref.watch(validatorSortOptionProvider);

  return validatorsAsync.whenData((list) {
    final filtered = list.where((v) {
      final matchesQuery = query.isEmpty ||
          v.name.toLowerCase().contains(query) ||
          v.address.toLowerCase().contains(query);

      final matchesScore = v.greenScore >= minScore;

      final matchesEnergy = energyFilter == null ||
          energyFilter == 'All' ||
          v.energySource.toLowerCase() == energyFilter.toLowerCase();

      return matchesQuery && matchesScore && matchesEnergy;
    }).toList();

    // Sort
    switch (sortOption) {
      case ValidatorSortOption.greenScoreDesc:
        filtered.sort((a, b) => b.greenScore.compareTo(a.greenScore));
        break;
      case ValidatorSortOption.greenScoreAsc:
        filtered.sort((a, b) => a.greenScore.compareTo(b.greenScore));
        break;
      case ValidatorSortOption.stakeDesc:
        filtered.sort((a, b) => b.totalStaked.compareTo(a.totalStaked));
        break;
      case ValidatorSortOption.commissionAsc:
        filtered.sort((a, b) => a.commission.compareTo(b.commission));
        break;
      case ValidatorSortOption.nameAsc:
        filtered.sort((a, b) => a.name.compareTo(b.name));
        break;
    }

    return filtered;
  });
});
