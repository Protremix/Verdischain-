import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'dex_providers.dart';
import 'liquidity_page.dart';
import 'pools_page.dart';
import 'swap_page.dart';
import 'widgets/swap_settings.dart';

/// Main DEX Page featuring TVL & Volume banner, tabs for Swap, Liquidity, Pools
class DexPage extends ConsumerStatefulWidget {
  const DexPage({super.key});

  @override
  ConsumerState<DexPage> createState() => _DexPageState();
}

class _DexPageState extends ConsumerState<DexPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  String _formatCurrency(num value) {
    if (value >= 1000000) {
      return '\$${(value / 1000000).toStringAsFixed(2)}M';
    } else if (value >= 1000) {
      return '\$${(value / 1000).toStringAsFixed(1)}K';
    }
    return '\$${NumberFormat('#,##0').format(value)}';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final primary = theme.colorScheme.primary;
    final metrics = ref.watch(dexMetricsProvider);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('Verdis DEX'),
        centerTitle: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Refresh DEX Data',
            onPressed: () {
              ref.invalidate(poolsProvider);
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            tooltip: 'DEX Settings',
            onPressed: () => SwapSettingsSheet.show(context),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Top Header Card: Total Value Locked (TVL) & 24h Volume Banner
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: VerdisCard(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.lock_clock_outlined, size: 16, color: primary),
                              const SizedBox(width: 4),
                              Text('Total Value Locked', style: theme.textTheme.bodySmall),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _formatCurrency(metrics['tvl'] ?? 0.0),
                            style: theme.textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: primary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      height: 36,
                      width: 1,
                      color: theme.colorScheme.outline,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.bar_chart_rounded, size: 16, color: theme.colorScheme.secondary),
                              const SizedBox(width: 4),
                              Text('24h Volume', style: theme.textTheme.bodySmall),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _formatCurrency(metrics['volume24h'] ?? 0.0),
                            style: theme.textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Tab Bar: Swap | Liquidity | Pools
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: theme.colorScheme.surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: theme.colorScheme.outline),
              ),
              child: TabBar(
                controller: _tabController,
                indicator: BoxDecoration(
                  color: primary,
                  borderRadius: BorderRadius.circular(10),
                ),
                labelColor: Colors.black,
                unselectedLabelColor: theme.colorScheme.onSurface,
                labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                tabs: const [
                  Tab(text: 'Swap'),
                  Tab(text: 'Liquidity'),
                  Tab(text: 'Pools'),
                ],
              ),
            ),

            // TabBarView Content
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  const SwapPage(),
                  const LiquidityPage(),
                  PoolsPage(
                    onPoolAction: (pool, action) {
                      if (action == 'swap') {
                        _tabController.animateTo(0);
                      } else if (action == 'add_liquidity') {
                        _tabController.animateTo(1);
                      }
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
