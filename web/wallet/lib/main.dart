import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/di/injection.dart';
import 'core/storage/hive_helper.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize dependency injection
  await configureDependencies();

  // Initialize Hive storage
  await HiveHelper.init();

  runApp(
    const ProviderScope(
      child: VerdisWalletApp(),
    ),
  );
}
