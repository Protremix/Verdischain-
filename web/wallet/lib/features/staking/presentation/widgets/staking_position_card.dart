import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../staking_providers.dart';
import '../unstake_dialog.dart';

class StakingPositionCard extends ConsumerWidget {

  const StakingPositionCard({
    super.key,
    required this.position,
    this.onClaimRewards,
  });
  final StakingPosition position;
  final VoidCallback? onClaimRewards;

  String _formatAddress(String address) {
    if (address.length <= 12) return address;
    return '${address.substring(0, 6)}...${address.substring(address.length - 6)}';
  }

  String _formatTimeAgo(DateTime dateTime) {
    final diff = DateTime.now().difference(dateTime);
    if (diff.inDays > 0) return '${diff.inDays}d ago';
    if (diff.inHours > 0) return '${diff.inHours}h ago';
    return '${diff.inMinutes}m ago';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final validatorAsync = ref.watch(validatorDetailProvider(position.validatorAddress));

    final validatorName = validatorAsync.when(
      data: (v) => v?.name ?? _formatAddress(position.validatorAddress),
      loading: () => _formatAddress(position.validatorAddress),
      error: (_, __) => _formatAddress(position.validatorAddress),
    );

    return VerdisCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: Validator Name & Position Status
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary.withOpacity(0.15),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.lock_clock_outlined,
                      color: theme.colorScheme.primary,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        validatorName,
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Staked ${_formatTimeAgo(position.stakedAt)}',
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
                ],
              ),

              // Status Chip
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: position.status == StakingStatus.active
                      ? theme.colorScheme.primary.withOpacity(0.15)
                      : theme.colorScheme.secondary.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  position.status.name.toUpperCase(),
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: position.status == StakingStatus.active
                        ? theme.colorScheme.primary
                        : theme.colorScheme.secondary,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),
          const Divider(height: 1),
          const SizedBox(height: 12),

          // Amounts Grid
          Row(
            children: [
              // Staked Amount
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Staked Amount',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${position.amount} VRD',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),

              // Earned Rewards
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Earned Rewards',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(
                          Icons.eco_rounded,
                          size: 16,
                          color: theme.colorScheme.primary,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '+${position.rewards} VRD',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: theme.colorScheme.primary,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Action Buttons: Unstake & Claim
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (context) => UnstakeDialog(
                        validatorName: validatorName,
                        validatorAddress: position.validatorAddress,
                        currentStakedAmount: position.amount,
                      ),
                    );
                  },
                  icon: const Icon(Icons.output_rounded, size: 18),
                  label: const Text('Unstake'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: position.rewards > 0
                      ? (onClaimRewards ??
                          () async {
                            final repo = ref.read(stakingRepositoryProvider);
                            final account = ref.read(currentAccountAddressProvider);
                            await repo.claimRewards(account);
                            ref.invalidate(stakingPositionsProvider);
                            ref.invalidate(rewardsProvider);
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('Rewards claimed successfully!'),
                                ),
                              );
                            }
                          })
                      : null,
                  icon: const Icon(Icons.card_giftcard_rounded, size: 18),
                  label: const Text('Claim Rewards'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
