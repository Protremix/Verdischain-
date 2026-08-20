import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/di/injection.dart';
import 'core/security/platform_security_service.dart';
import 'core/storage/hive_helper.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Catch ALL Flutter framework errors — in release mode these are silently
  // swallowed and render as empty (black) widgets. We log them so we can debug.
  FlutterError.onError = (FlutterErrorDetails details) {
    debugPrint('FLUTTER ERROR: ${details.exception}');
    debugPrint('STACK: ${details.stack}');
    FlutterError.dumpErrorToConsole(details);
  };

  // CRITICAL: runApp() FIRST so the user sees UI immediately.
  // All initialization happens in the background while the splash screen is visible.
  runApp(
    ProviderScope(
      overrides: [],
      child: const VerdisWalletApp(),
    ),
  );

  // Background initialization — non-blocking, each step has a 3s timeout.
  // Failures are non-fatal; the app still works with reduced functionality.
  try {
    await configureDependencies().timeout(const Duration(seconds: 3));
  } catch (e) {
    debugPrint('configureDependencies failed: $e');
  }

  try {
    await HiveHelper.init().timeout(const Duration(seconds: 3));
  } catch (e) {
    debugPrint('HiveHelper.init failed: $e');
  }

  try {
    await PlatformSecurityService.setSecureFlag(enabled: true)
        .timeout(const Duration(seconds: 3));
  } catch (e) {
    debugPrint('setSecureFlag failed: $e');
  }

  try {
    await PlatformSecurityService.isDeviceRooted()
        .timeout(const Duration(seconds: 3));
  } catch (e) {
    debugPrint('isDeviceRooted failed: $e');
  }
}
