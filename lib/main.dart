import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/di/injection.dart';
import 'core/security/platform_security_service.dart';
import 'core/storage/hive_helper.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Set ErrorWidget GLOBALLY before runApp — catches ANY widget build failure
  // In release mode, default ErrorWidget is invisible (black screen)
  ErrorWidget.builder = (FlutterErrorDetails details) {
    return Material(
      color: const Color(0xFF1A0000),
      child: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Text(
            'RENDER ERROR: ${details.exception}\n${details.stack}',
            style: const TextStyle(color: Color(0xFFFF6B6B), fontSize: 12),
          ),
        ),
      ),
    );
  };

  // Catch ALL Flutter framework errors
  FlutterError.onError = (FlutterErrorDetails details) {
    debugPrint('FLUTTER ERROR: ${details.exception}');
    debugPrint('STACK: ${details.stack}');
    FlutterError.dumpErrorToConsole(details);
  };

  // Initialize Hive BEFORE runApp so the splash page can read onboarding state.
  // This prevents a race condition where the splash page tries to read Hive
  // before it's initialized, causing the app to show the welcome page
  // instead of the PIN lock screen for existing wallets.
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

  // NOW run the app — Hive is ready, splash page will work correctly.
  runApp(
    ProviderScope(
      overrides: [],
      child: const VerdisWalletApp(),
    ),
  );

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
