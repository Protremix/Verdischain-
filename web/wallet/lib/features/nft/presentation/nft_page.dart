import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../domain/nft_repository.dart';
import 'nft_providers.dart';
import 'widgets/nft_gallery.dart';

/// NFT Feature Main Page with TabBar (Collections | Gallery | Activity),
/// collection filter pills, search bar, sort options, and activity feed.
class NftPage extends ConsumerStatefulWidget {
  const NftPage({super.key});

  @override
  ConsumerState<NftPage> createState() => _NftPageState();
}

class _NftPageState extends ConsumerState<NftPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
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
    final selectedFilter = ref.watch(nftSelectedCollectionFilterProvider);
    final selectedSort = ref.watch(nftSortOptionProvider);
    final collectionsAsync = ref.watch(nftCollectionsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('NFT Portfolio'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh NFTs',
            onPressed: () {
              ref.invalidate(nftAssetsProvider);
              ref.invalidate(nftCollectionsProvider);
              ref.invalidate(nftActivityProvider);
            },
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: theme.colorScheme.primary,
          labelColor: theme.colorScheme.primary,
          unselectedLabelColor: theme.colorScheme.onSurfaceVariant,
          tabs: const [
            Tab(text: 'Gallery'),
            Tab(text: 'Collections'),
            Tab(text: 'Activity'),
          ],
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Search and Sort Bar (visible on Gallery tab)
            AnimatedBuilder(
              animation: _tabController,
              builder: (context, _) {
                if (_tabController.index != 0) {
                  return const SizedBox.shrink();
                }

                return Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                  child: Row(
                    children: [
                      // Search Bar
                      Expanded(
                        child: TextField(
                          controller: _searchController,
                          onChanged: (val) {
                            ref.read(nftSearchQueryProvider.notifier).state = val;
                          },
                          decoration: InputDecoration(
                            hintText: 'Search NFT name or asset ID...',
                            prefixIcon: const Icon(Icons.search, size: 20),
                            suffixIcon: _searchController.text.isNotEmpty
                                ? IconButton(
                                    icon: const Icon(Icons.clear, size: 18),
                                    onPressed: () {
                                      _searchController.clear();
                                      ref
                                          .read(nftSearchQueryProvider.notifier)
                                          .state = '';
                                    },
                                  )
                                : null,
                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 10,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),

                      // Sort Options Popup Menu
                      PopupMenuButton<NftSortOption>(
                        initialValue: selectedSort,
                        tooltip: 'Sort NFTs',
                        icon: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: theme.colorScheme.surfaceContainerHighest,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: theme.colorScheme.outline,
                            ),
                          ),
                          child: Icon(
                            Icons.tune,
                            color: theme.colorScheme.primary,
                            size: 20,
                          ),
                        ),
                        onSelected: (option) {
                          ref.read(nftSortOptionProvider.notifier).state = option;
                        },
                        itemBuilder: (context) => [
                          const PopupMenuItem(
                            value: NftSortOption.recentlyMinted,
                            child: Text('Recently Added'),
                          ),
                          const PopupMenuItem(
                            value: NftSortOption.rarityRankAsc,
                            child: Text('Rarity (Highest First)'),
                          ),
                          const PopupMenuItem(
                            value: NftSortOption.nameAsc,
                            child: Text('Name (A-Z)'),
                          ),
                          const PopupMenuItem(
                            value: NftSortOption.assetIdAsc,
                            child: Text('Token ID'),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),

            // Horizontal Collection Filter Pills (visible on Gallery tab)
            AnimatedBuilder(
              animation: _tabController,
              builder: (context, _) {
                if (_tabController.index != 0) {
                  return const SizedBox.shrink();
                }

                return collectionsAsync.when(
                  data: (collections) {
                    return SizedBox(
                      height: 48,
                      child: ListView(
                        scrollDirection: Axis.horizontal,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 4,
                        ),
                        children: [
                          // 'All' Filter Pill
                          Padding(
                            padding: const EdgeInsets.only(right: 8.0),
                            child: FilterChip(
                              label: const Text('All Collections'),
                              selected: selectedFilter == null,
                              onSelected: (_) {
                                ref
                                    .read(
                                      nftSelectedCollectionFilterProvider.notifier,
                                    )
                                    .state = null;
                              },
                            ),
                          ),

                          ...collections.map((coll) {
                            final isSelected = selectedFilter == coll.id;
                            return Padding(
                              padding: const EdgeInsets.only(right: 8.0),
                              child: FilterChip(
                                label: Text(coll.name),
                                selected: isSelected,
                                onSelected: (_) {
                                  ref
                                      .read(
                                        nftSelectedCollectionFilterProvider.notifier,
                                      )
                                      .state = coll.id;
                                },
                              ),
                            );
                          }),
                        ],
                      ),
                    );
                  },
                  loading: () => const SizedBox.shrink(),
                  error: (_, __) => const SizedBox.shrink(),
                );
              },
            ),

            // Tab Views
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  // Tab 1: Gallery Tab
                  _buildGalleryTab(context),

                  // Tab 2: Collections Tab
                  _buildCollectionsTab(context),

                  // Tab 3: Activity Tab
                  _buildActivityTab(context),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGalleryTab(BuildContext context) {
    final filteredAssetsAsync = ref.watch(filteredNftAssetsProvider);

    return filteredAssetsAsync.when(
      data: (assets) => NftGallery(
        assets: assets,
        onRefresh: () => ref.invalidate(nftAssetsProvider),
      ),
      loading: () => const NftGallery(assets: [], isLoading: true),
      error: (err, stack) => EmptyState(
        icon: Icons.error_outline,
        title: 'Error Loading NFTs',
        subtitle: err.toString(),
        actionLabel: 'Retry',
        onAction: () => ref.invalidate(nftAssetsProvider),
      ),
    );
  }

  Widget _buildCollectionsTab(BuildContext context) {
    final collectionsAsync = ref.watch(nftCollectionsProvider);
    final theme = Theme.of(context);

    return collectionsAsync.when(
      data: (collections) {
        if (collections.isEmpty) {
          return const EmptyState(
            icon: Icons.collections_bookmark_outlined,
            title: 'No Collections Found',
          );
        }

        return ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: collections.length,
          separatorBuilder: (_, __) => const SizedBox(height: 16),
          itemBuilder: (context, index) {
            final coll = collections[index];

            return VerdisCard(
              padding: EdgeInsets.zero,
              onTap: () {
                // Filter gallery by this collection and jump to Gallery tab
                ref
                    .read(nftSelectedCollectionFilterProvider.notifier)
                    .state = coll.id;
                _tabController.animateTo(0);
              },
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Banner or Cover Image
                  ClipRRect(
                    borderRadius:
                        const BorderRadius.vertical(top: Radius.circular(16)),
                    child: SizedBox(
                      height: 120,
                      width: double.infinity,
                      child: CachedNetworkImage(
                        imageUrl: coll.bannerUrl ?? coll.imageUrl,
                        fit: BoxFit.cover,
                        placeholder: (_, __) =>
                            Container(color: theme.colorScheme.surfaceContainerHighest),
                        errorWidget: (_, __, ___) => Container(
                          color: theme.colorScheme.surfaceContainerHighest,
                          child: const Icon(Icons.image),
                        ),
                      ),
                    ),
                  ),

                  // Info details
                  Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              width: 44,
                              height: 44,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: theme.colorScheme.primary,
                                  width: 2,
                                ),
                              ),
                              child: ClipOval(
                                child: CachedNetworkImage(
                                  imageUrl: coll.imageUrl,
                                  fit: BoxFit.cover,
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    coll.name,
                                    style: theme.textTheme.titleMedium?.copyWith(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  Text(
                                    '${coll.symbol} • ${coll.itemCount} items',
                                    style: theme.textTheme.bodySmall,
                                  ),
                                ],
                              ),
                            ),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Text(
                                  'Floor Price',
                                  style: theme.textTheme.labelSmall,
                                ),
                                Text(
                                  '${coll.floorPrice.toStringAsFixed(1)} VRDX',
                                  style: theme.textTheme.titleSmall?.copyWith(
                                    color: theme.colorScheme.primary,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                        if (coll.description.isNotEmpty) ...[
                          const SizedBox(height: 12),
                          Text(
                            coll.description,
                            style: theme.textTheme.bodySmall,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
      loading: () => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: 3,
        separatorBuilder: (_, __) => const SizedBox(height: 16),
        itemBuilder: (_, __) => const ShimmerPlaceholder(height: 180),
      ),
      error: (err, __) => EmptyState(
        icon: Icons.error_outline,
        title: 'Error loading collections',
        subtitle: err.toString(),
      ),
    );
  }

  Widget _buildActivityTab(BuildContext context) {
    final activityAsync = ref.watch(nftActivityProvider);
    final theme = Theme.of(context);

    return activityAsync.when(
      data: (activities) {
        if (activities.isEmpty) {
          return const EmptyState(
            icon: Icons.history_toggle_off,
            title: 'No Recent Activity',
          );
        }

        return ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: activities.length,
          separatorBuilder: (_, __) => const SizedBox(height: 12),
          itemBuilder: (context, index) {
            final act = activities[index];

            IconData icon;
            Color iconColor;
            switch (act.type) {
              case 'mint':
                icon = Icons.auto_awesome;
                iconColor = theme.colorScheme.primary;
                break;
              case 'sale':
                icon = Icons.shopping_bag_outlined;
                iconColor = theme.colorScheme.secondary;
                break;
              default:
                icon = Icons.swap_horiz_rounded;
                iconColor = const Color(0xFF2196F3);
            }

            return VerdisCard(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  CircleAvatar(
                    backgroundColor: iconColor.withOpacity(0.15),
                    child: Icon(icon, color: iconColor, size: 20),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          act.assetName,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${act.type.toUpperCase()} • From ${act.from.substring(0, 6)} to ${act.to.substring(0, 6)}',
                          style: theme.textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      if (act.price != null)
                        Text(
                          '${act.price} VRDX',
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: theme.colorScheme.primary,
                          ),
                        ),
                      Text(
                        '${act.timestamp.day}/${act.timestamp.month} ${act.timestamp.hour}:${act.timestamp.minute.toString().padLeft(2, '0')}',
                        style: theme.textTheme.labelSmall,
                      ),
                    ],
                  ),
                ],
              ),
            );
          },
        );
      },
      loading: () => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: 4,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (_, __) => const ShimmerPlaceholder(height: 72),
      ),
      error: (err, __) => EmptyState(
        icon: Icons.error_outline,
        title: 'Error loading activity',
        subtitle: err.toString(),
      ),
    );
  }
}
