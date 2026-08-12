import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;
import 'package:verdis_wallet/core/config/network_config.dart';
import 'package:verdis_wallet/core/security/secure_storage.dart';
import 'package:verdis_wallet/core/security/wallet_crypto.dart';
import 'package:verdis_wallet/features/home/presentation/home_providers.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'package:bip39/bip39.dart' as bip39;
import 'package:hex/hex.dart';
import 'package:polkadart_keyring/polkadart_keyring.dart';

/// Email Recovery Page — restore wallet from email + password + PIN backup.
/// Matches web wallet exactly: password encrypts/decrypts via PBKDF2+AES-256-GCM,
/// PIN is only used for server-side backend verification/rate-limiting.
class EmailRecoveryPage extends ConsumerStatefulWidget {
  const EmailRecoveryPage({super.key});

  @override
  ConsumerState<EmailRecoveryPage> createState() => _EmailRecoveryPageState();
}

class _EmailRecoveryPageState extends ConsumerState<EmailRecoveryPage> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _pinController = TextEditingController();
  bool _isLoading = false;
  String? _error;

  static const String _relayUrl = 'https://verdischain.com/api/tx-relay';

  Future<void> _recover() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text;
    final pin = _pinController.text.trim();

    if (email.isEmpty) {
      setState(() => _error = 'Please enter your email');
      return;
    }
    if (password.isEmpty) {
      setState(() => _error = 'Please enter your recovery password');
      return;
    }
    if (pin.isEmpty || !RegExp(r'^\d{4,6}$').hasMatch(pin)) {
      setState(() => _error = 'Wallet PIN is required (4-6 digits)');
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // 1. Fetch encrypted backup from TX Relay (PIN verified server-side)
      final response = await http.post(
        Uri.parse(_relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'action': 'wallet-recover',
          'email': email,
          'pin': pin,
        }),
      ).timeout(const Duration(seconds: 20));

      final data = jsonDecode(response.body);

      if (data['ok'] != true) {
        setState(() {
          _isLoading = false;
          _error = data['error']?.toString() ?? 'Recovery failed. Check your email and PIN.';
        });
        return;
      }

      // 2. Decrypt mnemonic using password (PBKDF2 + AES-256-GCM — matches web wallet)
      final backup = data['data']['backup'] as Map<String, dynamic>;
      final mnemonic = await WalletCrypto.decryptBackup(
        backup['ciphertext'] as String,
        backup['salt'] as String,
        backup['iv'] as String,
        password,
      );

      // 3. Validate mnemonic
      if (!bip39.validateMnemonic(mnemonic)) {
        setState(() {
          _isLoading = false;
          _error = 'Decryption produced an invalid recovery phrase. Check your password.';
        });
        return;
      }

      // 4. Derive keypair from mnemonic
      final keyPair = KeyPair.sr25519;
      keyPair.ss58Format = 909;
      await keyPair.fromMnemonic(mnemonic);

      final address = keyPair.address;
      final publicKeyHex = HEX.encode(keyPair.publicKey.bytes);
      final privateKeyHex = HEX.encode(keyPair.bytes());

      // 5. Store wallet in secure storage
      final storage = ref.read(secureStorageProvider);
      await storage.storePrivateKey(privateKeyHex);
      await storage.storePublicKey(publicKeyHex);
      await storage.write(AppConstants.walletKey, address);
      await storage.write('verdis_mnemonic', mnemonic);
      await storage.write(AppConstants.onboardingCompleteKey, 'true');
      await storage.setRecoveryEmail(email);

      // 6. Update address provider
      ref.read(selectedAddressProvider.notifier).state = address;

      // 7. Navigate to home
      if (mounted) {
        context.go('/home');
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        if (e is FormatException || e.toString().contains('SecretBox') || e.toString().contains('Mac')) {
          _error = 'Wrong password or PIN — could not decrypt wallet.';
        } else {
          _error = 'Error: $e';
        }
      });
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _pinController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E0A),
      appBar: AppBar(
        title: const Text('Recover with Email'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.mark_email_read, size: 48, color: const Color(0xFF00FF88)),
              const SizedBox(height: 16),
              Text(
                'Recover Your Wallet',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFFE8F0E8),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Enter the email, password, and PIN you used when setting up email recovery.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFF8B9D8B),
                ),
              ),
              const SizedBox(height: 32),

              TextField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                style: const TextStyle(color: Color(0xFFE8F0E8)),
                decoration: const InputDecoration(
                  labelText: 'Email Address',
                  prefixIcon: Icon(Icons.email, color: Color(0xFF00FF88)),
                ),
              ),
              const SizedBox(height: 16),

              TextField(
                controller: _passwordController,
                obscureText: true,
                style: const TextStyle(color: Color(0xFFE8F0E8)),
                decoration: const InputDecoration(
                  labelText: 'Recovery Password',
                  helperText: 'The password you set when backing up (not your PIN)',
                  prefixIcon: Icon(Icons.key, color: Color(0xFF00FF88)),
                ),
              ),
              const SizedBox(height: 16),

              TextField(
                controller: _pinController,
                keyboardType: TextInputType.number,
                obscureText: true,
                style: const TextStyle(color: Color(0xFFE8F0E8)),
                decoration: const InputDecoration(
                  labelText: 'Wallet PIN',
                  prefixIcon: Icon(Icons.lock, color: Color(0xFF00FF88)),
                ),
              ),
              const SizedBox(height: 24),

              if (_error != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Text(
                    _error!,
                    style: const TextStyle(color: Color(0xFFCF6679), fontSize: 13),
                  ),
                ),

              VerdisButton(
                label: 'Recover Wallet',
                isLoading: _isLoading,
                onPressed: _isLoading ? null : _recover,
              ),

              const SizedBox(height: 32),
              Center(
                child: TextButton(
                  onPressed: () => context.push('/import-wallet'),
                  child: const Text(
                    'Recover with 12-word phrase instead',
                    style: TextStyle(color: Color(0xFF8B9D8B), fontSize: 13),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
