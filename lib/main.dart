import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/di/injection.dart';
import 'core/security/platform_security_service.dart';
import 'core/storage/hive_helper.dart';
import 'core/config/remote_config.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize dependency injection
  await configureDependencies();

  // Initialize Hive storage
  await HiveHelper.init();

  // Enable screenshot prevention (FLAG_SECURE) on Android
  await PlatformSecurityService.setSecureFlag(enabled: true);

  // Check for rooted device
  final isRooted = await PlatformSecurityService.isDeviceRooted();

  runApp(
    ProviderScope(
      overrides: [],
      child: const VerdisWalletApp(),
    ),
  );
}
