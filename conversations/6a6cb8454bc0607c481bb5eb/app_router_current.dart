Warning: Permanently added '91.98.160.145' (ED25519) to the list of known hosts.
     1	import 'package:go_router/go_router.dart';
     2	import 'package:flutter_riverpod/flutter_riverpod.dart';
     3	import '../../features/onboarding/presentation/splash_page.dart';
     4	import '../../features/onboarding/presentation/welcome_page.dart';
     5	import '../../features/onboarding/presentation/create_wallet_page.dart';
     6	import '../../features/onboarding/presentation/import_wallet_page.dart';
     7	import '../../features/onboarding/presentation/backup_phrase_page.dart';
     8	import '../../features/onboarding/presentation/verify_phrase_page.dart';
     9	import '../../features/onboarding/presentation/biometric_setup_page.dart';
    10	import '../../features/onboarding/presentation/pin_setup_page.dart';
    11	import '../../features/onboarding/presentation/security_notice_page.dart';
    12	import '../../features/onboarding/presentation/email_recovery_page.dart';
    13	import '../../features/home/presentation/home_page.dart';
    14	import '../../features/transactions/presentation/send_page.dart';
    15	import '../../features/transactions/presentation/receive_page.dart';
    16	import '../../features/transactions/presentation/transactions_page.dart';
    17	import '../../features/tokens/presentation/tokens_page.dart';
    18	import '../../features/tokens/presentation/import_token_page.dart';
    19	import '../../features/nft/presentation/nft_page.dart';
    20	import '../../features/staking/presentation/staking_page.dart';
    21	import '../../features/staking/presentation/staking_info_page.dart';
    22	import '../../features/dex/presentation/swap_page.dart';
    23	import '../../features/dex/presentation/liquidity_page.dart';
    24	import '../../features/dex/presentation/pools_page.dart';
    25	import '../../features/explorer/presentation/explorer_page.dart';
    26	import '../../features/settings/presentation/settings_page.dart';
    27	import '../../features/settings/presentation/account_settings_page.dart';
    28	import '../../features/settings/presentation/security_settings_page.dart';
    29	import '../../features/settings/presentation/network_settings_page.dart';
    30	import '../../features/settings/presentation/about_page.dart';
    31	
    32	final appRouterProvider = Provider<GoRouter>((ref) {
    33	  return GoRouter(
    34	    initialLocation: '/splash',
    35	    routes: [
    36	      GoRoute(path: '/splash', builder: (c, s) => const SplashPage()),
    37	      GoRoute(
    38	        path: '/security-notice',
    39	        name: 'SecurityNotice',
    40	        builder: (context, state) => const SecurityNoticePage(),
    41	      ),
    42	      GoRoute(path: '/welcome', builder: (c, s) => const WelcomePage()),
    43	      GoRoute(path: '/create-wallet', builder: (c, s) => const CreateWalletPage()),
    44	      GoRoute(path: '/import-wallet', builder: (c, s) => const ImportWalletPage()),
    45	      GoRoute(path: '/email-recovery', builder: (c, s) => const EmailRecoveryPage()),
    46	      GoRoute(path: '/backup-phrase', builder: (c, s) => const BackupPhrasePage()),
    47	      GoRoute(path: '/verify-phrase', builder: (c, s) => const VerifyPhrasePage()),
    48	      GoRoute(path: '/biometric-setup', builder: (c, s) => const BiometricSetupPage()),
    49	      GoRoute(path: '/pin-setup', builder: (c, s) => const PinSetupPage()),
    50	      GoRoute(path: '/home', builder: (c, s) => const HomePage()),
    51	      GoRoute(path: '/send', builder: (c, s) => const SendPage()),
    52	      GoRoute(path: '/receive', builder: (c, s) => const ReceivePage()),
    53	      GoRoute(path: '/tokens', builder: (c, s) => const TokensPage()),
    54	      GoRoute(path: '/tokens/import', builder: (c, s) => const ImportTokenPage()),
    55	      GoRoute(path: '/nft', builder: (c, s) => const NftPage()),
    56	      GoRoute(path: '/transactions', builder: (c, s) => const TransactionsPage()),
    57	      GoRoute(path: '/staking', builder: (c, s) => const StakingPage()),
    58	      GoRoute(path: '/staking/info', builder: (c, s) => const StakingInfoPage()),
    59	      GoRoute(path: '/dex', builder: (c, s) => const SwapPage()),
    60	      GoRoute(path: '/dex/swap', builder: (c, s) => const SwapPage()),
    61	      GoRoute(path: '/dex/liquidity', builder: (c, s) => const LiquidityPage()),
    62	      GoRoute(path: '/dex/pools', builder: (c, s) => const PoolsPage()),
    63	      GoRoute(path: '/explorer', builder: (c, s) => const ExplorerPage()),
    64	      GoRoute(path: '/settings', builder: (c, s) => const SettingsPage()),
    65	      GoRoute(path: '/settings/account', builder: (c, s) => const AccountSettingsPage()),
    66	      GoRoute(path: '/settings/security', builder: (c, s) => const SecuritySettingsPage()),
    67	      GoRoute(path: '/settings/network', builder: (c, s) => const NetworkSettingsPage()),
    68	      GoRoute(path: '/settings/about', builder: (c, s) => const AboutPage()),
    69	    ],
    70	  );
    71	});
