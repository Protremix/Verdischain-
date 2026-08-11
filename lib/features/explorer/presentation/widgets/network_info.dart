import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../explorer_providers.dart';

class NetworkInfoWidget extends ConsumerWidget {
  const NetworkInfoWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final networkState = ref.watch(networkInfoProvider);
    final theme = Theme.of(context);

    return networkState.when(
      loading: () => ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          ShimmerPlaceholder(height: 160),
          SizedBox(height: 16),
          ShimmerPlaceholder(height: 240),
        ],
      ),
      error: (error, _) => Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.redAccent),
            const SizedBox(height: 12),
            Text('Failed to load network info', style: theme.textTheme.titleMedium),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => ref.refresh(networkInfoProvider),
              child: const Text('Retry'),
            ),
          ],
        ),
      ),
      data: (data) {
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // TPS Chart Card
            VerdisCard(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.speed_rounded, color: theme.colorScheme.primary, size: 20),
                          const SizedBox(width: 8),
                          Text('Live Throughput (TPS)', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primary.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          '${data.currentTps.toStringAsFixed(1)} TPS',
                          style: TextStyle(
                            color: theme.colorScheme.primary,
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    height: 120,
                    child: LineChart(
                      LineChartData(
                        gridData: const FlGridData(show: false),
                        titlesData: const FlTitlesData(show: false),
                        borderData: FlBorderData(show: false),
                        lineBarsData: [
                          LineChartBarData(
                            spots: data.tpsHistory.asMap().entries.map((entry) {
                              return FlSpot(entry.key.toDouble(), entry.value);
                            }).toList(),
                            isCurved: true,
                            color: theme.colorScheme.primary,
                            barWidth: 3,
                            isStrokeCapRound: true,
                            dotData: const FlDotData(show: false),
                            belowBarData: BarAreaData(
                              show: true,
                              color: theme.colorScheme.primary.withOpacity(0.15),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Peak Observed: ${data.peakTps.toInt()} TPS', style: theme.textTheme.labelSmall),
                      Text('Target Max: 2,500 TPS', style: theme.textTheme.labelSmall),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Network Specifications Grid/List
            VerdisCard(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.hub_rounded, color: theme.colorScheme.primary, size: 20),
                      const SizedBox(width: 8),
                      Text('Chain Properties', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildPropertyRow(context, 'Chain Name', data.chainName),
                  _buildPropertyRow(context, 'Chain Type', data.chainType),
                  _buildPropertyRow(context, 'Consensus', data.consensus),
                  _buildPropertyRow(context, 'Runtime Version', data.runtimeVersion),
                  _buildPropertyRow(context, 'Spec Version', 'v${data.specVersion}'),
                  _buildPropertyRow(context, 'Genesis Hash', _shortenHash(data.genesisHash), isMonospace: true, fullValue: data.genesisHash),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Live Consensus & Blocks Card
            VerdisCard(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.cloud_done_rounded, color: theme.colorScheme.primary, size: 20),
                      const SizedBox(width: 8),
                      Text('Live Consensus State', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildPropertyRow(context, 'Best Block Height', '#${data.bestBlock}'),
                  _buildPropertyRow(context, 'Finalized Block', '#${data.finalizedBlock}'),
                  _buildPropertyRow(context, 'Connected Peers', '${data.peers} nodes'),
                  _buildPropertyRow(context, 'Finality Lag', '${data.bestBlock - data.finalizedBlock} blocks'),
                ],
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildPropertyRow(BuildContext context, String label, String value, {bool isMonospace = false, String? fullValue}) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
          SelectableText(
            value,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
              fontFamily: isMonospace ? 'Monospace' : null,
            ),
          ),
        ],
      ),
    );
  }

  String _shortenHash(String hash) {
    if (hash.length <= 16) return hash;
    return '${hash.substring(0, 10)}...${hash.substring(hash.length - 8)}';
  }
}
