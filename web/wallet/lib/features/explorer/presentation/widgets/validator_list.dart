import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../explorer_providers.dart';

class ValidatorListWidget extends ConsumerWidget {
  const ValidatorListWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final validatorsState = ref.watch(validatorsProvider);
    final sortBy = ref.watch(validatorSortProvider);
    final theme = Theme.of(context);

    return Column(
      children: [
        // Sort selector header
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Active Green Validators',
                style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
              ),
              Row(
                children: [
                  Text('Sort by: ', style: theme.textTheme.labelSmall),
                  ChoiceChip(
                    label: const Text('Green Score'),
                    selected: sortBy == ValidatorSortBy.score,
                    onSelected: (selected) {
                      if (selected) {
                        ref.read(validatorSortProvider.notifier).state = ValidatorSortBy.score;
                      }
                    },
                    visualDensity: VisualDensity.compact,
                  ),
                  const SizedBox(width: 8),
                  ChoiceChip(
                    label: const Text('Stake'),
                    selected: sortBy == ValidatorSortBy.stake,
                    onSelected: (selected) {
                      if (selected) {
                        ref.read(validatorSortProvider.notifier).state = ValidatorSortBy.stake;
                      }
                    },
                    visualDensity: VisualDensity.compact,
                  ),
                ],
              ),
            ],
          ),
        ),

        // List view
        Expanded(
          child: validatorsState.when(
            loading: () => ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: 6,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (_, __) => const ShimmerPlaceholder(height: 100),
            ),
            error: (error, _) => Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 48, color: Colors.redAccent),
                  const SizedBox(height: 12),
                  Text('Failed to load validators', style: theme.textTheme.titleMedium),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => ref.refresh(validatorsProvider),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
            data: (validators) {
              if (validators.isEmpty) {
                return const EmptyState(
                  icon: Icons.shield_outlined,
                  title: 'No validators found',
                  subtitle: 'Active block producers will appear here.',
                );
              }

              return RefreshIndicator(
                color: theme.colorScheme.primary,
                onRefresh: () async => ref.refresh(validatorsProvider),
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  itemCount: validators.length,
                  itemBuilder: (context, index) {
                    final validator = validators[index];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: VerdisCard(
                        onTap: () => _showValidatorDetail(context, validator),
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                CircleAvatar(
                                  backgroundColor: theme.colorScheme.primary.withOpacity(0.15),
                                  child: Text(
                                    '${index + 1}',
                                    style: TextStyle(
                                      color: theme.colorScheme.primary,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        validator.name,
                                        style: theme.textTheme.titleMedium?.copyWith(
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        _shortenAddress(validator.address),
                                        style: theme.textTheme.bodySmall?.copyWith(
                                          fontFamily: 'Monospace',
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                // Green Score Badge
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: Colors.green.withOpacity(0.15),
                                    borderRadius: BorderRadius.circular(16),
                                    border: Border.all(color: Colors.green.withOpacity(0.4)),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Icon(Icons.eco_rounded, color: Colors.greenAccent, size: 16),
                                      const SizedBox(width: 4),
                                      Text(
                                        '${validator.greenScore}',
                                        style: const TextStyle(
                                          color: Colors.greenAccent,
                                          fontWeight: FontWeight.bold,
                                          fontSize: 13,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            const Divider(),
                            const SizedBox(height: 8),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text('Total Stake', style: theme.textTheme.labelSmall),
                                    const SizedBox(height: 2),
                                    Text(
                                      _formatStake(validator.stake),
                                      style: theme.textTheme.labelLarge?.copyWith(
                                        fontWeight: FontWeight.bold,
                                        color: theme.colorScheme.primary,
                                      ),
                                    ),
                                  ],
                                ),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.end,
                                  children: [
                                    Text('Energy Source', style: theme.textTheme.labelSmall),
                                    const SizedBox(height: 2),
                                    Row(
                                      children: [
                                        const Icon(Icons.bolt, size: 14, color: Colors.amberAccent),
                                        const SizedBox(width: 2),
                                        Text(
                                          validator.energySource,
                                          style: theme.textTheme.bodySmall?.copyWith(
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  void _showValidatorDetail(BuildContext context, ValidatorInfo validator) {
    final theme = Theme.of(context);
    showModalBottomSheet(
      context: context,
      backgroundColor: theme.colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.outline,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  const Icon(Icons.shield_rounded, color: Colors.greenAccent, size: 28),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      validator.name,
                      style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              _buildDetailRow(context, 'Validator Address', validator.address, isMonospace: true),
              _buildDetailRow(context, 'Green Sustainability Rating', '${validator.greenScore} / 100 Eco Score'),
              _buildDetailRow(context, 'Energy Source', validator.energySource),
              _buildDetailRow(context, 'Total Self Stake', _formatStake(validator.stake)),
              _buildDetailRow(context, 'Commission Rate', '${validator.commission}%'),
              _buildDetailRow(context, 'Node Status', validator.isActive ? 'Active (Producing Blocks)' : 'Inactive'),
              const SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }

  Widget _buildDetailRow(BuildContext context, String label, String value, {bool isMonospace = false}) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: theme.textTheme.labelMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: theme.textTheme.bodyMedium?.copyWith(
                fontFamily: isMonospace ? 'Monospace' : null,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  String _shortenAddress(String addr) {
    if (addr.length <= 16) return addr;
    return '${addr.substring(0, 8)}...${addr.substring(addr.length - 6)}';
  }

  String _formatStake(int planck) {
    final vrdx = planck / 1e18;
    if (vrdx >= 1e6) {
      return '${(vrdx / 1e6).toStringAsFixed(2)}M VRDX';
    }
    if (vrdx >= 1e3) {
      return '${(vrdx / 1e3).toStringAsFixed(1)}K VRDX';
    }
    return '${vrdx.toStringAsFixed(0)} VRDX';
  }
}
