import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'home_providers.dart';
import 'widgets/balance_card.dart';
import 'widgets/network_status.dart';
import 'widgets/nft_overview.dart';
import 'widgets/quick_actions.dart';
import 'widgets/recent_transactions.dart';
import 'widgets/staking_summary.dart';

/// Portfolio View displaying VRDX total balance, 7-day fl_chart LineChart, quick action buttons, staking summary, NFTs, recent transactions, and network status card.
class PortfolioView extends ConsumerWidget {
  const PortfolioView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final homeDataAsync = ref.watch(homeDataProvider);

    return RefreshIndicator(
      color: theme.colorScheme.primary,
      backgroundColor: theme.colorScheme.surface,
      onRefresh: () async {
        ref.invalidate(homeDataProvider);
        ref.invalidate(balanceProvider);
        ref.invalidate(recentTransactionsProvider);
        ref.invalidate(networkStatusProvider);
        ref.invalidate(stakingSummaryProvider);
        ref.invalidate(tokenBalancesProvider);
        ref.invalidate(nftOverviewProvider);
        ref.invalidate(balanceHistoryProvider);
      },
      child: homeDataAsync.when(
        data: (data) => SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Large Balance Card
              BalanceCard(
                balance: data.balance,
                vrdxPriceUsd: 0.25,
                change24hPercent: 5.4,
              ),
              const SizedBox(height: 20),

              // 7-Day Balance History Portfolio Line Chart
              _PortfolioChartCard(historyPoints: data.balanceHistory),
              const SizedBox(height: 20),

              // Quick Action Buttons (Send, Receive, Swap, Stake)
              QuickActions(
                onActionTap: (type) {
                  _handleQuickAction(context, type, ref);
                },
              ),
              const SizedBox(height: 24),

              // Staking Summary Card
              StakingSummaryCard(
                summary: data.stakingSummary,
                onManageTap: () {
                  ref.read(bottomNavIndexProvider.notifier).state = 3; // Navigate to Staking tab
                },
              ),
              const SizedBox(height: 24),

              // NFT Overview
              NftOverview(
                nfts: data.nfts,
                onViewGalleryTap: () {
                  _showToast(context, 'Full NFT Gallery view coming in next update');
                },
              ),
              const SizedBox(height: 24),

              // Recent Transactions List (Last 5)
              RecentTransactionsList(
                transactions: data.recentTransactions,
                onViewAllTap: () {
                  _showToast(context, 'Navigating to transaction history');
                },
              ),
              const SizedBox(height: 24),

              // Network Status Card
              NetworkStatusCard(
                networkStatus: data.networkStatus,
                onTap: () {
                  _showToast(context, 'Connected to Verdis Mainnet Node');
                },
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
        loading: () => const Center(
          child: Padding(
            padding: EdgeInsets.all(48.0),
            child: CircularProgressIndicator(),
          ),
        ),
        error: (err, stack) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.error_outline, size: 48, color: theme.colorScheme.error),
                const SizedBox(height: 16),
                Text('Failed to load portfolio data', style: theme.textTheme.titleMedium),
                const SizedBox(height: 8),
                Text(err.toString(), style: theme.textTheme.bodySmall, textAlign: TextAlign.center),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => ref.refresh(homeDataProvider),
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _handleQuickAction(BuildContext context, QuickActionType type, WidgetRef ref) {
    switch (type) {
      case QuickActionType.send:
        _showActionBottomSheet(context, 'Send VRDX', Icons.send);
        break;
      case QuickActionType.receive:
        _showActionBottomSheet(context, 'Receive VRDX', Icons.download);
        break;
      case QuickActionType.swap:
        ref.read(bottomNavIndexProvider.notifier).state = 2; // Switch to DEX tab
        break;
      case QuickActionType.stake:
        ref.read(bottomNavIndexProvider.notifier).state = 3; // Switch to Staking tab
        break;
    }
  }

  void _showActionBottomSheet(BuildContext context, String title, IconData icon) {
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
            children: [
              Icon(icon, size: 40, color: theme.colorScheme.primary),
              const SizedBox(height: 12),
              Text(title, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(
                'Initiating $title transaction on Verdis Network...',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodySmall,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Dismiss'),
              ),
            ],
          ),
        );
      },
    );
  }

  void _showToast(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), duration: const Duration(seconds: 2)),
    );
  }
}

/// Portfolio 7-Day Line Chart Container using fl_chart
class _PortfolioChartCard extends StatelessWidget {

  const _PortfolioChartCard({required this.historyPoints});
  final List<double> historyPoints;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final primaryColor = theme.colorScheme.primary;

    final spots = historyPoints.asMap().entries.map((entry) {
      return FlSpot(entry.key.toDouble(), entry.value);
    }).toList();

    final minY = historyPoints.isNotEmpty ? historyPoints.reduce((a, b) => a < b ? a : b) * 0.98 : 10000.0;
    final maxY = historyPoints.isNotEmpty ? historyPoints.reduce((a, b) => a > b ? a : b) * 1.02 : 13000.0;

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: BorderSide(color: theme.colorScheme.outline),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Portfolio Performance',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: primaryColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    '7 Days',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: primaryColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            SizedBox(
              height: 160,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    getDrawingHorizontalLine: (value) {
                      return FlLine(
                        color: theme.colorScheme.outline.withOpacity(0.5),
                        strokeWidth: 1,
                      );
                    },
                  ),
                  titlesData: FlTitlesData(
                    show: true,
                    rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 24,
                        getTitlesWidget: (value, meta) {
                          const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                          final index = value.toInt();
                          if (index >= 0 && index < days.length) {
                            return Text(
                              days[index],
                              style: theme.textTheme.labelSmall?.copyWith(
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                            );
                          }
                          return const Text('');
                        },
                      ),
                    ),
                  ),
                  borderData: FlBorderData(show: false),
                  minX: 0,
                  maxX: 6,
                  minY: minY,
                  maxY: maxY,
                  lineBarsData: [
                    LineChartBarData(
                      spots: spots,
                      isCurved: true,
                      color: primaryColor,
                      barWidth: 3,
                      isStrokeCapRound: true,
                      dotData: const FlDotData(show: false),
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          colors: [
                            primaryColor.withOpacity(0.35),
                            primaryColor.withOpacity(0.0),
                          ],
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
