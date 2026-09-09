import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../stake_dialog.dart';
import '../staking_providers.dart';
import '../unstake_dialog.dart';
import 'validator_card.dart';

class ValidatorList extends ConsumerWidget {
  const ValidatorList({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final filteredValidatorsAsync = ref.watch(filteredValidatorsProvider);
    final searchQuery = ref.watch(validatorSearchQueryProvider);
    final minGreenScore = ref.watch(validatorMinGreenScoreProvider);
    final selectedEnergy = ref.watch(validatorEnergyFilterProvider);
    final sortOption = ref.watch(validatorSortOptionProvider);

    return Column(
      children: [
        // Controls Section: Search & Sort Row
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Column(
            children: [
              // Search Input
              TextField(
                decoration: InputDecoration(
                  hintText: 'Search by validator name or address...',
                  prefixIcon: const Icon(Icons.search_rounded),
                  suffixIcon: searchQuery.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear_rounded, size: 18),
                          onPressed: () {
                            ref.read(validatorSearchQueryProvider.notifier).state = '';
                          },
                        )
                      : null,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                ),
                onChanged: (val) {
                  ref.read(validatorSearchQueryProvider.notifier).state = val;
                },
              ),

              const SizedBox(height: 12),

              // Filters & Sort Bar
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    // Sort Dropdown Button
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: theme.colorScheme.outline),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<ValidatorSortOption>(
                          value: sortOption,
                          isDense: true,
                          icon: const Icon(Icons.sort_rounded, size: 18),
                          dropdownColor: theme.colorScheme.surface,
                          items: const [
                            DropdownMenuItem(
                              value: ValidatorSortOption.greenScoreDesc,
                              child: Text('Green Score (High to Low)'),
                            ),
                            DropdownMenuItem(
                              value: ValidatorSortOption.greenScoreAsc,
                              child: Text('Green Score (Low to High)'),
                            ),
                            DropdownMenuItem(
                              value: ValidatorSortOption.stakeDesc,
                              child: Text('Highest Stake'),
                            ),
                            DropdownMenuItem(
                              value: ValidatorSortOption.commissionAsc,
                              child: Text('Lowest Commission'),
                            ),
                            DropdownMenuItem(
                              value: ValidatorSortOption.nameAsc,
                              child: Text('Name (A-Z)'),
                            ),
                          ],
                          onChanged: (val) {
                            if (val != null) {
                              ref.read(validatorSortOptionProvider.notifier).state = val;
                            }
                          },
                        ),
                      ),
                    ),

                    const SizedBox(width: 8),

                    // Energy Source Filter Chips
                    _EnergyFilterChip(
                      label: 'All Energy',
                      isSelected: selectedEnergy == null || selectedEnergy == 'All',
                      onSelected: () {
                        ref.read(validatorEnergyFilterProvider.notifier).state = null;
                      },
                    ),
                    const SizedBox(width: 6),
                    _EnergyFilterChip(
                      label: '☀️ Solar',
                      isSelected: selectedEnergy == 'Solar',
                      onSelected: () {
                        ref.read(validatorEnergyFilterProvider.notifier).state = 'Solar';
                      },
                    ),
                    const SizedBox(width: 6),
                    _EnergyFilterChip(
                      label: '💨 Wind',
                      isSelected: selectedEnergy == 'Wind',
                      onSelected: () {
                        ref.read(validatorEnergyFilterProvider.notifier).state = 'Wind';
                      },
                    ),
                    const SizedBox(width: 6),
                    _EnergyFilterChip(
                      label: '💧 Hydro',
                      isSelected: selectedEnergy == 'Hydro',
                      onSelected: () {
                        ref.read(validatorEnergyFilterProvider.notifier).state = 'Hydro';
                      },
                    ),
                    const SizedBox(width: 6),
                    _EnergyFilterChip(
                      label: '🌋 Geothermal',
                      isSelected: selectedEnergy == 'Geothermal',
                      onSelected: () {
                        ref.read(validatorEnergyFilterProvider.notifier).state = 'Geothermal';
                      },
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 8),

              // Green Score Threshold Slider Filter Expansion
              ExpansionTile(
                tilePadding: EdgeInsets.zero,
                dense: true,
                title: Text(
                  minGreenScore > 0
                      ? 'Min Green Score: ${minGreenScore.toInt()}+'
                      : 'Filter by Green Score',
                  style: theme.textTheme.labelMedium?.copyWith(
                    color: minGreenScore > 0 ? theme.colorScheme.primary : theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                trailing: Icon(
                  Icons.tune_rounded,
                  size: 18,
                  color: minGreenScore > 0 ? theme.colorScheme.primary : theme.colorScheme.onSurfaceVariant,
                ),
                children: [
                  Row(
                    children: [
                      const Icon(Icons.eco_outlined, size: 18),
                      const SizedBox(width: 8),
                      Text('0', style: theme.textTheme.bodySmall),
                      Expanded(
                        child: Slider(
                          value: minGreenScore,
                          min: 0,
                          max: 100,
                          divisions: 20,
                          label: '${minGreenScore.toInt()}',
                          onChanged: (val) {
                            ref.read(validatorMinGreenScoreProvider.notifier).state = val;
                          },
                        ),
                      ),
                      Text('100', style: theme.textTheme.bodySmall),
                      if (minGreenScore > 0)
                        IconButton(
                          icon: const Icon(Icons.refresh, size: 16),
                          onPressed: () {
                            ref.read(validatorMinGreenScoreProvider.notifier).state = 0.0;
                          },
                        ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),

        const Divider(height: 1),

        // Validator List View
        Expanded(
          child: filteredValidatorsAsync.when(
            data: (validators) {
              if (validators.isEmpty) {
                return const EmptyState(
                  icon: Icons.search_off_rounded,
                  title: 'No Validators Found',
                  subtitle: 'Try adjusting your search query or green score filter.',
                );
              }

              return ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: validators.length,
                separatorBuilder: (context, index) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final validator = validators[index];
                  return ValidatorCard(
                    validator: validator,
                    onStakePressed: () => _openStakeDialog(context, validator),
                    onUnstakePressed: () => _openUnstakeDialog(context, validator),
                  );
                },
              );
            },
            loading: () => ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: 4,
              separatorBuilder: (context, index) => const SizedBox(height: 12),
              itemBuilder: (context, index) => const ShimmerPlaceholder(height: 180),
            ),
            error: (err, stack) => EmptyState(
              icon: Icons.error_outline_rounded,
              title: 'Error Loading Validators',
              subtitle: err.toString(),
            ),
          ),
        ),
      ],
    );
  }

  void _openStakeDialog(BuildContext context, ValidatorInfo validator) {
    showDialog(
      context: context,
      builder: (context) => StakeDialog(validator: validator),
    );
  }

  void _openUnstakeDialog(BuildContext context, ValidatorInfo validator) {
    showDialog(
      context: context,
      builder: (context) => UnstakeDialog(
        validatorName: validator.name,
        validatorAddress: validator.address,
      ),
    );
  }
}

class _EnergyFilterChip extends StatelessWidget {

  const _EnergyFilterChip({
    required this.label,
    required this.isSelected,
    required this.onSelected,
  });
  final String label;
  final bool isSelected;
  final VoidCallback onSelected;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) => onSelected(),
      selectedColor: theme.colorScheme.primary.withOpacity(0.2),
      labelStyle: TextStyle(
        fontSize: 12,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        color: isSelected ? theme.colorScheme.primary : theme.colorScheme.onSurface,
      ),
      side: BorderSide(
        color: isSelected ? theme.colorScheme.primary : theme.colorScheme.outline,
      ),
    );
  }
}
