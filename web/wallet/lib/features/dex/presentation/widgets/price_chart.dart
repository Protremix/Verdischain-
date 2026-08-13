import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../domain/dex_repository.dart';
import '../dex_providers.dart';

/// Interactive price chart component built with fl_chart
class PriceChart extends ConsumerStatefulWidget {

  const PriceChart({
    super.key,
    required this.poolId,
    required this.tokenPair,
  });
  final int poolId;
  final String tokenPair;

  @override
  ConsumerState<PriceChart> createState() => _PriceChartState();
}

class _PriceChartState extends ConsumerState<PriceChart> {
  PricePoint? _selectedPoint;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final timeframe = ref.watch(selectedTimeframeProvider);
    final historyAsync = ref.watch(
      priceHistoryProvider(ChartParams(widget.poolId, timeframe)),
    );

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: theme.colorScheme.outline),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Timeframe selector & header stats
          historyAsync.when(
            data: (points) {
              if (points.isEmpty) return const SizedBox.shrink();

              final first = points.first.price;
              final latest = points.last.price;
              final change = first > 0 ? ((latest - first) / first) * 100 : 0.0;
              final isPositive = change >= 0;

              final activePoint = _selectedPoint ?? points.last;

              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            widget.tokenPair,
                            style: theme.textTheme.titleMedium?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Row(
                            children: [
                              Text(
                                '\$${activePoint.price < 0.01 ? activePoint.price.toStringAsFixed(6) : activePoint.price.toStringAsFixed(4)}',
                                style: theme.textTheme.headlineMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(
                                  color: (isPositive ? theme.colorScheme.primary : theme.colorScheme.error)
                                      .withOpacity(0.15),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  '${isPositive ? '+' : ''}${change.toStringAsFixed(2)}%',
                                  style: theme.textTheme.labelSmall?.copyWith(
                                    color: isPositive ? theme.colorScheme.primary : theme.colorScheme.error,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          Text(
                            DateFormat('MMM dd, yyyy - HH:mm').format(activePoint.timestamp),
                            style: theme.textTheme.bodySmall,
                          ),
                        ],
                      ),
                      _buildTimeframeSelector(ref, timeframe, theme),
                    ],
                  ),
                  const SizedBox(height: 20),

                  // Line chart & Volume bar chart
                  SizedBox(
                    height: 180,
                    child: LineChart(
                      _buildLineChartData(points, theme),
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Volume chart section
                  SizedBox(
                    height: 48,
                    child: BarChart(
                      _buildVolumeChartData(points, theme),
                    ),
                  ),
                ],
              );
            },
            loading: () => const SizedBox(
              height: 240,
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (err, _) => SizedBox(
              height: 240,
              child: Center(
                child: Text('Unable to load chart data', style: theme.textTheme.bodySmall),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTimeframeSelector(WidgetRef ref, String current, ThemeData theme) {
    final options = ['24h', '7d', '30d'];
    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(10),
      ),
      padding: const EdgeInsets.all(2),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: options.map((tf) {
          final isSelected = current == tf;
          return GestureDetector(
            onTap: () {
              ref.read(selectedTimeframeProvider.notifier).state = tf;
              setState(() => _selectedPoint = null);
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: isSelected ? theme.colorScheme.primary : Colors.transparent,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                tf,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  color: isSelected ? Colors.black : theme.colorScheme.onSurface,
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  LineChartData _buildLineChartData(List<PricePoint> points, ThemeData theme) {
    final spots = <FlSpot>[];
    for (int i = 0; i < points.length; i++) {
      spots.add(FlSpot(i.toDouble(), points[i].price));
    }

    final minPrice = points.map((p) => p.price).reduce((a, b) => a < b ? a : b) * 0.98;
    final maxPrice = points.map((p) => p.price).reduce((a, b) => a > b ? a : b) * 1.02;

    return LineChartData(
      minY: minPrice,
      maxY: maxPrice,
      gridData: FlGridData(
        show: true,
        drawVerticalLine: false,
        getDrawingHorizontalLine: (value) => FlLine(
          color: theme.colorScheme.outline.withOpacity(0.3),
          strokeWidth: 1,
        ),
      ),
      titlesData: const FlTitlesData(
        leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
      ),
      borderData: FlBorderData(show: false),
      lineTouchData: LineTouchData(
        enabled: true,
        touchTooltipData: LineTouchTooltipData(
          getTooltipColor: (spot) => theme.colorScheme.surfaceContainerHighest,
          getTooltipItems: (touchedSpots) {
            return touchedSpots.map((spot) {
              final idx = spot.spotIndex;
              if (idx >= 0 && idx < points.length) {
                final pt = points[idx];
                return LineTooltipItem(
                  '\$${pt.price.toStringAsFixed(4)}',
                  TextStyle(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.bold,
                  ),
                );
              }
              return null;
            }).toList();
          },
        ),
        touchCallback: (event, response) {
          if (response?.lineBarSpots != null && response!.lineBarSpots!.isNotEmpty) {
            final idx = response.lineBarSpots!.first.spotIndex;
            if (idx >= 0 && idx < points.length) {
              setState(() {
                _selectedPoint = points[idx];
              });
            }
          }
        },
      ),
      lineBarsData: [
        LineChartBarData(
          spots: spots,
          isCurved: true,
          barWidth: 2.5,
          color: theme.colorScheme.primary,
          dotData: const FlDotData(show: false),
          belowBarData: BarAreaData(
            show: true,
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                theme.colorScheme.primary.withOpacity(0.25),
                theme.colorScheme.primary.withOpacity(0.0),
              ],
            ),
          ),
        ),
      ],
    );
  }

  BarChartData _buildVolumeChartData(List<PricePoint> points, ThemeData theme) {
    final maxVol = points.map((p) => p.volume).reduce((a, b) => a > b ? a : b);

    final groups = <BarChartGroupData>[];
    for (int i = 0; i < points.length; i++) {
      groups.add(
        BarChartGroupData(
          x: i,
          barRods: [
            BarChartRodData(
              toY: points[i].volume,
              color: theme.colorScheme.primary.withOpacity(0.4),
              width: 3,
              borderRadius: BorderRadius.circular(1),
            ),
          ],
        ),
      );
    }

    return BarChartData(
      maxY: maxVol * 1.1,
      gridData: const FlGridData(show: false),
      titlesData: const FlTitlesData(
        leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
      ),
      borderData: FlBorderData(show: false),
      barGroups: groups,
    );
  }
}
