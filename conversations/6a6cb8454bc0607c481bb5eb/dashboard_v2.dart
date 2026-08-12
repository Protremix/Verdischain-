import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/wallet_service.dart';
import '../services/auth_service.dart';
import '../widgets/balance_card.dart';
import 'send_screen.dart';
import 'receive_screen.dart';
import 'staking_screen.dart';
import 'dex_screen.dart';
import 'eco_screen.dart';
import 'settings_screen.dart';

// ignore_for_file: use_build_context_synchronously

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen>
    with TickerProviderStateMixin {
  int _currentBottomNavIndex = 0;
  late AnimationController _gradientController;
  late Animation<double> _gradientAnim;
  late AnimationController _fadeController;
  late Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _gradientController = AnimationController(
      duration: const Duration(seconds: 8),
      vsync: this,
    );
    _gradientAnim = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _gradientController, curve: Curves.easeInOut),
    );
    _gradientController.repeat(reverse: true);

    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    _fadeAnim = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _fadeController, curve: Curves.easeOut),
    );
    _fadeController.forward();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final wallet = Provider.of<WalletService>(context, listen: false);
      wallet.fetchBalance();
    });
  }

  @override
  void dispose() {
    _gradientController.dispose();
    _fadeController.dispose();
    super.dispose();
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
        body: AnimatedBuilder(
          animation: _gradientAnim,
          builder: (context, _) {
            final t = _gradientAnim.value;
            return Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Color.lerp(const Color(0xFF040806), const Color(0xFF0a1410), t)!,
                    Color.lerp(const Color(0xFF0a1410), const Color(0xFF0D1410), t)!,
                    const Color(0xFF040806),
                  ],
                ),
              ),
              child: _buildCurrentTabBody(),
            );
          },
        ),
        bottomNavigationBar: Container(
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF0D1410), Color(0xFF040806)],
            ),
            border: Border(
              top: BorderSide(color: const Color(0xFF16a34a).withOpacity(0.1)),
            ),
          ),
          child: BottomNavigationBar(
            currentIndex: _currentBottomNavIndex,
            onTap: (index) {
              setState(() {
                _currentBottomNavIndex = index;
              });
            },
            backgroundColor: Colors.transparent,
            elevation: 0,
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
          child: FadeTransition(
            opacity: _fadeAnim,
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
                            Image.asset(
                              'assets/images/verdis-logo-white.png',
                              height: 32,
                              fit: BoxFit.contain,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              activeAcc?.name ?? 'Main Wallet',
                              style: const TextStyle(
                                color: Color(0xFF94a3b8),
                                fontSize: 13,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                        Container(
                          decoration: BoxDecoration(
                            color: const Color(0xFF16a34a).withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: const Color(0xFF16a34a).withOpacity(0.2),
                            ),
                          ),
                          child: IconButton(
                            icon: const Icon(Icons.shield_outlined, color: Color(0xFF16a34a)),
                            onPressed: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(builder: (_) => const StakingScreen()),
                              );
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
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
        GestureDetector(
          onTap: onTap,
          child: Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xFF0D1410), Color(0xFF152017)],
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.15)),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF16a34a).withOpacity(0.08),
                  blurRadius: 12,
                  offset: const Offset(0, 2),
                ),
              ],
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
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF0D1410), Color(0xFF152017)],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.15)),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF16a34a).withOpacity(0.05),
            blurRadius: 12,
            offset: const Offset(0, 2),
          ),
        ],
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
        const Text(
          'Recent Transactions',
          style: TextStyle(
            color: Color(0xFFFFFFFF),
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        if (txs.isEmpty)
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: const Color(0xFF0D1410),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFF2E2E34)),
            ),
            child: Center(
              child: Column(
                children: [
                  Icon(Icons.receipt_long_outlined, color: const Color(0xFF475569), size: 32),
                  const SizedBox(height: 12),
                  Text(
                    'No transactions yet',
                    style: TextStyle(color: const Color(0xFF94a3b8), fontSize: 13),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Receive VRDX to get started',
                    style: TextStyle(color: const Color(0xFF475569), fontSize: 12),
                  ),
                ],
              ),
            ),
          )
        else
          ...txs.take(5).map((tx) => _buildTransactionItem(tx)),
      ],
    );
  }

  Widget _buildTransactionItem(dynamic tx) {
    final isIncoming = tx.type == 'received';
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF0D1410), Color(0xFF152017)],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.08)),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: (isIncoming ? const Color(0xFF16a34a) : const Color(0xFF94a3b8))
                  .withOpacity(0.12),
              shape: BoxShape.circle,
            ),
            child: Icon(
              isIncoming ? Icons.south_west : Icons.call_made,
              color: isIncoming ? const Color(0xFF16a34a) : const Color(0xFF94a3b8),
              size: 18,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isIncoming ? 'Received' : 'Sent',
                  style: const TextStyle(
                    color: Color(0xFFFFFFFF),
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  tx.timestamp ?? '',
                  style: const TextStyle(color: Color(0xFF94a3b8), fontSize: 11),
                ),
              ],
            ),
          ),
          Text(
            '${isIncoming ? '+' : '-'}${tx.amount?.toStringAsFixed(4) ?? '0.0000'} VRDX',
            style: TextStyle(
              color: isIncoming ? const Color(0xFF16a34a) : const Color(0xFF94a3b8),
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
