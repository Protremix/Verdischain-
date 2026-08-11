import 'package:flutter/material.dart';
import '../../domain/home_repository.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';

/// Card displaying staking summary: total staked, active validators, rewards earned, and estimated APY.
class StakingSummaryCard extends StatelessWidget {

  const StakingSummaryCard({
    super.key,
    required this.summary,
    this.onManageTap,
  });
  final StakingSummaryData summary;
  final VoidCallback? onManageTap;

  double get stakedAmount => summary.totalStaked / 10000000000.0;
  double get rewardsAmount => summary.rewardsEarned / 10000000000.0;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final apyFormatted = (summary.apyEstimate * 100).toStringAsFixed(1);

    return VerdisCard(
      onTap: onManageTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFB300).withOpacity(0.15),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.energy_savings_leaf,
                      size: 18,
                      color: Color(0xFFFFB300),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Green Staking',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '$apyFormatted% APY',
                  style: theme.textTheme.labelMedium?.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Total Staked',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${stakedAmount.toStringAsFixed(2)} VRDX',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Rewards Earned',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '+${rewardsAmount.toStringAsFixed(2)} VRDX',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: theme.colorScheme.primary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.how_to_reg,
                    size: 16,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    '${summary.activeValidators} Active Validators',
                    style: theme.textTheme.bodySmall,
                  ),
                ],
              ),
              InkWell(
                onTap: onManageTap,
                child: Row(
                  children: [
                    Text(
                      'Manage Stake',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Icon(
                      Icons.chevron_right,
                      size: 14,
                      color: theme.colorScheme.primary,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
