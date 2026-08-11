import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'explorer_providers.dart';
import 'widgets/block_list.dart';
import 'widgets/network_info.dart';
import 'widgets/tx_list.dart';
import 'widgets/validator_list.dart';

enum SearchResultType { block, transaction, address, validator, notFound }

class ExplorerPage extends ConsumerStatefulWidget {
  const ExplorerPage({super.key});

  @override
  ConsumerState<ExplorerPage> createState() => _ExplorerPageState();
}

class _ExplorerPageState extends ConsumerState<ExplorerPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final networkState = ref.watch(networkInfoProvider);
    final searchQuery = ref.watch(searchQueryProvider);
    final isSearching = searchQuery.isNotEmpty;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Verdis Block Explorer'),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () {
              ref.invalidate(networkInfoProvider);
              ref.read(blocksProvider.notifier).refresh();
              ref.read(txsProvider.notifier).refresh();
            },
            tooltip: 'Refresh explorer data',
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Network Stats Header Bar
            networkState.when(
              data: (net) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: theme.colorScheme.outline),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildStatBadge(
                      context,
                      label: 'Block Height',
                      value: '#${net.bestBlock}',
                      icon: Icons.tag_rounded,
                    ),
                    Container(height: 24, width: 1, color: theme.colorScheme.outline),
                    _buildStatBadge(
                      context,
                      label: 'Network TPS',
                      value: net.currentTps.toStringAsFixed(1),
                      icon: Icons.speed_rounded,
                    ),
                    Container(height: 24, width: 1, color: theme.colorScheme.outline),
                    _buildStatBadge(
                      context,
                      label: 'Active Peers',
                      value: '${net.peers}',
                      icon: Icons.hub_rounded,
                    ),
                  ],
                ),
              ),
              loading: () => const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: ShimmerPlaceholder(height: 60),
              ),
              error: (_, __) => const SizedBox.shrink(),
            ),

            // Search Bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'Search block number, hash, or address...',
                  prefixIcon: const Icon(Icons.search_rounded),
                  suffixIcon: isSearching
                      ? IconButton(
                          icon: const Icon(Icons.clear_rounded),
                          onPressed: () {
                            _searchController.clear();
                            ref.read(searchQueryProvider.notifier).state = '';
                          },
                        )
                      : null,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                ),
                onSubmitted: (value) {
                  ref.read(searchQueryProvider.notifier).state = value;
                },
                onChanged: (value) {
                  if (value.isEmpty) {
                    ref.read(searchQueryProvider.notifier).state = '';
                  }
                },
              ),
            ),

            // Tab Bar
            if (!isSearching) ...[
              TabBar(
                controller: _tabController,
                indicatorColor: theme.colorScheme.primary,
                labelColor: theme.colorScheme.primary,
                unselectedLabelColor: theme.colorScheme.onSurfaceVariant,
                indicatorSize: TabBarIndicatorSize.tab,
                tabs: const [
                  Tab(text: 'Blocks'),
                  Tab(text: 'Transactions'),
                  Tab(text: 'Validators'),
                  Tab(text: 'Network'),
                ],
              ),
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: const [
                    BlockListWidget(),
                    TxListWidget(),
                    ValidatorListWidget(),
                    NetworkInfoWidget(),
                  ],
                ),
              ),
            ] else ...[
              // Search Results View
              Expanded(
                child: _SearchResultsView(query: searchQuery),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatBadge(BuildContext context, {required String label, required String value, required IconData icon}) {
    final theme = Theme.of(context);
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: theme.colorScheme.primary),
            const SizedBox(width: 4),
            Text(
              value,
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: theme.textTheme.labelSmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
            fontSize: 10,
          ),
        ),
      ],
    );
  }
}

class _SearchResultsView extends ConsumerWidget {

  const _SearchResultsView({required this.query});
  final String query;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final searchAsync = ref.watch(searchProvider);
    final theme = Theme.of(context);

    return searchAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('Search error: $e')),
      data: (result) {
        if (result == null || result.type.index == SearchResultType.notFound.index) {
          return EmptyState(
            icon: Icons.search_off_rounded,
            title: 'No search results',
            subtitle: 'Could not find block, transaction, or address matching:\n"$query"',
          );
        }

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(
              'Search Result for "$query"',
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            if (result.block != null) ...[
              VerdisCard(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.dns_rounded, color: theme.colorScheme.primary),
                        const SizedBox(width: 8),
                        Text('Block #${result.block!.number}', style: theme.textTheme.titleMedium),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text('Hash: ${result.block!.hash}', style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'Monospace')),
                    Text('Validator: ${result.block!.validator}', style: theme.textTheme.bodySmall),
                    Text('Txs: ${result.block!.extrinsicCount}', style: theme.textTheme.bodySmall),
                  ],
                ),
              ),
            ],
            if (result.transaction != null) ...[
              VerdisCard(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.swap_horiz_rounded, color: theme.colorScheme.primary),
                        const SizedBox(width: 8),
                        Text('Transaction ${result.transaction!.module}.${result.transaction!.call}', style: theme.textTheme.titleMedium),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text('Hash: ${result.transaction!.hash}', style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'Monospace')),
                    Text('From: ${result.transaction!.from}', style: theme.textTheme.bodySmall),
                    Text('Status: ${result.transaction!.status}', style: theme.textTheme.bodySmall),
                  ],
                ),
              ),
            ],
            if (result.validator != null) ...[
              VerdisCard(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.shield_rounded, color: Colors.greenAccent),
                        const SizedBox(width: 8),
                        Text(result.validator!.name, style: theme.textTheme.titleMedium),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text('Address: ${result.validator!.address}', style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'Monospace')),
                    Text('Eco Score: ${result.validator!.greenScore}/100', style: theme.textTheme.bodySmall),
                  ],
                ),
              ),
            ],
            if (result.accountAddress != null) ...[
              VerdisCard(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.account_circle_rounded, color: theme.colorScheme.primary),
                        const SizedBox(width: 8),
                        Text('Verdis Account', style: theme.textTheme.titleMedium),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text('Address: ${result.accountAddress}', style: theme.textTheme.bodyMedium?.copyWith(fontFamily: 'Monospace')),
                  ],
                ),
              ),
            ],
          ],
        );
      },
    );
  }
}
