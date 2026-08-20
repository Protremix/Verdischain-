import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/di/injection.dart';
import 'core/security/platform_security_service.dart';
import 'core/storage/hive_helper.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize everything with timeouts — if any step hangs (e.g., plugin
  // not registered on this platform), the app still starts and renders.
  // Each step has a 3-second timeout; failures are non-fatal.

  try {
    await configureDependencies().timeout(const Duration(seconds: 3));
  } catch (e) {
    debugPrint('⚠️ configureDependencies failed: $e');
  }

  try {
    await HiveHelper.init().timeout(const Duration(seconds: 3));
  } catch (e) {
    debugPrint('⚠️ HiveHelper.init failed: $e');
  }

  try {
    await PlatformSecurityService.setSecureFlag(enabled: true)
        .timeout(const Duration(seconds: 3));
  } catch (e) {
    debugPrint('⚠️ setSecureFlag failed: $e');
  }

  try {
    await PlatformSecurityService.isDeviceRooted()
        .timeout(const Duration(seconds: 3));
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
