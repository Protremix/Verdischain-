import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'home_providers.dart';
import 'package:verdis_wallet/features/settings/presentation/settings_page.dart';
import 'portfolio_view.dart';

/// Main Dashboard Page with custom AppBar (Wallet Address + Network Status) and Bottom Navigation Bar.
class HomePage extends ConsumerWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final currentIndex = ref.watch(bottomNavIndexProvider);
    final walletAddress = ref.watch(selectedAddressProvider);
    final networkStatusAsync = ref.watch(networkStatusProvider);

    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 70,
        title: Row(
          children: [
            AddressChip(
              address: walletAddress,
              showCopy: true,
            ),
            const Spacer(),
            networkStatusAsync.when(
              data: (status) => NetworkStatusBadge(
                isConnected: status.isConnected,
                blockNumber: status.blockHeight,
              ),
              loading: () => const NetworkStatusBadge(isConnected: true),
              error: (_, __) => const NetworkStatusBadge(isConnected: false),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_none),
            tooltip: 'Notifications',
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('No new network notifications')),
              );
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: IndexedStack(
        index: currentIndex,
        children: [
          // Tab 0: Home Portfolio Dashboard
          const PortfolioView(),

          // Tab 1: Tokens View
          _buildPlaceholderTab(
            context,
            icon: Icons.toll,
            title: 'Token Assets',
            subtitle: 'View and manage all eco-tokens on the Verdis Network.',
          ),

          // Tab 2: DEX View
          _buildPlaceholderTab(
            context,
            icon: Icons.swap_horizontal_circle,
            title: 'Verdis DEX',
            subtitle: 'Decentralized exchange with automated yield pools.',
          ),

          // Tab 3: Staking View
          _buildPlaceholderTab(
            context,
            icon: Icons.energy_savings_leaf,
            title: 'Staking & Governance',
            subtitle: 'Stake VRDX with green validator nodes to earn rewards.',
          ),

          // Tab 4: Settings
          const SettingsPage(),
        ],
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          border: Border(
            top: BorderSide(
              color: theme.colorScheme.outline.withOpacity(0.5),
              width: 1,
            ),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: currentIndex,
          onTap: (index) {
            ref.read(bottomNavIndexProvider.notifier).state = index;
          },
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home_outlined),
              activeIcon: Icon(Icons.home),
              label: 'Home',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.account_balance_wallet_outlined),
              activeIcon: Icon(Icons.account_balance_wallet),
              label: 'Tokens',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.swap_horiz_outlined),
              activeIcon: Icon(Icons.swap_horiz),
              label: 'DEX',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.energy_savings_leaf_outlined),
              activeIcon: Icon(Icons.energy_savings_leaf),
              label: 'Staking',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.settings_outlined),
              activeIcon: Icon(Icons.settings),
              label: 'Settings',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPlaceholderTab(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
    return Center(
      child: EmptyState(
        icon: icon,
        title: title,
        subtitle: subtitle,
        actionLabel: 'Return to Home',
        onAction: () {},
      ),
    );
  }
}
