import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/theme/app_theme.dart';
import 'core/router/app_router.dart';
import 'core/theme/theme_provider.dart';
import 'core/config/remote_config.dart';

class VerdisWalletApp extends ConsumerStatefulWidget {
  const VerdisWalletApp({super.key});

  @override
  ConsumerState<VerdisWalletApp> createState() => _VerdisWalletAppState();
}

class _VerdisWalletAppState extends ConsumerState<VerdisWalletApp> {
  @override
  void initState() {
    super.initState();
    // Fetch remote config on startup — non-blocking, silent fail
    Future.microtask(() {
      ref.read(remoteConfigProvider.notifier).fetch();
    });
  }

  @override
  Widget build(BuildContext context) {
    final router = ref.watch(appRouterProvider);
    final themeMode = ref.watch(themeModeProvider);
    final config = ref.watch(remoteConfigProvider);

    // Show maintenance screen if maintenance mode is on
    if (config.maintenanceMode) {
      return MaterialApp(
        title: 'Verdis Wallet',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.darkTheme,
        home: Scaffold(
          backgroundColor: const Color(0xFF0A0E0A),
          body: Center(
            child: Padding(
              padding: const EdgeInsets.all(32.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.build_circle,
                    size: 64,
                    color: Color(0xFF00FF88),
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    'Maintenance Mode',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFFE8F0E8),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    config.maintenanceMessage.isNotEmpty
                        ? config.maintenanceMessage
                        : 'Verdis Wallet is undergoing maintenance. Please check back shortly.',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      color: Color(0xFF8B9D8B),
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    }

    return MaterialApp.router(
      title: 'Verdis Wallet',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: router,
      builder: (context, child) {
        // Show errors even in release mode (default ErrorWidget is invisible)
        ErrorWidget.builder = (FlutterErrorDetails details) {
          return Material(
            color: const Color(0xFF1A0000),
            child: SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Text(
                  'RENDER ERROR:

' + details.exception.toString() + '

' + details.stack.toString(),
                  style: const TextStyle(color: Color(0xFFFF6B6B), fontSize: 12),
                ),
              ),
            ),
          );
        };
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(
            textScaler: const TextScaler.linear(1.0),
          ),
          child: child!,
        );
      },
    );
  }
}
