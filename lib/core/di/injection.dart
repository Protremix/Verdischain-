import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../network/rpc_client.dart';
import '../security/secure_storage.dart';
import '../security/biometric_auth.dart';

/// Dependency injection container
/// Configures all providers and singletons
final providers = <Provider<dynamic>>[
  rpcClientProvider,
  secureStorageProvider,
  biometricAuthProvider,
];

/// Initialize all dependencies before app starts
Future<void> configureDependencies() async {
  // Any async initialization goes here
  // Hive boxes, Isar databases, etc.
}
