import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'staking_providers.dart';

class RewardsChart extends ConsumerWidget {
  const RewardsChart({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final rewardsAsync = ref.watch(rewardsProvider);

    return rewardsAsync.when(
      data: (rewards) {
        if (rewards.dailyBreakdown.isEmpty) {
          return const EmptyState(
            icon: Icons.show_chart_rounded,
            title: 'No Reward History Yet',
            subtitle: 'Stake VRD with active validators to start earning daily rewards.',
          );
        }

        final points = rewards.dailyBreakdown;
        final maxReward = points.fold<double>(
          0.0,
          (max, p) => p.amount > max ? p.amount : max,
        );
        final avgDaily = rewards.totalRewards / points.length;

        // Convert points to FlSpot
        final spots = List.generate(points.length, (index) {
          return FlSpot(index.toDouble(), points[index].amount);
        });

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top Metrics Summary Cards
            Row(
              children: [
                Expanded(
                  child: VerdisCard(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('30-Day Rewards', style: theme.textTheme.labelSmall),
                        const SizedBox(height: 6),
                        Text(
                          '+${rewards.totalRewards.toStringAsFixed(2)} VRD',
                          style: theme.textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: theme.colorScheme.primary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: VerdisCard(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Avg. Daily Reward', style: theme.textTheme.labelSmall),
                        const SizedBox(height: 6),
                        Text(
                          '+${avgDaily.toStringAsFixed(2)} VRD',
                          style: theme.textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 20),

            // Line Chart Section Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '30-Day Rewards Trend',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primary.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    'Peak: +${maxReward.toStringAsFixed(1)} VRD',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // fl_chart LineChart Container
            Container(
              height: 220,
              padding: const EdgeInsets.only(right: 16, left: 4, top: 16, bottom: 8),
              decoration: BoxDecoration(
                color: theme.colorScheme.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: theme.colorScheme.outline),
              ),
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    horizontalInterval: (maxReward / 3) > 0 ? (maxReward / 3) : 1,
                    getDrawingHorizontalLine: (value) => FlLine(
                      color: theme.colorScheme.outline.withOpacity(0.5),
                      strokeWidth: 1,
                      dashArray: [4, 4],
                    ),
                  ),
                  titlesData: FlTitlesData(
                    show: true,
                    rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 36,
                        interval: (maxReward / 3) > 0 ? (maxReward / 3) : 1,
                        getTitlesWidget: (value, meta) {
                          return Text(
                            value.toStringAsFixed(1),
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                              fontSize: 10,
                            ),
                          );
                        },
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 24,
                        interval: 6,
                        getTitlesWidget: (value, meta) {
                          final idx = value.toInt();
                          if (idx >= 0 && idx < points.length) {
                            final date = points[idx].date;
                            return Padding(
                              padding: const EdgeInsets.only(top: 6),
                              child: Text(
                                DateFormat('d MMM').format(date),
                                style: theme.textTheme.labelSmall?.copyWith(
                                  color: theme.colorScheme.onSurfaceVariant,
                                  fontSize: 10,
                                ),
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
                  maxX: (points.length - 1).toDouble(),
                  minY: 0,
                  maxY: maxReward * 1.15,
                  lineTouchData: LineTouchData(
                    enabled: true,
                    touchTooltipData: LineTouchTooltipData(
                      getTooltipColor: (touchedSpot) => theme.colorScheme.surfaceContainerHighest,
                      getTooltipItems: (touchedSpots) {
                        return touchedSpots.map((spot) {
                          final idx = spot.x.toInt();
                          final date = points[idx].date;
                          final formattedDate = DateFormat('MMM d, yyyy').format(date);
                          return LineTooltipItem(
                            '$formattedDate\n',
                            theme.textTheme.labelSmall!,
                            children: [
                              TextSpan(
                                text: '+${spot.y.toStringAsFixed(2)} VRD',
                                style: TextStyle(
                                  color: theme.colorScheme.primary,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 13,
                                ),
                              ),
                            ],
                          );
                        }).toList();
                      },
                    ),
                  ),
                  lineBarsData: [
                    LineChartBarData(
                      spots: spots,
                      isCurved: true,
                      curveSmoothness: 0.35,
                      color: theme.colorScheme.primary,
                      barWidth: 3,
                      isStrokeCapRound: true,
                      dotData: const FlDotData(show: false),
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            theme.colorScheme.primary.withOpacity(0.35),
                            theme.colorScheme.primary.withOpacity(0.0),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Daily Rewards Breakdown List
            Text(
              'Recent Daily Claims',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),

            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: points.length > 7 ? 7 : points.length,
              separatorBuilder: (context, index) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final item = points[points.length - 1 - index];
                return ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary.withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(Icons.eco_rounded, color: theme.colorScheme.primary, size: 18),
                  ),
                  title: Text(
                    DateFormat('EEEE, MMM d').format(item.date),
                    style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
                  ),
                  subtitle: Text(
                    'Block Staking Reward',
                    style: theme.textTheme.bodySmall,
                  ),
                  trailing: Text(
                    '+${item.amount.toStringAsFixed(2)} VRD',
                    style: theme.textTheme.titleMedium?.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                );
              },
            ),
          ],
        );
      },
      loading: () => const Column(
        children: [
          ShimmerPlaceholder(height: 100),
          SizedBox(height: 16),
          ShimmerPlaceholder(height: 220),
        ],
      ),
      error: (err, stack) => EmptyState(
        icon: Icons.error_outline_rounded,
        title: 'Unable to Load Rewards',
        subtitle: err.toString(),
      ),
    );
  }
}
