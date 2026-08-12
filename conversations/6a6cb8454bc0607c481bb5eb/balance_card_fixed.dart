import 'package:flutter/material.dart';

import 'package:verdis_wallet/core/config/network_config.dart';

/// Glassmorphism card displaying total VRDX balance, USD value, 24h change, and allocation breakdown on tap.
class BalanceCard extends StatelessWidget {

  const BalanceCard({
    super.key,
    required this.balance,
    this.totalStaked = 0,
    this.vrdxPriceUsd = 0.25,
    this.change24hPercent = 5.4,
    this.onTap,
  });

  /// Liquid (available) balance, in base units (9 decimals per NetworkConfig).
  final int balance;

  /// Currently staked balance, in base units (9 decimals). Real value comes
  /// from StakingSummaryData.totalStaked — the breakdown sheet below used to
  /// show a hardcoded fake 15,400 VRDX regardless of the actual stake.
  final int totalStaked;
  final double vrdxPriceUsd;
  final double change24hPercent;
  final VoidCallback? onTap;

  static double _pow10(int exp) {
    var v = 1.0;
    for (var i = 0; i < exp; i++) {
      v *= 10.0;
    }
    return v;
  }

  double get vrdxAmount => balance / _pow10(NetworkConfig.decimals);
  double get stakedVrdxAmount => totalStaked / _pow10(NetworkConfig.decimals);
  double get totalVrdxAmount => vrdxAmount + stakedVrdxAmount;
  double get usdValue => vrdxAmount * vrdxPriceUsd;
  double get totalUsdValue => totalVrdxAmount * vrdxPriceUsd;

  /// Percentage of the given VRDX amount relative to the total portfolio
  /// (liquid + staked). Returns 0 when there is no balance at all, instead
  /// of dividing by zero.
  double _percentOf(double amount) {
    if (totalVrdxAmount <= 0) return 0;
    return (amount / totalVrdxAmount) * 100;
  }

  void _showAllocationBreakdown(BuildContext context) {
    final theme = Theme.of(context);

    showModalBottomSheet(
      context: context,
      backgroundColor: theme.colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.onSurfaceVariant.withOpacity(0.4),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Text(
                'Portfolio Allocation Breakdown',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              _buildAllocationRow(
                context,
                title: 'Liquid VRDX',
                amount: '${vrdxAmount.toStringAsFixed(2)} VRDX',
                percentage: '${_percentOf(vrdxAmount).toStringAsFixed(1)}%',
                color: theme.colorScheme.primary,
              ),
              const Divider(height: 24),
              _buildAllocationRow(
                context,
                title: 'Staked VRDX (gVRDX)',
                amount: '${stakedVrdxAmount.toStringAsFixed(2)} VRDX',
                percentage: '${_percentOf(stakedVrdxAmount).toStringAsFixed(1)}%',
                color: const Color(0xFF00FF88),
              ),
              const Divider(height: 24),
              _buildAllocationRow(
                context,
                title: 'Total Portfolio Value',
                amount: '\$${totalUsdValue.toStringAsFixed(2)} USD',
                percentage: '100.0%',
                color: Colors.white,
                isBold: true,
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Close'),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildAllocationRow(
    BuildContext context, {
    required String title,
    required String amount,
    required String percentage,
    required Color color,
    bool isBold = false,
  }) {
    final theme = Theme.of(context);
    final textStyle = isBold
        ? theme.textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.bold)
        : theme.textTheme.bodyMedium;

    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(title, style: textStyle),
        ),
        Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(amount, style: textStyle),
            Text(
              percentage,
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isPositive = change24hPercent >= 0;

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: BorderSide(
          color: theme.colorScheme.primary.withOpacity(0.25),
          width: 1.5,
        ),
      ),
      child: InkWell(
        onTap: onTap ?? () => _showAllocationBreakdown(context),
        borderRadius: BorderRadius.circular(20),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            gradient: LinearGradient(
              colors: [
                theme.colorScheme.surface,
                theme.colorScheme.surfaceContainerHighest.withOpacity(0.8),
                theme.colorScheme.primary.withOpacity(0.08),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          padding: const EdgeInsets.all(20.0),
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
                          color: theme.colorScheme.primary.withOpacity(0.15),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          Icons.account_balance_wallet,
                          size: 16,
                          color: theme.colorScheme.primary,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Total Balance',
                        style: theme.textTheme.labelLarge?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: (isPositive ? const Color(0xFF00E676) : theme.colorScheme.error)
                          .withOpacity(0.15),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          isPositive ? Icons.trending_up : Icons.trending_down,
                          size: 14,
                          color: isPositive ? const Color(0xFF00E676) : theme.colorScheme.error,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${isPositive ? '+' : ''}${change24hPercent.toStringAsFixed(1)}%',
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: isPositive ? const Color(0xFF00E676) : theme.colorScheme.error,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
                children: [
                  Text(
                    vrdxAmount.toStringAsFixed(2),
                    style: theme.textTheme.displayMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                      letterSpacing: -0.5,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'VRDX',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '≈ \$${usdValue.toStringAsFixed(2)} USD',
                    style: theme.textTheme.titleMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  Row(
                    children: [
                      Text(
                        'Tap for breakdown',
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.primary,
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
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
