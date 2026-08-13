import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/config/network_config.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';

class SettingsPage extends ConsumerWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const _SectionHeader('Account'),
          VerdisCard(
            onTap: () => Navigator.pushNamed(context, '/settings/account'),
            child: const ListTile(
              leading: Icon(Icons.account_circle, size: 32),
              title: Text('Wallet Account'),
              subtitle: Text('Address, backup, export, delete'),
              trailing: Icon(Icons.chevron_right),
            ),
          ),
          const SizedBox(height: 24),

          const _SectionHeader('Security'),
          VerdisCard(
            onTap: () => Navigator.pushNamed(context, '/settings/security'),
            child: const ListTile(
              leading: Icon(Icons.security, size: 32),
              title: Text('Security & Authentication'),
              subtitle: Text('Biometric, PIN, auto-lock, clipboard'),
              trailing: Icon(Icons.chevron_right),
            ),
          ),
          const SizedBox(height: 24),

          const _SectionHeader('Network'),
          VerdisCard(
            onTap: () => Navigator.pushNamed(context, '/settings/network'),
            child: const ListTile(
              leading: Icon(Icons.language, size: 32),
              title: Text('Network & RPC'),
              subtitle: Text('Endpoint, connection, latency'),
              trailing: Icon(Icons.chevron_right),
            ),
          ),
          const SizedBox(height: 24),

          const _SectionHeader('About'),
          VerdisCard(
            onTap: () => Navigator.pushNamed(context, '/settings/about'),
            child: const ListTile(
              leading: Icon(Icons.info, size: 32),
              title: Text('About Verdis'),
              subtitle: Text('Version, links, license, privacy'),
              trailing: Icon(Icons.chevron_right),
            ),
          ),
          const SizedBox(height: 32),

          // App version
          Center(
            child: Text(
              'Verdis Wallet v${AppConstants.appVersion}+${AppConstants.appBuild}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader(this.title);
  final String title;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, left: 4),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleSmall?.copyWith(
          color: Theme.of(context).colorScheme.primary,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
