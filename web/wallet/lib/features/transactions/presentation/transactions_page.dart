import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'send_page.dart';
import 'transaction_detail_page.dart';
import 'transactions_providers.dart';
import 'widgets/tx_item.dart';

/// Transactions Page listing history with category filters, pull-to-refresh & infinite scroll
class TransactionsPage extends ConsumerStatefulWidget {
  const TransactionsPage({super.key});

  @override
  ConsumerState<TransactionsPage> createState() => _TransactionsPageState();
}

class _TransactionsPageState extends ConsumerState<TransactionsPage> {
  final ScrollController _scrollController = ScrollController();

  final List<String> _filters = ['All', 'Send', 'Receive', 'Swap', 'Stake'];

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      ref.read(transactionHistoryProvider.notifier).loadMore();
    }
  }

  Future<void> _onRefresh() async {
    await ref
        .read(transactionHistoryProvider.notifier)
        .fetchHistory(isRefresh: true);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final historyAsync = ref.watch(transactionHistoryProvider);
    final selectedFilter = ref.watch(selectedFilterProvider);
    final userAddress = ref.watch(userWalletAddressProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Transactions'),
        centerTitle: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.send_rounded),
            tooltip: 'Send VRDX',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const SendPage()),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Filter Chips Horizontal Row
          SizedBox(
            height: 52,
            child: ListView.separated(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              scrollDirection: Axis.horizontal,
              itemCount: _filters.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (context, index) {
                final filter = _filters[index];
                final isSelected = filter == selectedFilter;

                return ChoiceChip(
                  label: Text(filter),
                  selected: isSelected,
                  onSelected: (bool selected) {
                    if (selected) {
                      ref.read(selectedFilterProvider.notifier).state = filter;
                    }
                  },
                  selectedColor: theme.colorScheme.primary,
                  labelStyle: TextStyle(
                    color: isSelected
                        ? Colors.black
                        : theme.colorScheme.onSurface,
                    fontWeight:
                        isSelected ? FontWeight.bold : FontWeight.normal,
                  ),
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                );
              },
            ),
          ),
          const Divider(height: 1),

          // History List
          Expanded(
            child: RefreshIndicator(
              onRefresh: _onRefresh,
              color: theme.colorScheme.primary,
              child: historyAsync.when(
                data: (transactions) {
                  if (transactions.isEmpty) {
                    return ListView(
                      physics: const AlwaysScrollableScrollPhysics(),
                      children: [
                        const SizedBox(height: 80),
                        EmptyState(
                          icon: Icons.receipt_long_rounded,
                          title: 'No Transactions Found',
                          subtitle:
                              'No $selectedFilter transactions record available on network.',
                          actionLabel: 'Send VRDX',
                          onAction: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                  builder: (context) => const SendPage(),),
                            );
                          },
                        ),
                      ],
                    );
                  }

                  return ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 12,),
                    physics: const AlwaysScrollableScrollPhysics(),
                    itemCount: transactions.length + 1,
                    itemBuilder: (context, index) {
                      if (index == transactions.length) {
                        final notifier =
                            ref.read(transactionHistoryProvider.notifier);
                        if (notifier.hasMore) {
                          return const Padding(
                            padding: EdgeInsets.all(16.0),
                            child: Center(
                              child: SizedBox(
                                width: 24,
                                height: 24,
                                child: CircularProgressIndicator(
                                    strokeWidth: 2.5,),
                              ),
                            ),
                          );
                        } else {
                          return Padding(
                            padding: const EdgeInsets.symmetric(vertical: 24),
                            child: Center(
                              child: Text(
                                'End of transaction history',
                                style: theme.textTheme.bodySmall?.copyWith(
                                  color: theme.colorScheme.onSurfaceVariant,
                                ),
                              ),
                            ),
                          );
                        }
                      }

                      final tx = transactions[index];
                      return TxItem(
                        transaction: tx,
                        currentUserAddress: userAddress,
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) =>
                                  TransactionDetailPage(transaction: tx),
                            ),
                          );
                        },
                      );
                    },
                  );
                },
                loading: () => ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: 6,
                  itemBuilder: (_, __) => const Padding(
                    padding: EdgeInsets.only(bottom: 12),
                    child: ShimmerPlaceholder(height: 68, borderRadius: 14),
                  ),
                ),
                error: (error, stack) => ListView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  children: [
                    const SizedBox(height: 80),
                    EmptyState(
                      icon: Icons.error_outline_rounded,
                      title: 'Failed to Load History',
                      subtitle: error.toString(),
                      actionLabel: 'Retry',
                      onAction: _onRefresh,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
