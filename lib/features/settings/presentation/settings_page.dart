import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/config/network_config.dart';
import 'package:verdis_wallet/core/security/secure_storage.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'package:go_router/go_router.dart';

class SettingsPage extends ConsumerStatefulWidget {
  const SettingsPage({super.key});

  @override
  ConsumerState<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends ConsumerState<SettingsPage> {
  String? _recoveryEmail;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadEmail();
  }

  Future<void> _loadEmail() async {
    final storage = ref.read(secureStorageProvider);
    final email = await storage.getRecoveryEmail();
    if (mounted) {
      setState(() {
        _recoveryEmail = email;
        _isLoading = false;
      });
    }
  }

  Future<void> _addOrUpdateEmail() async {
    final emailController = TextEditingController(text: _recoveryEmail ?? '');

    final result = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(_recoveryEmail != null ? 'Update Email' : 'Add Your Email'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Your email is used for wallet recovery and important account notifications.',
              style: TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: emailController,
              decoration: const InputDecoration(
                labelText: 'Email Address',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.email),
                hintText: 'you@example.com',
              ),
              keyboardType: TextInputType.emailAddress,
              autofocus: true,
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              final email = emailController.text.trim();
              if (email.isNotEmpty && RegExp(r'^[\w.+-]+@[\w-]+\.[\w.-]+$').hasMatch(email)) {
                Navigator.pop(context, email);
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Please enter a valid email address')),
                );
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );

    if (result == null) return;

    final storage = ref.read(secureStorageProvider);
    await storage.setRecoveryEmail(result);
    if (mounted) {
      setState(() => _recoveryEmail = result);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Email saved')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const _SectionHeader('Account'),
          VerdisCard(
            onTap: () => context.push('/settings/account'),
            child: const ListTile(
              leading: Icon(Icons.account_circle, size: 32),
              title: Text('Wallet Account'),
              subtitle: Text('Address, backup, export, delete'),
              trailing: Icon(Icons.chevron_right),
            ),
          ),
          const SizedBox(height: 16),

          // Email section — direct on settings page
          VerdisCard(
            child: ListTile(
              leading: const Icon(Icons.email, size: 32),
              title: const Text('Email'),
              subtitle: Text(
                _isLoading
                    ? 'Loading...'
                    : _recoveryEmail != null
                        ? _recoveryEmail!
                        : 'Add your email for recovery & notifications',
              ),
              trailing: const Icon(Icons.chevron_right),
              onTap: _addOrUpdateEmail,
            ),
          ),
          const SizedBox(height: 24),

          const _SectionHeader('Security'),
          VerdisCard(
            onTap: () => context.push('/settings/security'),
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
            onTap: () => context.push('/settings/network'),
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
            onTap: () => context.push('/settings/about'),
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
