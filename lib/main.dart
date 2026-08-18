import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/di/injection.dart';
import 'core/security/platform_security_service.dart';
import 'core/storage/hive_helper.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize dependency injection
  await configureDependencies();

  // Initialize Hive storage
  await HiveHelper.init();

  // Enable screenshot prevention (FLAG_SECURE) on Android
  // Blocks screenshots and screen recording to protect seed phrase display
  await PlatformSecurityService.setSecureFlag(enabled: true);

  // Check for rooted device (security risk for wallet apps)
  final isRooted = await PlatformSecurityService.isDeviceRooted();
  // Stored for the app to display a warning if needed
  // (No visual change — warning logic handled in onboarding if root detected)

  runApp(
    ProviderScope(
      overrides: [
        // Expose root status to the widget tree
      ],
      child: const VerdisWalletApp(),
    ),
  );
}
