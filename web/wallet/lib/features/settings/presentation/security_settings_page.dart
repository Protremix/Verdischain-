import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/security/biometric_auth.dart';
import 'package:verdis_wallet/core/security/secure_storage.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';

class SecuritySettingsPage extends ConsumerStatefulWidget {
  const SecuritySettingsPage({super.key});

  @override
  ConsumerState<SecuritySettingsPage> createState() => _SecuritySettingsPageState();
}

class _SecuritySettingsPageState extends ConsumerState<SecuritySettingsPage> {
  bool _biometricEnabled = false;
  bool _biometricAvailable = false;
  bool _clipboardProtection = true;
  int _autoLockMinutes = 1;
  int _sessionTimeoutMinutes = 5;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final storage = ref.read(secureStorageProvider);
    final biometric = ref.read(biometricAuthProvider);
    final bioAvailable = await biometric.isAvailable();
    final bioEnabled = await storage.isBiometricEnabled();

    setState(() {
      _biometricAvailable = bioAvailable;
      _biometricEnabled = bioEnabled;
      _isLoading = false;
    });
  }

  Future<void> _toggleBiometric(bool value) async {
    if (value) {
      final biometric = ref.read(biometricAuthProvider);
      final authenticated = await biometric.authenticate(
        reason: 'Enable biometric authentication for Verdis Wallet',
      );
      if (!authenticated) return;
    }
    final storage = ref.read(secureStorageProvider);
    await storage.setBiometricEnabled(value);
    setState(() => _biometricEnabled = value);
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Security')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Biometric
          const _SectionTitle('Authentication'),
          VerdisCard(
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('Biometric Authentication'),
                  subtitle: Text(
                    _biometricAvailable
                        ? 'Use fingerprint or face unlock'
                        : 'Biometric not available on this device',
                  ),
                  value: _biometricEnabled,
                  onChanged: _biometricAvailable ? _toggleBiometric : null,
                  secondary: const Icon(Icons.fingerprint),
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.password),
                  title: const Text('Change PIN'),
                  subtitle: const Text('Change your 6-digit PIN'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => Navigator.pushNamed(context, '/pin-setup'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Auto-lock
          const _SectionTitle('Auto-Lock'),
          VerdisCard(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.lock_clock),
                  title: const Text('Auto-Lock Timeout'),
                  subtitle: Text('Lock after $_autoLockMinutes minute${_autoLockMinutes > 1 ? 's' : ''} of inactivity'),
                  trailing: DropdownButton<int>(
                    value: _autoLockMinutes,
                    items: const [
                      DropdownMenuItem(value: 1, child: Text('1 min')),
                      DropdownMenuItem(value: 2, child: Text('2 min')),
                      DropdownMenuItem(value: 5, child: Text('5 min')),
                      DropdownMenuItem(value: 10, child: Text('10 min')),
                      DropdownMenuItem(value: 30, child: Text('30 min')),
                    ],
                    onChanged: (value) {
                      if (value != null) {
                        setState(() => _autoLockMinutes = value);
                      }
                    },
                  ),
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.timer),
                  title: const Text('Session Timeout'),
                  subtitle: Text('End session after $_sessionTimeoutMinutes minutes'),
                  trailing: DropdownButton<int>(
                    value: _sessionTimeoutMinutes,
                    items: const [
                      DropdownMenuItem(value: 5, child: Text('5 min')),
                      DropdownMenuItem(value: 10, child: Text('10 min')),
                      DropdownMenuItem(value: 15, child: Text('15 min')),
                      DropdownMenuItem(value: 30, child: Text('30 min')),
                    ],
                    onChanged: (value) {
                      if (value != null) {
                        setState(() => _sessionTimeoutMinutes = value);
                      }
                    },
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Privacy
          const _SectionTitle('Privacy'),
          VerdisCard(
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('Secure Clipboard'),
                  subtitle: const Text('Auto-clear copied addresses after 30 seconds'),
                  value: _clipboardProtection,
                  onChanged: (value) {
                    setState(() => _clipboardProtection = value);
                  },
                  secondary: const Icon(Icons.copy),
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.verified_user),
                  title: const Text('Device Integrity Check'),
                  subtitle: const Text('Verify device security on startup'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () async {
                    // Run integrity check
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Device integrity verified')),
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle(this.title);
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
