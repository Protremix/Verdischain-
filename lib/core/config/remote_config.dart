import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Remote configuration fetched from the server.
///
/// This allows us to toggle features, change network endpoints,
/// enable maintenance mode, and show messages — all without
/// pushing a new app version to the App Store / Google Play.
///
/// The app fetches this on startup and caches it.
/// If the server is unreachable, it falls back to defaults.

class RemoteConfig {
  final String version;
  final String minVersion;
  final bool maintenanceMode;
  final String maintenanceMessage;
  final Map<String, bool> features;
  final Map<String, String> network;
  final Map<String, String> messages;

  const RemoteConfig({
    this.version = '',
    this.minVersion = '2.1.0',
    this.maintenanceMode = false,
    this.maintenanceMessage = '',
    this.features = const {},
    this.network = const {},
    this.messages = const {},
  });

  bool isFeatureEnabled(String key) => features[key] ?? true;

  String? get rpcUrl => network['rpc_url'];
  String? get wsUrl => network['ws_url'];
  String? get explorerUrl => network['explorer_url'];
  String? get chainName => network['chain_name'];
  String? get welcomeMessage => messages['welcome'];
  String? get warningMessage => messages['warning'];

  factory RemoteConfig.fromJson(Map<String, dynamic> json) {
    return RemoteConfig(
      version: json['version'] as String? ?? '',
      minVersion: json['min_version'] as String? ?? '2.1.0',
      maintenanceMode: json['maintenance_mode'] as bool? ?? false,
      maintenanceMessage: json['maintenance_message'] as String? ?? '',
      features: (json['features'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, v as bool)) ??
          const {},
      network: (json['network'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, v as String? ?? '')) ??
          const {},
      messages: (json['messages'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, v as String? ?? '')) ??
          const {},
    );
  }
}

class RemoteConfigNotifier extends StateNotifier<RemoteConfig> {
  static const String _url = 'https://verdischain.com/api/tx-relay';

  RemoteConfigNotifier() : super(const RemoteConfig());

  Future<void> fetch() async {
    try {
      final response = await http.post(
        Uri.parse(_url),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'action': 'app-config'}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as Map<String, dynamic>;
        if (data['ok'] == true && data['data'] != null) {
          state = RemoteConfig.fromJson(data['data'] as Map<String, dynamic>);
        }
      }
    } catch (_) {
      // Silent fail — use defaults
    }
  }
}

final remoteConfigProvider =
    StateNotifierProvider<RemoteConfigNotifier, RemoteConfig>((ref) {
  return RemoteConfigNotifier();
});
