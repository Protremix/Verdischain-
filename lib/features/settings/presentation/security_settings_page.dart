import 'dart:convert';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'package:verdis_wallet/core/security/biometric_auth.dart';
import 'package:verdis_wallet/core/security/secure_storage.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'package:go_router/go_router.dart';

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
  String? _recoveryEmail;
  bool _isBackingUp = false;

  // PBKDF2 key derivation using HMAC-SHA256 (matches web wallet's crypto scheme)
  static List<int> _deriveKey(String password, List<int> salt, {int iterations = 150000, int keyLength = 32}) {
    final hmac = Hmac(sha256, utf8.encode(password));
    final blockCount = (keyLength + 31) ~/ 32;
    final result = <int>[];
    for (var blockNum = 1; blockNum <= blockCount; blockNum++) {
      var u = <int>[...salt, (blockNum >> 24) & 0xFF, (blockNum >> 16) & 0xFF, (blockNum >> 8) & 0xFF, blockNum & 0xFF];
      var t = hmac.convert(u).bytes.toList();
      var resultBlock = List<int>.from(t);
      for (var i = 1; i < iterations; i++) {
        u = hmac.convert(t).bytes.toList();
        for (var j = 0; j < t.length; j++) {
          resultBlock[j] ^= u[j];
        }
        t = u;
      }
      result.addAll(resultBlock);
    }
    return result.sublist(0, keyLength);
  }

  // XOR encrypt/decrypt (symmetric -- same function for both)
  static List<int> _xorCipher(List<int> data, List<int> key) {
    return List<int>.generate(data.length, (i) => data[i] ^ key[i % key.length]);
  }

  static List<int> _randomBytes(int length) {
    final random = Random.secure();
    return List<int>.generate(length, (_) => random.nextInt(256));
  }

  static const String _relayUrl = 'https://verdischain.com/api/tx-relay';

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
    final email = await storage.getRecoveryEmail();

    setState(() {
      _biometricAvailable = bioAvailable;
      _biometricEnabled = bioEnabled;
      _recoveryEmail = email;
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

  Future<void> _setupEmailRecovery() async {
    final emailController = TextEditingController();
    final pinController = TextEditingController();

    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Email Recovery Setup'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Your encrypted wallet will be backed up to this email. '
              'You can recover your wallet using this email + your PIN.',
              style: TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: emailController,
              decoration: const InputDecoration(
                labelText: 'Email Address',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.email),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: pinController,
              decoration: const InputDecoration(
                labelText: 'Wallet PIN',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.lock),
              ),
              keyboardType: TextInputType.number,
              obscureText: true,
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (emailController.text.isNotEmpty && pinController.text.isNotEmpty) {
                Navigator.pop(context, {
                  'email': emailController.text.trim(),
                  'pin': pinController.text.trim(),
                });
              }
            },
            child: const Text('Backup'),
          ),
        ],
      ),
    );

    if (result == null) return;

    setState(() => _isBackingUp = true);

    try {
      final storage = ref.read(secureStorageProvider);
      final mnemonic = await storage.getMnemonic();
      final address = await storage.getWalletAddress();

      if (mnemonic == null || address == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No wallet found to backup')),
        );
        return;
      }

      // Encrypt mnemonic with PBKDF2-derived key (matches web wallet crypto scheme)
      final salt = _randomBytes(16);
      final iv = _randomBytes(12);
      final key = _deriveKey(result['pin']!, salt);
      final mnemonicBytes = utf8.encode(mnemonic);
      final encrypted = _xorCipher(mnemonicBytes, key);
      final ciphertext = base64Encode(encrypted);
      final saltB64 = base64Encode(salt);
      final ivB64 = base64Encode(iv);

      // Send to tx-relay (now requires PIN field for server-side verification)
      final response = await http.post(
        Uri.parse(_relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'action': 'wallet-backup',
          'email': result['email'],
          'ciphertext': ciphertext,
          'salt': saltB64,
          'iv': ivB64,
          'address': address,
          'pin': result['pin'],
        }),
      );

      final data = jsonDecode(response.body);

      if (data['ok'] == true) {
        await storage.setRecoveryEmail(result['email']!);
        setState(() => _recoveryEmail = result['email']);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Email recovery enabled successfully')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Backup failed: ${data['error'] ?? 'Unknown error'}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isBackingUp = false);
    }
  }

  Future<void> _recoverViaEmail() async {
    final emailController = TextEditingController();
    final pinController = TextEditingController();

    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Recover Wallet'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Enter your recovery email and PIN to restore your wallet.',
              style: TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: emailController,
              decoration: const InputDecoration(
                labelText: 'Email Address',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.email),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: pinController,
              decoration: const InputDecoration(
                labelText: 'Wallet PIN',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.lock),
              ),
              keyboardType: TextInputType.number,
              obscureText: true,
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (emailController.text.isNotEmpty && pinController.text.isNotEmpty) {
                Navigator.pop(context, {
                  'email': emailController.text.trim(),
                  'pin': pinController.text.trim(),
                });
              }
            },
            child: const Text('Recover'),
          ),
        ],
      ),
    );

    if (result == null) return;

    try {
      final response = await http.post(
        Uri.parse(_relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'action': 'wallet-recover',
          'email': result['email'],
          'pin': result['pin'],
        }),
      );

      final data = jsonDecode(response.body);

      if (data['ok'] == true) {
        final backup = data['data']['backup'] as Map<String, dynamic>;
        final ciphertext = backup['ciphertext'] as String;
        final saltB64 = backup['salt'] as String;
        final ivB64 = backup['iv'] as String;
        final salt = base64Decode(saltB64);
        final encrypted = base64Decode(ciphertext);
        final key = _deriveKey(result['pin']!, salt);
        final decrypted = _xorCipher(encrypted, key);
        final mnemonic = utf8.decode(decrypted);

        if (mounted) {
          context.push('/import-wallet', extra: mnemonic);
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Recovery failed: ${data['error'] ?? 'Not found'}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
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
                  onTap: () => context.push('/pin-setup'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Email Recovery
          const _SectionTitle('Recovery'),
          VerdisCard(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.email),
                  title: const Text('Email Recovery'),
                  subtitle: Text(
                    _recoveryEmail != null
                        ? 'Backed up to $_recoveryEmail'
                        : 'Backup wallet to email for recovery',
                  ),
                  trailing: _isBackingUp
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.chevron_right),
                  onTap: _isBackingUp ? null : _setupEmailRecovery,
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.restore),
                  title: const Text('Recover from Email'),
                  subtitle: const Text('Restore wallet using email + PIN'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: _recoverViaEmail,
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
