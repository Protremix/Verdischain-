import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/wallet_service.dart';
import '../services/auth_service.dart';
import '../widgets/balance_card.dart';
import 'send_screen.dart';
import 'receive_screen.dart';
import 'staking_screen.dart';
import 'dex_screen.dart';
import 'eco_screen.dart';
import 'settings_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _currentBottomNavIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final wallet = Provider.of<WalletService>(context, listen: false);
      wallet.fetchBalance();
    });
  }

  void _onInteraction() {
    final authService = Provider.of<AuthService>(context, listen: false);
    authService.resetInactivityTimer();
  }

  @override
  Widget build(BuildContext context) {
    return Listener(
      onPointerDown: (_) => _onInteraction(),
      child: Scaffold(
        backgroundColor: const Color(0xFF040806),
        body: _buildCurrentTabBody(),
        bottomNavigationBar: BottomNavigationBar(
          currentIndex: _currentBottomNavIndex,
          onTap: (index) {
            setState(() {
              _currentBottomNavIndex = index;
            });
          },
          backgroundColor: const Color(0xFF0D1410),
          selectedItemColor: const Color(0xFF16a34a),
          unselectedItemColor: const Color(0xFF94a3b8),
          type: BottomNavigationBarType.fixed,
          selectedFontSize: 11,
          unselectedFontSize: 11,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.account_balance_wallet_outlined),
              activeIcon: Icon(Icons.account_balance_wallet),
              label: 'Home',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.swap_horiz_outlined),
              activeIcon: Icon(Icons.swap_horiz),
              label: 'DEX',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.eco_outlined),
              activeIcon: Icon(Icons.eco),
              label: 'Eco',
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

  Widget _buildCurrentTabBody() {
    switch (_currentBottomNavIndex) {
      case 0:
        return _buildHomeTab();
      case 1:
        return const DexScreen();
      case 2:
        return const EcoScreen();
      case 3:
        return const SettingsScreen();
      default:
        return _buildHomeTab();
    }
  }

  Widget _buildHomeTab() {
    return Consumer<WalletService>(
      builder: (context, wallet, child) {
        final activeAcc = wallet.activeAccount;

        return SafeArea(
          child: RefreshIndicator(
            color: const Color(0xFF16a34a),
            backgroundColor: const Color(0xFF0D1410),
            onRefresh: () async {
              await wallet.fetchBalance();
            },
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Verdis Wallet',
                            style: TextStyle(
                              color: Color(0xFF94a3b8),
                              fontSize: 12,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          Text(
                            activeAcc?.name ?? 'Main Wallet',
                            style: const TextStyle(
                              color: Color(0xFFFFFFFF),
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      IconButton(
                        icon: const Icon(Icons.shield_outlined, color: Color(0xFF16a34a)),
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => const StakingScreen()),
                          );
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  BalanceCard(
                    accountName: activeAcc?.name ?? 'Main Wallet',
                    address: activeAcc?.address ?? '',
                    vrdxBalance: wallet.vrdxBalance,
                    usdBalance: wallet.usdBalance,
                    onRefresh: () => wallet.fetchBalance(),
                  ),
                  const SizedBox(height: 24),
                  _buildQuickActionGrid(),
                  const SizedBox(height: 28),
                  _buildEcoStatsCard(wallet),
                  const SizedBox(height: 28),
                  _buildRecentTransactionsSection(wallet),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildQuickActionGrid() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        _buildActionButton(
          icon: Icons.call_made,
          label: 'Send',
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const SendScreen()),
            );
          },
        ),
        _buildActionButton(
          icon: Icons.south_west,
          label: 'Receive',
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const ReceiveScreen()),
            );
          },
        ),
        _buildActionButton(
          icon: Icons.lock_clock_outlined,
          label: 'Stake',
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const StakingScreen()),
            );
          },
        ),
        _buildActionButton(
          icon: Icons.swap_calls,
          label: 'Swap',
          onTap: () {
            setState(() {
              _currentBottomNavIndex = 1;
            });
          },
        ),
      ],
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return Column(
      children: [
        InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Container(
            width: 54,
            height: 54,
            decoration: BoxDecoration(
              color: const Color(0xFF0D1410),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFF2E2E34)),
            ),
            child: Icon(icon, color: const Color(0xFF16a34a), size: 24),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: const TextStyle(
            color: Color(0xFFFFFFFF),
            fontSize: 12,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildEcoStatsCard(WalletService wallet) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0D1410),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2E2E34)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFF16a34a).withOpacity(0.12),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.eco, color: Color(0xFF16a34a), size: 20),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Eco Credits & Impact',
                    style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 13, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${wallet.carbonCredits.toStringAsFixed(1)} VERD-ECO • Green Score: ${wallet.greenScore}/100',
                    style: const TextStyle(color: Color(0xFF94a3b8), fontSize: 12),
                  ),
                ],
              ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.chevron_right, color: Color(0xFF94a3b8)),
            onPressed: () {
              setState(() {
                _currentBottomNavIndex = 2;
              });
            },
          ),
        ],
      ),
    );
  }

  Widget _buildRecentTransactionsSection(WalletService wallet) {
    final txs = wallet.recentTransactions;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Recent Transactions',
              style: TextStyle(
                color: Color(0xFFFFFFFF),
                fontSize: 15,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              '${txs.length} total',
              style: const TextStyle(color: Color(0xFF94a3b8), fontSize: 12),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (txs.isEmpty)
          Container(
            padding: const EdgeInsets.all(24),
            width: double.infinity,
            decoration: BoxDecoration(
              color: const Color(0xFF0D1410),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFF2E2E34)),
            ),
            child: const Center(
              child: Text(
                'No transactions recorded yet.',
                style: TextStyle(color: Color(0xFF94a3b8), fontSize: 13),
              ),
            ),
          )
        else
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: txs.length > 5 ? 5 : txs.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final tx = txs[index];
              final isSend = tx.txType.contains('Send') || tx.fromAddress == wallet.activeAccount?.address;
              final dateStr = DateFormat('MMM dd, HH:mm').format(
                DateTime.fromMillisecondsSinceEpoch(tx.timestamp),
              );

              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                decoration: BoxDecoration(
                  color: const Color(0xFF0D1410),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFF2E2E34)),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: isSend
                            ? const Color(0xFFEF4444).withOpacity(0.12)
                            : const Color(0xFF16a34a).withOpacity(0.12),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        isSend ? Icons.arrow_upward : Icons.arrow_downward,
                        color: isSend ? const Color(0xFFEF4444) : const Color(0xFF16a34a),
                        size: 16,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            tx.txType,
                            style: const TextStyle(
                              color: Color(0xFFFFFFFF),
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            dateStr,
                            style: const TextStyle(color: Color(0xFF94a3b8), fontSize: 11),
                          ),
                        ],
                      ),
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          '${isSend ? "-" : "+"}${tx.amount.toStringAsFixed(2)} VRDX',
                          style: TextStyle(
                            color: isSend ? const Color(0xFFFFFFFF) : const Color(0xFF16a34a),
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          tx.status,
                          style: const TextStyle(color: Color(0xFF16a34a), fontSize: 11),
                        ),
                      ],
                    ),
                  ],
                ),
              );
            },
          ),
      ],
    );
  }
}
