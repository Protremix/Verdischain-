import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'dex_providers.dart';
import 'widgets/pool_card.dart';

/// Pools Page listing all DEX liquidity pools with search and filter options
class PoolsPage extends ConsumerStatefulWidget {

  const PoolsPage({super.key, this.onPoolAction});
  final Function(DexPool pool, String action)? onPoolAction;

  @override
  ConsumerState<PoolsPage> createState() => _PoolsPageState();
}

class _PoolsPageState extends ConsumerState<PoolsPage> {
  final TextEditingController _searchController = TextEditingController();
  String _selectedFilter = 'All';

  @override
  void initState() {
    super.initState();
    _searchController.addListener(() {
      setState(() {});
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final primary = theme.colorScheme.primary;

    final poolsAsync = ref.watch(poolsProvider);

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(poolsProvider);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Search Bar & Filters
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _searchController,
                      decoration: InputDecoration(
                        hintText: 'Search pool or token...',
                        prefixIcon: const Icon(Icons.search, size: 20),
                        suffixIcon: _searchController.text.isNotEmpty
                            ? IconButton(
                                icon: const Icon(Icons.clear, size: 18),
                                onPressed: () => _searchController.clear(),
                              )
                            : null,
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Filter Chips
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: ['All', 'High TVL', 'High APR', 'Stable'].map((filter) {
                    final isSelected = _selectedFilter == filter;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ChoiceChip(
                        label: Text(filter),
                        selected: isSelected,
                        onSelected: (_) {
                          setState(() {
                            _selectedFilter = filter;
                          });
                        },
                        selectedColor: primary,
                        labelStyle: TextStyle(
                          color: isSelected ? Colors.black : theme.colorScheme.onSurface,
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),

              const SizedBox(height: 16),

              // Pools list
              poolsAsync.when(
                data: (pools) {
                  final filtered = _filterPools(pools);

                  if (filtered.isEmpty) {
                    return const EmptyState(
                      icon: Icons.search_off,
                      title: 'No Liquidity Pools Found',
                      subtitle: 'Try adjusting your search terms or filters.',
                    );
                  }

                  return ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: filtered.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 12),
                    itemBuilder: (context, index) {
                      final pool = filtered[index];
                      return PoolCard(
                        pool: pool,
                        onSwap: () {
                          ref.read(selectedPoolProvider.notifier).state = pool;
                          ref.read(swapInputTokenProvider.notifier).state = pool.tokenA;
                          ref.read(swapOutputTokenProvider.notifier).state = pool.tokenB;
                          widget.onPoolAction?.call(pool, 'swap');
                        },
                        onAddLiquidity: () {
                          ref.read(selectedPoolProvider.notifier).state = pool;
                          widget.onPoolAction?.call(pool, 'add_liquidity');
                        },
                      );
                    },
                  );
                },
                loading: () => ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: 3,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (_, __) => const ShimmerPlaceholder(height: 180),
                ),
                error: (err, stack) => EmptyState(
                  icon: Icons.error_outline,
                  title: 'Failed to load pools',
                  subtitle: err.toString(),
                  actionLabel: 'Retry',
                  onAction: () => ref.invalidate(poolsProvider),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  List<DexPool> _filterPools(List<DexPool> pools) {
    var result = pools;

    // Search query filter
    final query = _searchController.text.trim().toLowerCase();
    if (query.isNotEmpty) {
      result = result.where((p) {
        return p.tokenA.toLowerCase().contains(query) ||
            p.tokenB.toLowerCase().contains(query) ||
            '${p.tokenA}/${p.tokenB}'.toLowerCase().contains(query);
      }).toList();
    }

    // Category filter
    if (_selectedFilter == 'High TVL') {
      result.sort((a, b) => b.reserveB.compareTo(a.reserveB));
    } else if (_selectedFilter == 'High APR') {
      result.sort((a, b) => b.totalVolume24h.compareTo(a.totalVolume24h));
    } else if (_selectedFilter == 'Stable') {
      result = result.where((p) => (p.tokenA == 'USDT' || p.tokenA == 'USDC') && (p.tokenB == 'USDT' || p.tokenB == 'USDC')).toList();
    }

    return result;
  }
}
