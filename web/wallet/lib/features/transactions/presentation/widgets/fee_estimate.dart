import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../transactions_providers.dart';

/// Fee estimate widget with selectable speed tiers (Slow, Standard, Fast)
class FeeEstimateWidget extends ConsumerWidget {

  const FeeEstimateWidget({
    super.key,
    required this.recipient,
    required this.amount,
    this.onSpeedSelected,
  });
  final String recipient;
  final double amount;
  final ValueChanged<String>? onSpeedSelected;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final selectedSpeed = ref.watch(selectedFeeSpeedProvider);

    final feeAsync = ref.watch(feeEstimateProvider({
      'recipient': recipient,
      'amount': amount,
      'speed': selectedSpeed,
    }),);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.5),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: theme.colorScheme.outline.withOpacity(0.5),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.local_gas_station_rounded,
                    size: 18,
                    color: theme.colorScheme.primary,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Network Fee',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              feeAsync.when(
                data: (fee) => Text(
                  '~${fee.toStringAsFixed(4)} VRDX',
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                loading: () => const SizedBox(
                  width: 14,
                  height: 14,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
                error: (_, __) => Text(
                  '0.0012 VRDX',
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildSpeedChip(
                context,
                ref,
                speedKey: 'slow',
                label: 'Slow',
                time: '~30s',
                feeEstimate: '0.0006 VRDX',
                isSelected: selectedSpeed == 'slow',
              ),
              const SizedBox(width: 8),
              _buildSpeedChip(
                context,
                ref,
                speedKey: 'standard',
                label: 'Standard',
                time: '~12s',
                feeEstimate: '0.0012 VRDX',
                isSelected: selectedSpeed == 'standard',
              ),
              const SizedBox(width: 8),
              _buildSpeedChip(
                context,
                ref,
                speedKey: 'fast',
                label: 'Fast',
                time: '~6s',
                feeEstimate: '0.0024 VRDX',
                isSelected: selectedSpeed == 'fast',
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(
                Icons.timer_outlined,
                size: 14,
                color: theme.colorScheme.onSurfaceVariant,
              ),
              const SizedBox(width: 4),
              Text(
                'Estimated confirmation: ${_getConfirmationTime(selectedSpeed)}',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSpeedChip(
    BuildContext context,
    WidgetRef ref, {
    required String speedKey,
    required String label,
    required String time,
    required String feeEstimate,
    required bool isSelected,
  }) {
    final theme = Theme.of(context);
    return Expanded(
      child: InkWell(
        onTap: () {
          ref.read(selectedFeeSpeedProvider.notifier).state = speedKey;
          if (onSpeedSelected != null) {
            onSpeedSelected!(speedKey);
          }
        },
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 8),
          decoration: BoxDecoration(
            color: isSelected
                ? theme.colorScheme.primary.withOpacity(0.15)
                : theme.colorScheme.surface,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: isSelected
                  ? theme.colorScheme.primary
                  : theme.colorScheme.outline.withOpacity(0.3),
              width: isSelected ? 1.5 : 1.0,
            ),
          ),
          child: Column(
            children: [
              Text(
                label,
                style: theme.textTheme.labelMedium?.copyWith(
                  color: isSelected
                      ? theme.colorScheme.primary
                      : theme.colorScheme.onSurface,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                time,
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                  fontSize: 10,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _getConfirmationTime(String speed) {
    switch (speed) {
      case 'slow':
        return '~30 seconds (1-2 blocks)';
      case 'fast':
        return '~6 seconds (next block)';
      case 'standard':
      default:
        return '~12 seconds (1 block)';
    }
  }
}
