import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:verdis_wallet/core/router/route_names.dart';
import '../domain/wallet_repository.dart';
import 'package:verdis_wallet/core/config/network_config.dart';

/// Animated splash page with Verdis V logo animation
class SplashPage extends ConsumerStatefulWidget {
  const SplashPage({super.key});

  @override
  ConsumerState<SplashPage> createState() => _SplashPageState();
}

class _SplashPageState extends ConsumerState<SplashPage> {
  @override
  void initState() {
    super.initState();
    _checkWalletAndNavigate();
  }

  Future<void> _checkWalletAndNavigate() async {
    await Future.delayed(const Duration(milliseconds: 2500));
    if (!mounted) return;

    try {
      final repository = ref.read(walletRepositoryProvider);
      final hasWallet = await repository.hasWallet();

      if (!mounted) return;
      if (hasWallet) {
        // Wallet exists — go to lock screen for PIN/biometric unlock
        if (!mounted) return;
        context.go(RouteNames.lock);
      } else {
        context.go(RouteNames.welcome);
      }
    } catch (e) {
      if (!mounted) return;
      context.go(RouteNames.welcome);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E0A),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Verdis Chain logo
            Image.asset(
              'assets/images/verdis-logo-white.png',
              width: 130,
              height: 130,
              fit: BoxFit.contain,
            ),
            const SizedBox(height: 32),

            // App Name
            Text(
              AppConstants.appName,
              style: theme.textTheme.displayMedium?.copyWith(
                color: const Color(0xFFE8F0E8),
                fontWeight: FontWeight.bold,
                letterSpacing: 1.2,
              ),
            ),
            const SizedBox(height: 8),

            Text(
              'Carbon-Negative Blockchain Wallet',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: const Color(0xFF8B9D8B),
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 48),

            // Loading Indicator
            const SizedBox(
              width: 28,
              height: 28,
              child: CircularProgressIndicator(
                strokeWidth: 2.5,
                valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF00FF88)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
