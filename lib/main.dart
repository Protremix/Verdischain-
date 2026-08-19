import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/di/injection.dart';
import 'core/security/platform_security_service.dart';
import 'core/storage/hive_helper.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize everything — if any step fails, still run the app
  try {
    await configureDependencies();
  } catch (e) {
    debugPrint('⚠️ configureDependencies failed: $e');
  }

  try {
    await HiveHelper.init();
  } catch (e) {
    debugPrint('⚠️ HiveHelper.init failed: $e');
  }

  try {
    await PlatformSecurityService.setSecureFlag(enabled: true);
  } catch (e) {
    debugPrint('⚠️ setSecureFlag failed: $e');
  }

  try {
    await PlatformSecurityService.isDeviceRooted();
  } catch (e) {
    debugPrint('⚠️ isDeviceRooted failed: $e');
  }

  runApp(
    ProviderScope(
      overrides: [],
      child: const VerdisWalletApp(),
    ),
  );
}
