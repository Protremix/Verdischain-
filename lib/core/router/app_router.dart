import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/onboarding/presentation/splash_page.dart';
import '../../features/onboarding/presentation/lock_screen_page.dart';
import '../../features/onboarding/presentation/welcome_page.dart';
import '../../features/onboarding/presentation/create_wallet_page.dart';
import '../../features/onboarding/presentation/import_wallet_page.dart';
import '../../features/onboarding/presentation/backup_phrase_page.dart';
import '../../features/onboarding/presentation/verify_phrase_page.dart';
import '../../features/onboarding/presentation/biometric_setup_page.dart';
import '../../features/onboarding/presentation/pin_setup_page.dart';
import '../../features/onboarding/presentation/security_notice_page.dart';
import '../../features/onboarding/presentation/email_recovery_page.dart';
import '../../features/home/presentation/home_page.dart';
import '../../features/transactions/presentation/send_page.dart';
import '../../features/transactions/presentation/receive_page.dart';
import '../../features/transactions/presentation/transactions_page.dart';
import '../../features/tokens/presentation/tokens_page.dart';
import '../../features/tokens/presentation/import_token_page.dart';
import '../../features/nft/presentation/nft_page.dart';
import '../../features/staking/presentation/staking_page.dart';
import '../../features/staking/presentation/staking_info_page.dart';
import '../../features/dex/presentation/swap_page.dart';
import '../../features/dex/presentation/liquidity_page.dart';
import '../../features/dex/presentation/pools_page.dart';
import '../../features/explorer/presentation/explorer_page.dart';
import '../../features/settings/presentation/settings_page.dart';
import '../../features/settings/presentation/account_settings_page.dart';
import '../../features/settings/presentation/security_settings_page.dart';
import '../../features/settings/presentation/network_settings_page.dart';
import '../../features/settings/presentation/about_page.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(path: '/splash', builder: (c, s) => const SplashPage()),
      GoRoute(path: "/lock", builder: (c, s) => const LockScreenPage()),
      GoRoute(
        path: '/security-notice',
        name: 'SecurityNotice',
        builder: (context, state) => const SecurityNoticePage(),
      ),
      GoRoute(path: '/welcome', builder: (c, s) => const WelcomePage()),
      GoRoute(path: '/create-wallet', builder: (c, s) => const CreateWalletPage()),
      GoRoute(path: '/import-wallet', builder: (c, s) => const ImportWalletPage()),
      GoRoute(path: '/email-recovery', builder: (c, s) => const EmailRecoveryPage()),
      GoRoute(path: '/backup-phrase', builder: (c, s) => const BackupPhrasePage()),
      GoRoute(path: '/verify-phrase', builder: (c, s) => const VerifyPhrasePage()),
      GoRoute(path: '/biometric-setup', builder: (c, s) => const BiometricSetupPage()),
      GoRoute(path: '/pin-setup', builder: (c, s) => const PinSetupPage()),
      GoRoute(path: '/home', builder: (c, s) => const HomePage()),
      GoRoute(path: '/send', builder: (c, s) => const SendPage()),
      GoRoute(path: '/receive', builder: (c, s) => const ReceivePage()),
      GoRoute(path: '/tokens', builder: (c, s) => const TokensPage()),
      GoRoute(path: '/tokens/import', builder: (c, s) => const ImportTokenPage()),
      GoRoute(path: '/nft', builder: (c, s) => const NftPage()),
      GoRoute(path: '/transactions', builder: (c, s) => const TransactionsPage()),
      GoRoute(path: '/staking', builder: (c, s) => const StakingPage()),
      GoRoute(path: '/staking/info', builder: (c, s) => const StakingInfoPage()),
      GoRoute(path: '/dex', builder: (c, s) => const SwapPage()),
      GoRoute(path: '/dex/swap', builder: (c, s) => const SwapPage()),
      GoRoute(path: '/dex/liquidity', builder: (c, s) => const LiquidityPage()),
      GoRoute(path: '/dex/pools', builder: (c, s) => const PoolsPage()),
      GoRoute(path: '/explorer', builder: (c, s) => const ExplorerPage()),
      GoRoute(path: '/settings', builder: (c, s) => const SettingsPage()),
      GoRoute(path: '/settings/account', builder: (c, s) => const AccountSettingsPage()),
      GoRoute(path: '/settings/security', builder: (c, s) => const SecuritySettingsPage()),
      GoRoute(path: '/settings/network', builder: (c, s) => const NetworkSettingsPage()),
      GoRoute(path: '/settings/about', builder: (c, s) => const AboutPage()),
    ],
  );
});
