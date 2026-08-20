import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:verdis_wallet/core/router/route_names.dart';
import 'package:verdis_wallet/core/security/persistent_storage.dart';
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
      // Check 1: PersistentStorage (plain file — always reliable)
      // Timeout: if path_provider hangs, skip to welcome page
      final prefsOnboarding = await PersistentStorage.isOnboardingComplete()
          .timeout(const Duration(seconds: 3));
      final prefsAddress = await PersistentStorage.getWalletAddress()
          .timeout(const Duration(seconds: 3));
      debugPrint('🔵 Splash: prefsOnboarding=$prefsOnboarding, prefsAddress=$prefsAddress');

      if (prefsOnboarding && prefsAddress != null && prefsAddress.isNotEmpty) {
        debugPrint('🔵 Splash: Wallet found via PersistentStorage → lock screen');
        if (!mounted) return;
        context.go(RouteNames.lock);
        return;
      }

      // Check 2: Repository (flutter_secure_storage fallback)
      final repository = ref.read(walletRepositoryProvider);
      final hasWallet = await repository.hasWallet()
          .timeout(const Duration(seconds: 3));
      debugPrint('🔵 Splash: repository.hasWallet()=$hasWallet');

      if (!mounted) return;
      if (hasWallet) {
        debugPrint('🔵 Splash: Wallet found via repository → lock screen');
        if (!mounted) return;
        context.go(RouteNames.lock);
      } else {
        debugPrint('🔵 Splash: No wallet found → welcome page');
        context.go(RouteNames.welcome);
      }
    } catch (e) {
      debugPrint('🔵 Splash: ERROR: $e → welcome page');
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
