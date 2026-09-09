import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../domain/staking_repository.dart';
import 'rewards_chart.dart';
import 'staking_info_page.dart';
import 'staking_providers.dart';
import 'widgets/staking_position_card.dart';
import 'widgets/validator_list.dart';

class StakingPage extends ConsumerStatefulWidget {
  const StakingPage({super.key});

  @override
  ConsumerState<StakingPage> createState() => _StakingPageState();
}

class _StakingPageState extends ConsumerState<StakingPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
  }

  void conversationInit() {
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final positionsAsync = ref.watch(stakingPositionsProvider);
    final rewardsAsync = ref.watch(rewardsProvider);
    final historyAsync = ref.watch(stakingHistoryProvider);

    // Calculate aggregated totals
    final totalStaked = positionsAsync.when(
      data: (positions) => positions.fold<int>(0, (sum, p) => sum + p.amount),
      loading: () => 0,
      error: (_, __) => 0,
    );

    final totalRewards = rewardsAsync.when(
      data: (r) => r.claimableRewards,
      loading: () => 0.0,
      error: (_, __) => 0.0,
    );

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E0A),
      appBar: AppBar(
        title: const Text('Verdis Staking'),
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline_rounded),
            tooltip: 'Staking Guide',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const StakingInfoPage()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Refresh',
            onPressed: () {
              ref.invalidate(validatorsProvider);
              ref.invalidate(stakingPositionsProvider);
              ref.invalidate(rewardsProvider);
              ref.invalidate(stakingHistoryProvider);
            },
          ),
        ],
      ),
      body: NestedScrollView(
        headerSliverBuilder: (context, innerBoxIsScrolled) {
          return [
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    // Top Overview Metrics: Total Staked, Active Rewards, Estimated APY
                    Row(
                      children: [
                        // Total Staked Card
                        Expanded(
                          child: StatTile(
                            label: 'Total Staked',
                            value: '$totalStaked VRD',
                            icon: Icons.lock_clock_outlined,
                            iconColor: theme.colorScheme.primary,
                          ),
                        ),
                        const SizedBox(width: 10),
                        // Claimable Rewards Card
                        Expanded(
                          child: StatTile(
                            label: 'Active Rewards',
                            value: '${totalRewards.toStringAsFixed(0)} VRD',
                            icon: Icons.card_giftcard_rounded,
                            iconColor: const Color(0xFF00FF88),
                          ),
                        ),
                        const SizedBox(width: 10),
                        // Estimated APY Card
                        const Expanded(
                          child: StatTile(
                            label: 'Est. APY',
                            value: '13.8%',
                            icon: Icons.bolt_rounded,
                            iconColor: Color(0xFFFFB300),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 16),

                    // Navigation Tabs Header
                    Container(
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surface,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: theme.colorScheme.outline),
                      ),
                      child: TabBar(
                        controller: _tabController,
                        indicatorColor: theme.colorScheme.primary,
                        labelColor: theme.colorScheme.primary,
                        unselectedLabelColor: theme.colorScheme.onSurfaceVariant,
                        indicatorSize: TabBarIndicatorSize.tab,
                        dividerColor: Colors.transparent,
                        labelStyle: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                        unselectedLabelStyle: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.normal,
                        ),
                        tabs: const [
                          Tab(text: 'Validators'),
                          Tab(text: 'My Stakes'),
                          Tab(text: 'Rewards'),
                          Tab(text: 'History'),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ];
        },
        body: TabBarView(
          controller: _tabController,
          children: [
            // Tab 1: Validators List
            const ValidatorList(),

            // Tab 2: My Stakes (Positions)
            _MyStakesTab(positionsAsync: positionsAsync),

            // Tab 3: Rewards Chart
            const SingleChildScrollView(
              padding: EdgeInsets.all(16),
              child: RewardsChart(),
            ),

            // Tab 4: Staking History
            _HistoryTab(historyAsync: historyAsync),
          ],
        ),
      ),
    );
  }
}

class _MyStakesTab extends StatelessWidget {

