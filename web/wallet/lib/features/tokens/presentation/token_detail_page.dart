import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../domain/token_repository.dart';
import 'tokens_providers.dart';

/// Comprehensive Token Detail Screen featuring info header, balance display,
/// fl_chart price history, send/receive buttons, and transfer history list.
class TokenDetailPage extends ConsumerStatefulWidget {

  const TokenDetailPage({
    super.key,
    required this.tokenId,
  });
  final String tokenId;

  @override
  ConsumerState<TokenDetailPage> createState() => _TokenDetailPageState();
}

class _TokenDetailPageState extends ConsumerState<TokenDetailPage> {
  String _selectedTimeframe = '7d';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final tokenAsync = ref.watch(tokenDetailProvider(widget.tokenId));
    final chartPointsAsync = ref.watch(tokenPriceChartProvider(widget.tokenId));
    final historyAsync = ref.watch(tokenHistoryProvider(widget.tokenId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Token Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.share_outlined),
            onPressed: () {
              // Share token contract
            },
          ),
        ],
      ),
      body: tokenAsync.when(
        data: (token) {
          if (token == null) {
            return const EmptyState(
              icon: Icons.error_outline,
              title: 'Token Not Found',
            );
          }

          final isPositive = token.change24h >= 0;

          return RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(tokenDetailProvider(widget.tokenId));
              ref.invalidate(tokenPriceChartProvider(widget.tokenId));
              ref.invalidate(tokenHistoryProvider(widget.tokenId));
            },
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 1. Token Header Card
                  VerdisCard(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        Row(
                          children: [
                            // Circular gradient icon
                            Container(
                              width: 56,
                              height: 56,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                gradient: LinearGradient(
                                  colors: token.gradientColors
                                      .map((c) => Color(c))
                                      .toList(),
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                ),
                              ),
                              child: Center(
                                child: Text(
                                  token.symbol.substring(
                                      0,
                                      token.symbol.length > 3
                                          ? 3
                                          : token.symbol.length,),
                                  style: const TextStyle(
                                    color: Colors.black,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 16,
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    token.name,
                                    style: theme.textTheme.headlineSmall?.copyWith(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    token.symbol,
                                    style: theme.textTheme.bodyMedium?.copyWith(
                                      color: theme.colorScheme.onSurfaceVariant,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            if (token.contractAddress != null)
                              AddressChip(
                                address: token.contractAddress!,
                                showCopy: true,
                              ),
                          ],
                        ),
                        const SizedBox(height: 20),
                        const Divider(),
                        const SizedBox(height: 16),

                        // Balance Display & USD price
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Your Balance',
                                  style: theme.textTheme.bodySmall,
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  '${token.balance.toStringAsFixed(2)} ${token.symbol}',
                                  style: theme.textTheme.headlineMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: theme.colorScheme.primary,
                                  ),
                                ),
                                Text(
                                  '≈ \$${token.usdValue.toStringAsFixed(2)} USD',
                                  style: theme.textTheme.bodyMedium?.copyWith(
                                    color: theme.colorScheme.onSurfaceVariant,
                                  ),
                                ),
                              ],
                            ),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Text(
                                  'Unit Price',
                                  style: theme.textTheme.bodySmall,
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  '\$${token.usdPrice.toStringAsFixed(2)}',
                                  style: theme.textTheme.titleLarge?.copyWith(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 3,),
                                  decoration: BoxDecoration(
                                    color: (isPositive
                                            ? theme.colorScheme.primary
                                            : theme.colorScheme.error)
                                        .withOpacity(0.15),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    '${isPositive ? '+' : ''}${token.change24h.toStringAsFixed(2)}% (24h)',
                                    style: theme.textTheme.labelSmall?.copyWith(
                                      color: isPositive
                                          ? theme.colorScheme.primary
                                          : theme.colorScheme.error,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),

                  // 2. Action Buttons Row (Send / Receive / Swap)
                  Row(
                    children: [
                      Expanded(
                        child: VerdisButton(
                          label: 'Send',
                          icon: Icons.north_east_rounded,
                          onPressed: () => _showSendModal(context, token),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: VerdisButton(
                          label: 'Receive',
                          icon: Icons.south_west_rounded,
                          isOutlined: true,
                          onPressed: () => _showReceiveModal(context, token),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // 3. Price History Chart Header & Timeframe Switcher
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Price Performance',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Row(
                        children: ['24h', '7d', '30d', '1y'].map((tf) {
                          final isSelected = _selectedTimeframe == tf;
                          return Padding(
                            padding: const EdgeInsets.only(left: 4),
                            child: InkWell(
                              onTap: () {
                                setState(() {
                                  _selectedTimeframe = tf;
                                });
                              },
                              borderRadius: BorderRadius.circular(8),
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 10, vertical: 6,),
                                decoration: BoxDecoration(
                                  color: isSelected
                                      ? theme.colorScheme.primary
                                      : theme.colorScheme.surfaceContainerHighest,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  tf,
                                  style: theme.textTheme.labelSmall?.copyWith(
                                    color: isSelected
                                        ? Colors.black
                                        : theme.colorScheme.onSurface,
                                    fontWeight: isSelected
                                        ? FontWeight.bold
                                        : FontWeight.normal,
                                  ),
                                ),
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                    ],
                  ),

                  const SizedBox(height: 16),

                  // Price Chart Container
                  VerdisCard(
                    padding: const EdgeInsets.all(16),
                    child: SizedBox(
                      height: 200,
                      child: chartPointsAsync.when(
                        data: (points) => _buildFlChart(context, points, isPositive),
                        loading: () => const Center(
                          child: CircularProgressIndicator(),
                        ),
                        error: (_, __) => const Center(
                          child: Text('Price chart unavailable'),
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // 4. Token Info Summary Grid
                  Text(
                    'Token Information',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: StatTile(
                          label: 'Total Supply',
                          value: '${(token.supply / 1e6).toStringAsFixed(1)}M',
                          icon: Icons.pie_chart_outline,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: StatTile(
                          label: 'Holders',
                          value: '${token.holderCount}',
                          icon: Icons.people_outline,
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // 5. Transfer History List
                  Text(
                    'Transfer History',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),

                  historyAsync.when(
                    data: (transfers) {
                      if (transfers.isEmpty) {
                        return const EmptyState(
                          icon: Icons.history,
                          title: 'No Transfers Yet',
                          subtitle: 'Your recent transaction history will show here.',
                        );
                      }

                      return Column(
                        children: transfers.map((tx) {
                          final isSend = tx.type == 'send';
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 8.0),
                            child: VerdisCard(
                              padding: const EdgeInsets.all(12),
                              child: Row(
                                children: [
                                  CircleAvatar(
                                    backgroundColor: (isSend
                                            ? theme.colorScheme.error
                                            : theme.colorScheme.primary)
                                        .withOpacity(0.15),
                                    child: Icon(
                                      isSend
                                          ? Icons.arrow_outward
                                          : Icons.arrow_downward,
                                      color: isSend
                                          ? theme.colorScheme.error
                                          : theme.colorScheme.primary,
                                      size: 20,
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          isSend ? 'Sent ${token.symbol}' : 'Received ${token.symbol}',
                                          style: theme.textTheme.titleMedium?.copyWith(
                                            fontSize: 14,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        Text(
                                          'Counterparty: ${tx.counterparty}',
                                          style: theme.textTheme.bodySmall,
                                        ),
                                      ],
                                    ),
                                  ),
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.end,
                                    children: [
                                      Text(
                                        '${isSend ? '-' : '+'}${tx.amount.toStringAsFixed(2)}',
                                        style: theme.textTheme.titleMedium?.copyWith(
                                          fontWeight: FontWeight.bold,
                                          color: isSend
                                              ? theme.colorScheme.error
                                              : theme.colorScheme.primary,
                                        ),
                                      ),
                                      Text(
                                        '${tx.timestamp.day}/${tx.timestamp.month} ${tx.timestamp.hour}:${tx.timestamp.minute.toString().padLeft(2, '0')}',
                                        style: theme.textTheme.labelSmall,
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          );
                        }).toList(),
                      );
                    },
                    loading: () => const ShimmerPlaceholder(height: 120),
                    error: (_, __) => const Text('Failed to load transaction history.'),
                  ),
                ],
              ),
            ),
          );
        },
        loading: () => const Scaffold(
          body: Center(child: CircularProgressIndicator()),
        ),
        error: (err, __) => Scaffold(
          body: Center(child: Text('Error loading token: $err')),
        ),
      ),
    );
  }

  Widget _buildFlChart(
      BuildContext context, List<TokenPricePoint> points, bool isPositive,) {
    final theme = Theme.of(context);
    if (points.isEmpty) {
      return const Center(child: Text('No chart data available'));
    }

    final minPrice = points.map((p) => p.price).reduce((a, b) => a < b ? a : b);
    final maxPrice = points.map((p) => p.price).reduce((a, b) => a > b ? a : b);

    final chartColor = isPositive ? theme.colorScheme.primary : theme.colorScheme.error;

    final spotList = points.asMap().entries.map((entry) {
      return FlSpot(entry.key.toDouble(), entry.value.price);
    }).toList();

    return LineChart(
      LineChartData(
        gridData: const FlGridData(show: false),
        titlesData: const FlTitlesData(show: false),
        borderData: FlBorderData(show: false),
        minY: minPrice * 0.98,
        maxY: maxPrice * 1.02,
        lineTouchData: LineTouchData(
          enabled: true,
          touchTooltipData: LineTouchTooltipData(
            getTooltipItems: (touchedSpots) {
              return touchedSpots.map((spot) {
                return LineTooltipItem(
                  '\$${spot.y.toStringAsFixed(2)}',
                  TextStyle(
                    color: theme.colorScheme.onSurface,
                    fontWeight: FontWeight.bold,
                  ),
                );
              }).toList();
            },
          ),
        ),
        lineBarsData: [
          LineChartBarData(
            spots: spotList,
            isCurved: true,
            color: chartColor,
            barWidth: 2.5,
            isStrokeCapRound: true,
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(
                colors: [
                  chartColor.withOpacity(0.25),
                  chartColor.withOpacity(0.0),
                ],
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showSendModal(BuildContext context, TokenModel token) {
    final addressCtrl = TextEditingController();
    final amountCtrl = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (modalCtx) => Padding(
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          top: 24,
          bottom: MediaQuery.of(modalCtx).viewInsets.bottom + 24,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Send ${token.symbol}',
                style: Theme.of(modalCtx).textTheme.headlineSmall,),
            const SizedBox(height: 16),
            TextField(
              controller: addressCtrl,
              decoration: const InputDecoration(
                labelText: 'Recipient Address',
                hintText: 'Enter 0x... or Verdis address',
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: amountCtrl,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: 'Amount (${token.symbol})',
                hintText: '0.00',
              ),
            ),
            const SizedBox(height: 24),
            VerdisButton(
              label: 'Confirm Transfer',
              onPressed: () {
                Navigator.pop(modalCtx);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Sent ${amountCtrl.text} ${token.symbol}')),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showReceiveModal(BuildContext context, TokenModel token) {
    final walletAddress = ref.read(userWalletAddressProvider);

    showModalBottomSheet(
      context: context,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (modalCtx) => Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Receive ${token.symbol}',
                style: Theme.of(modalCtx).textTheme.headlineSmall,),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Icon(Icons.qr_code_2, size: 160, color: Colors.black),
            ),
            const SizedBox(height: 16),
            AddressChip(address: walletAddress, showCopy: true),
            const SizedBox(height: 24),
            VerdisButton(
              label: 'Copy Address',
              icon: Icons.copy,
              onPressed: () => Navigator.pop(modalCtx),
            ),
          ],
        ),
      ),
    );
  }
}
