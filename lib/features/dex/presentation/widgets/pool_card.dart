import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';

/// Card component displaying pool statistics and action triggers
class PoolCard extends StatelessWidget {

  const PoolCard({
    super.key,
    required this.pool,
    this.onSwap,
    this.onAddLiquidity,
    this.onTap,
  });
  final DexPool pool;
  final VoidCallback? onSwap;
  final VoidCallback? onAddLiquidity;
  final VoidCallback? onTap;

  String _formatNumber(num value) {
    if (value >= 1000000) {
      return '${(value / 1000000).toStringAsFixed(2)}M';
    } else if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}K';
    }
    return NumberFormat('#,##0').format(value);
  }

  double get _calculatedApr {
    // Annualized fee return estimated from 24h volume
    final dailyFees = pool.totalVolume24h * pool.feeRate;
    final totalLiquidity = pool.reserveB * 2.0;
    if (totalLiquidity <= 0) return 12.5;
    final apr = (dailyFees * 365 / totalLiquidity) * 100;
    return apr.clamp(5.0, 185.0);
  }

  double get _priceRatio {
    if (pool.reserveA <= 0) return 0.0;
    return pool.reserveB / pool.reserveA;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final primaryColor = theme.colorScheme.primary;

    return VerdisCard(
      onTap: onTap,
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: Token Pair & APR badge
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  _buildStackedIcons(context, pool.tokenA, pool.tokenB),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${pool.tokenA} / ${pool.tokenB}',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Fee: ${(pool.feeRate * 100).toStringAsFixed(2)}%',
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: primaryColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: primaryColor.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '${_calculatedApr.toStringAsFixed(1)}% APR',
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: primaryColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'Est. Yield',
                      style: theme.textTheme.labelSmall?.copyWith(
                        fontSize: 9,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),
          const Divider(),
          const SizedBox(height: 12),

          // Reserves & Price ratio
          Row(
            children: [
              Expanded(
                child: _buildDetailItem(
                  context,
                  label: 'Reserves',
                  value: '${_formatNumber(pool.reserveA)} ${pool.tokenA}',
                  subValue: '${_formatNumber(pool.reserveB)} ${pool.tokenB}',
                ),
              ),
              Expanded(
                child: _buildDetailItem(
                  context,
                  label: 'Price Ratio',
                  value: '1 ${pool.tokenA} =',
                  subValue: '${_priceRatio < 0.01 ? _priceRatio.toStringAsFixed(6) : _priceRatio.toStringAsFixed(4)} ${pool.tokenB}',
                ),
              ),
              Expanded(
                child: _buildDetailItem(
                  context,
                  label: '24h Volume',
                  value: '\$${_formatNumber(pool.totalVolume24h)}',
                  subValue: '${pool.swapCount24h} swaps',
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Action Buttons: Swap | Add Liquidity
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onSwap,
                  icon: const Icon(Icons.swap_horiz, size: 18),
                  label: const Text('Swap'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    minimumSize: const Size(0, 40),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: onAddLiquidity,
                  icon: const Icon(Icons.add_circle_outline, size: 18),
                  label: const Text('Add Liquidity'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    minimumSize: const Size(0, 40),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStackedIcons(BuildContext context, String tokenA, String tokenB) {
    final theme = Theme.of(context);
    return SizedBox(
      width: 44,
      height: 32,
      child: Stack(
        children: [
          Positioned(
            left: 0,
            child: CircleAvatar(
              radius: 16,
              backgroundColor: theme.colorScheme.primary,
              child: Text(
                tokenA.substring(0, 1),
                style: const TextStyle(
                  color: Colors.black,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
          ),
          Positioned(
            right: 0,
            child: CircleAvatar(
              radius: 16,
              backgroundColor: theme.colorScheme.surfaceContainerHighest,
              child: Text(
                tokenB.substring(0, 1),
                style: TextStyle(
                  color: theme.colorScheme.onSurface,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailItem(
    BuildContext context, {
    required String label,
    required String value,
    required String subValue,
  }) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: theme.textTheme.bodySmall),
        const SizedBox(height: 2),
        Text(
          value,
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        Text(
          subValue,
          style: theme.textTheme.bodySmall?.copyWith(
            fontSize: 11,
            color: theme.colorScheme.onSurfaceVariant,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }
}