  const _MyStakesTab({required this.positionsAsync});
  final AsyncValue<List<StakingPosition>> positionsAsync;

  @override
  Widget build(BuildContext context) {
    return positionsAsync.when(
      data: (positions) {
        if (positions.isEmpty) {
          return EmptyState(
            icon: Icons.account_balance_wallet_outlined,
            title: 'No Active Staking Positions',
            subtitle: 'You currently have no staked VRD tokens. Stake with a validator to earn daily rewards.',
            actionLabel: 'Browse Validators',
            onAction: () {
              // Switch to validators tab
              DefaultTabController.maybeOf(context)?.animateTo(0);
            },
          );
        }

        return ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: positions.length,
          separatorBuilder: (context, index) => const SizedBox(height: 12),
          itemBuilder: (context, index) {
            final position = positions[index];
            return StakingPositionCard(position: position);
          },
        );
      },
      loading: () => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: 3,
        separatorBuilder: (context, index) => const SizedBox(height: 12),
        itemBuilder: (context, index) => const ShimmerPlaceholder(height: 160),
      ),
      error: (err, stack) => EmptyState(
        icon: Icons.error_outline_rounded,
        title: 'Error Loading Positions',
        subtitle: err.toString(),
      ),
    );
  }
}

class _HistoryTab extends StatelessWidget {

  const _HistoryTab({required this.historyAsync});
  final AsyncValue<List<StakingHistoryItem>> historyAsync;

  IconData _getTypeIcon(StakingHistoryType type) {
    switch (type) {
      case StakingHistoryType.stake:
        return Icons.add_circle_outline_rounded;
      case StakingHistoryType.unstake:
        return Icons.remove_circle_outline_rounded;
      case StakingHistoryType.claimReward:
        return Icons.card_giftcard_rounded;
    }
  }

  Color _getTypeColor(BuildContext context, StakingHistoryType type) {
    final theme = Theme.of(context);
    switch (type) {
      case StakingHistoryType.stake:
        return theme.colorScheme.primary;
      case StakingHistoryType.unstake:
        return const Color(0xFFFF9800);
      case StakingHistoryType.claimReward:
        return const Color(0xFF00FF88);
    }
  }

  String _getTypeLabel(StakingHistoryType type) {
    switch (type) {
      case StakingHistoryType.stake:
        return 'Staked';
      case StakingHistoryType.unstake:
        return 'Unstaked';
      case StakingHistoryType.claimReward:
        return 'Claimed Rewards';
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return historyAsync.when(
      data: (items) {
        if (items.isEmpty) {
          return const EmptyState(
            icon: Icons.history_rounded,
            title: 'No Staking History',
            subtitle: 'Your staking transaction history will appear here.',
          );
        }

        return ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: items.length,
          separatorBuilder: (context, index) => const SizedBox(height: 10),
          itemBuilder: (context, index) {
            final item = items[index];
            final typeColor = _getTypeColor(context, item.type);

            return VerdisCard(
              padding: const EdgeInsets.all(14),
              child: Row(
                children: [
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: typeColor.withOpacity(0.15),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(_getTypeIcon(item.type), color: typeColor, size: 20),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _getTypeLabel(item.type),
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${item.validatorName} • ${DateFormat('MMM d, yyyy HH:mm').format(item.timestamp)}',
                          style: theme.textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '${item.type == StakingHistoryType.unstake ? '-' : '+'}${item.amount} VRD',
                        style: theme.textTheme.titleMedium?.copyWith(
                          color: typeColor,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primary.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          item.status.toUpperCase(),
                          style: TextStyle(
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                            color: theme.colorScheme.primary,
                          ),
                        ),
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
        separatorBuilder: (context, index) => const SizedBox(height: 10),
        itemBuilder: (context, index) => const ShimmerPlaceholder(height: 64),
      ),
      error: (err, stack) => EmptyState(
        icon: Icons.error_outline_rounded,
        title: 'Error Loading History',
        subtitle: err.toString(),
      ),
    );
  }
}
