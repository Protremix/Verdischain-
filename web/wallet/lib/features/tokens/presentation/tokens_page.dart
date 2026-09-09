import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../domain/token_repository.dart';
import 'import_token_page.dart';
import 'token_detail_page.dart';
import 'tokens_providers.dart';
import 'widgets/token_card.dart';

/// Main Tokens Feature Screen with TabBar, Search, Sort & Import
class TokensPage extends ConsumerStatefulWidget {
  const TokensPage({super.key});

  @override
  ConsumerState<TokensPage> createState() => _TokensPageState();
}

class _TokensPageState extends ConsumerState<TokensPage>
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
    final selectedSort = ref.watch(tokenSortOptionProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tokens'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh balances',
            onPressed: () => ref.invalidate(tokenListProvider),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: theme.colorScheme.primary,
          labelColor: theme.colorScheme.primary,
          unselectedLabelColor: theme.colorScheme.onSurfaceVariant,
          tabs: const [
            Tab(text: 'My Tokens'),
            Tab(text: 'Custom Tokens'),
            Tab(text: 'Import'),
          ],
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Search and Sort Bar (shown for My Tokens and Custom Tokens tabs)
            AnimatedBuilder(
              animation: _tabController,
              builder: (context, _) {
                if (_tabController.index == 2) {
                  return const SizedBox.shrink(); // Hide search/sort on Import tab
                }

                return Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Row(
                    children: [
                      // Search Bar
                      Expanded(
                        child: TextField(
                          controller: _searchController,
                          onChanged: (val) {
                            ref.read(tokenSearchQueryProvider.notifier).state = val;
                          },
                          decoration: InputDecoration(
                            hintText: 'Search token name, symbol or address...',
                            prefixIcon: const Icon(Icons.search, size: 20),
                            suffixIcon: _searchController.text.isNotEmpty
                                ? IconButton(
                                    icon: const Icon(Icons.clear, size: 18),
                                    onPressed: () {
                                      _searchController.clear();
                                      ref
                                          .read(tokenSearchQueryProvider.notifier)
                                          .state = '';
                                    },
                                  )
                                : null,
                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 12,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),

                      // Sort Dropdown Button
                      PopupMenuButton<TokenSortOption>(
                        initialValue: selectedSort,
                        tooltip: 'Sort tokens',
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
                            Icons.sort,
                            color: theme.colorScheme.primary,
                            size: 20,
                          ),
                        ),
                        onSelected: (option) {
                          ref.read(tokenSortOptionProvider.notifier).state = option;
                        },
                        itemBuilder: (context) => [
                          const PopupMenuItem(
                            value: TokenSortOption.valueDesc,
                            child: Row(
                              children: [
                                Icon(Icons.arrow_downward, size: 18),
                                SizedBox(width: 8),
                                Text('Highest Value'),
                              ],
                            ),
                          ),
                          const PopupMenuItem(
                            value: TokenSortOption.valueAsc,
                            child: Row(
                              children: [
                                Icon(Icons.arrow_upward, size: 18),
                                SizedBox(width: 8),
                                Text('Lowest Value'),
                              ],
                            ),
                          ),
                          const PopupMenuItem(
                            value: TokenSortOption.changeDesc,
                            child: Row(
                              children: [
                                Icon(Icons.show_chart, size: 18),
                                SizedBox(width: 8),
                                Text('Top Gainers (24h)'),
                              ],
                            ),
                          ),
                          const PopupMenuItem(
                            value: TokenSortOption.nameAsc,
                            child: Row(
                              children: [
                                Icon(Icons.sort_by_alpha, size: 18),
                                SizedBox(width: 8),
                                Text('Name (A-Z)'),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),

            // Tab Views
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  // Tab 1: My Tokens List
                  _buildMyTokensList(context),

                  // Tab 2: Custom Tokens List
                  _buildCustomTokensList(context),

                  // Tab 3: Import Token Page
                  const ImportTokenPage(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMyTokensList(BuildContext context) {
    final filteredAsync = ref.watch(filteredTokensProvider);

    return filteredAsync.when(
      data: (tokens) {
        if (tokens.isEmpty) {
          return EmptyState(
            icon: Icons.token_outlined,
            title: 'No Tokens Found',
            subtitle: 'Try adjusting your search filter or import a custom token.',
            actionLabel: 'Import Token',
            onAction: () => _tabController.animateTo(2),
          );
        }

        // Calculate portfolio tokens total value
        final totalValue = tokens.fold<double>(
          0.0,
          (sum, token) => sum + token.usdValue,
        );

        return RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(tokenListProvider);
          },
          child: ListView.separated(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            itemCount: tokens.length + 1,
            separatorBuilder: (_, __) => const SizedBox(height: 10),
            itemBuilder: (context, index) {
              if (index == 0) {
                // Header summarizing token assets
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8.0),
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: Theme.of(context).colorScheme.outline,
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Total Tokens Value',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '\$${totalValue.toStringAsFixed(2)}',
                              style: Theme.of(context)
                                  .textTheme
                                  .headlineMedium
                                  ?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: Theme.of(context).colorScheme.primary,
                                  ),
                            ),
                          ],
                        ),
                        Chip(
                          avatar: const Icon(Icons.stars, size: 16),
                          label: Text('${tokens.length} Assets'),
                        ),
                      ],
                    ),
                  ),
                );
              }

              final token = tokens[index - 1];
              return TokenCard(
                token: token,
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => TokenDetailPage(tokenId: token.id),
                    ),
                  );
                },
                onTransfer: () => _openTransferDialog(context, token),
              );
            },
          ),
        );
      },
      loading: () => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: 5,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (_, __) => const ShimmerPlaceholder(height: 72),
      ),
      error: (err, stack) => EmptyState(
        icon: Icons.error_outline,
        title: 'Error Loading Tokens',
        subtitle: err.toString(),
        actionLabel: 'Retry',
        onAction: () => ref.invalidate(tokenListProvider),
      ),
    );
  }

  Widget _buildCustomTokensList(BuildContext context) {
    final customAsync = ref.watch(customTokensProvider);

    return customAsync.when(
      data: (customTokens) {
        if (customTokens.isEmpty) {
          return EmptyState(
            icon: Icons.add_circle_outline,
            title: 'No Custom Tokens',
            subtitle:
                'Import custom tokens by token ID or contract address to manage them here.',
            actionLabel: 'Import Custom Token',
            onAction: () => _tabController.animateTo(2),
          );
        }

        return ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: customTokens.length,
          separatorBuilder: (_, __) => const SizedBox(height: 10),
          itemBuilder: (context, index) {
            final token = customTokens[index];
            return TokenCard(
              token: token,
              onTap: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => TokenDetailPage(tokenId: token.id),
                  ),
                );
              },
              onTransfer: () => _openTransferDialog(context, token),
            );
          },
        );
      },
      loading: () => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: 3,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (_, __) => const ShimmerPlaceholder(height: 72),
      ),
      error: (err, stack) => EmptyState(
        icon: Icons.error_outline,
        title: 'Error',
        subtitle: err.toString(),
      ),
    );
  }

  void _openTransferDialog(BuildContext context, TokenModel token) {
    final recipientController = TextEditingController();
    final amountController = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (modalContext) {
        return Padding(
          padding: EdgeInsets.only(
            left: 20,
            right: 20,
            top: 24,
            bottom: MediaQuery.of(modalContext).viewInsets.bottom + 24,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Transfer ${token.symbol}',
                    style: Theme.of(modalContext).textTheme.headlineSmall,
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.of(modalContext).pop(),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              TextField(
                controller: recipientController,
                decoration: const InputDecoration(
                  labelText: 'Recipient Address',
                  hintText: 'Enter 0x... or Verdis address',
                  prefixIcon: Icon(Icons.person_outline),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: amountController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: InputDecoration(
                  labelText: 'Amount',
                  hintText: '0.00',
                  suffixText: token.symbol,
                  prefixIcon: const Icon(Icons.account_balance_wallet_outlined),
                ),
              ),
              const SizedBox(height: 24),
              VerdisButton(
                label: 'Send ${token.symbol}',
                icon: Icons.send_rounded,
                onPressed: () async {
                  final recipient = recipientController.text.trim();
                  final amount = double.tryParse(amountController.text.trim()) ?? 0.0;

                  if (recipient.isEmpty || amount <= 0) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Please enter valid address and amount.')),
                    );
                    return;
                  }

                  Navigator.of(modalContext).pop();

                  // Submit transfer
                  final repo = ref.read(tokenRepositoryProvider);
                  final sender = ref.read(userWalletAddressProvider);

                  final txHash = await repo.transferToken(
                    tokenId: token.id,
                    recipient: recipient,
                    amount: amount,
                    senderAddress: sender,
                  );

                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Transfer submitted! TX: ${txHash.substring(0, 10)}...'),
                        backgroundColor: Theme.of(context).colorScheme.primary,
                      ),
                    );
                  }
                },
              ),
            ],
          ),
        );
      },
    );
  }
}
