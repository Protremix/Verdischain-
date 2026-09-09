import 'package:flutter/material.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';

class ValidatorCard extends StatelessWidget {

  const ValidatorCard({
    super.key,
    required this.validator,
    this.onStakePressed,
    this.onUnstakePressed,
    this.onTap,
  });
  final ValidatorInfo validator;
  final VoidCallback? onStakePressed;
  final VoidCallback? onUnstakePressed;
  final VoidCallback? onTap;

  Color _getGreenScoreColor(int score) {
    if (score >= 90) return const Color(0xFF00FF88);
    if (score >= 75) return const Color(0xFF76FF03);
    if (score >= 50) return const Color(0xFFFFB300);
    return const Color(0xFFCF6679);
  }

  IconData _getEnergyIcon(String energySource) {
    switch (energySource.toLowerCase()) {
      case 'solar':
        return Icons.wb_sunny_rounded;
      case 'wind':
        return Icons.air_rounded;
      case 'hydro':
        return Icons.water_drop_rounded;
      case 'geothermal':
        return Icons.thermostat_rounded;
      case 'biomass':
        return Icons.eco_rounded;
      default:
        return Icons.bolt_rounded;
    }
  }

  String _formatAddress(String address) {
    if (address.length <= 12) return address;
    return '${address.substring(0, 6)}...${address.substring(address.length - 6)}';
  }

  String _formatNumber(int number) {
    if (number >= 1000000) {
      return '${(number / 1000000).toStringAsFixed(2)}M';
    } else if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}K';
    }
    return number.toString();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final greenScoreColor = _getGreenScoreColor(validator.greenScore);

    return VerdisCard(
      onTap: onTap,
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: Name, Address, Active status badge
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Energy source avatar
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: greenScoreColor.withOpacity(0.5),
                    width: 1.5,
                  ),
                ),
                child: Icon(
                  _getEnergyIcon(validator.energySource),
                  color: greenScoreColor,
                  size: 22,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            validator.name,
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        // Active / Inactive Badge
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: validator.isActive
                                ? theme.colorScheme.primary.withOpacity(0.15)
                                : theme.colorScheme.error.withOpacity(0.15),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Container(
                                width: 6,
                                height: 6,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: validator.isActive
                                      ? theme.colorScheme.primary
                                      : theme.colorScheme.error,
                                ),
                              ),
                              const SizedBox(width: 4),
                              Text(
                                validator.isActive ? 'ACTIVE' : 'INACTIVE',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                  color: validator.isActive
                                      ? theme.colorScheme.primary
                                      : theme.colorScheme.error,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _formatAddress(validator.address),
                      style: theme.textTheme.bodySmall?.copyWith(
                        fontFamily: 'monospace',
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),
          const Divider(height: 1),
          const SizedBox(height: 12),

          // Key Metrics Grid
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Green Score Badge
              _MetricItem(
                label: 'Green Score',
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: greenScoreColor.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: greenScoreColor.withOpacity(0.4)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.eco_rounded, size: 14, color: greenScoreColor),
                      const SizedBox(width: 4),
                      Text(
                        '${validator.greenScore}/100',
                        style: TextStyle(
                          color: greenScoreColor,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // Total Staked
              _MetricItem(
                label: 'Total Staked',
                value: '${_formatNumber(validator.totalStaked)} VRD',
              ),

              // Commission
              _MetricItem(
                label: 'Commission',
                value: '${validator.commission}%',
              ),

              // Energy Source
              _MetricItem(
                label: 'Energy',
                value: validator.energySource,
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Actions
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onUnstakePressed,
                  icon: const Icon(Icons.remove_circle_outline, size: 18),
                  label: const Text('Unstake'),
                  style: OutlinedButton.styleFrom(
                    visualDensity: VisualDensity.compact,
                    padding: const EdgeInsets.symmetric(vertical: 10),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: onStakePressed,
                  icon: const Icon(Icons.add_circle_outline, size: 18),
                  label: const Text('Stake'),
                  style: ElevatedButton.styleFrom(
                    visualDensity: VisualDensity.compact,
                    padding: const EdgeInsets.symmetric(vertical: 10),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _MetricItem extends StatelessWidget {

  const _MetricItem({
    required this.label,
    this.value,
    this.child,
  });
  final String label;
  final String? value;
  final Widget? child;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: theme.textTheme.labelSmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
            fontSize: 11,
          ),
        ),
        const SizedBox(height: 4),
        if (child != null)
          child!
        else
          Text(
            value ?? '',
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
      ],
    );
  }
}
