import 'package:flutter/material.dart';

import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../../domain/home_repository.dart';

/// Card showing Verdis network status: block height, peers, epoch progress bar, validator count, and consensus info.
class NetworkStatusCard extends StatelessWidget {

  const NetworkStatusCard({
    super.key,
    required this.networkStatus,
    this.onTap,
  });
  final NetworkStatusData networkStatus;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final progressPercent = (networkStatus.epochProgress * 100).clamp(0.0, 100.0);

    return VerdisCard(
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.sensors,
                    color: theme.colorScheme.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Network Health',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              NetworkStatusBadge(
                isConnected: networkStatus.isConnected,
                blockNumber: networkStatus.blockHeight,
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _statItem(
                  context,
                  label: 'Block Height',
                  value: '#${_formatNumber(networkStatus.blockHeight)}',
                  icon: Icons.tag,
                ),
              ),
              Expanded(
                child: _statItem(
                  context,
                  label: 'Active Peers',
                  value: '${networkStatus.peersCount} Connected',
                  icon: Icons.hub,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _statItem(
                  context,
                  label: 'Validators',
                  value: '${networkStatus.validatorCount} Active',
                  icon: Icons.shield,
                ),
              ),
              Expanded(
                child: _statItem(
                  context,
                  label: 'Consensus',
                  value: 'PoGS (BABE)',
                  icon: Icons.eco,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Epoch #${networkStatus.currentEpoch} Progress',
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  Text(
                    '${progressPercent.toStringAsFixed(1)}%',
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: LinearProgressIndicator(
                  value: networkStatus.epochProgress,
                  minHeight: 8,
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                  color: theme.colorScheme.primary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _statItem(
    BuildContext context, {
    required String label,
    required String value,
    required IconData icon,
  }) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 14, color: theme.colorScheme.onSurfaceVariant),
            const SizedBox(width: 4),
            Text(
              label,
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  String _formatNumber(int number) {
    return number.toString().replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match m) => '${m[1]},',
    );
  }
}
