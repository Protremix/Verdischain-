import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/security/secure_storage.dart';
import 'package:verdis_wallet/core/security/wallet_crypto.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';

class AccountSettingsPage extends ConsumerStatefulWidget {
  const AccountSettingsPage({super.key});

  @override
  ConsumerState<AccountSettingsPage> createState() => _AccountSettingsPageState();
}

class _AccountSettingsPageState extends ConsumerState<AccountSettingsPage> {
  String? _address;
  String? _publicKey;
  bool _isLoading = true;
  bool _showBackup = false;
  String? _backupPhrase;

  @override
  void initState() {
    super.initState();
    _loadAccountInfo();
  }

  Future<void> _loadAccountInfo() async {
    final storage = ref.read(secureStorageProvider);
    final publicKey = await storage.getPublicKey();
    if (publicKey != null) {
      final keyBytes = WalletCrypto.hexToBytes(publicKey);
      setState(() {
        _address = WalletCrypto.ss58Address(keyBytes);
        _publicKey = publicKey;
        _isLoading = false;
      });
    } else {
      setState(() => _isLoading = false);
    }
  }

  void _copyAddress() {
    if (_address != null) {
      Clipboard.setData(ClipboardData(text: _address!));
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Address copied to clipboard')),
      );
    }
  }

  Future<void> _revealBackupPhrase() async {
    // Require PIN re-entry before showing backup phrase
    final confirmed = await _showPinDialog();
    if (!confirmed) return;

    // In production, this would decrypt and show the mnemonic
    setState(() {
      _showBackup = true;
      _backupPhrase = 'Recovery phrase requires decryption with PIN';
    });
  }

  Future<bool> _showPinDialog() async {
    final pinController = TextEditingController();
    return await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Enter PIN'),
        content: TextField(
          controller: pinController,
          keyboardType: TextInputType.number,
          obscureText: true,
          maxLength: 6,
          decoration: const InputDecoration(
            labelText: 'PIN',
            hintText: 'Enter your 6-digit PIN',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
                        final storage = ref.read(secureStorageProvider);
                        final pinHash = await storage.getPinHash();
              if (pinHash != null && WalletCrypto.verifyPin(pinController.text, pinHash)) {
                if (context.mounted) Navigator.pop(context, true);
              } else {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Invalid PIN')),
                  );
                }
              }
            },
            child: const Text('Confirm'),
          ),
        ],
      ),
    ) ?? false;
  }

  Future<void> _deleteWallet() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Wallet'),
        content: const Text(
          'This will permanently delete your wallet from this device. '
          'Make sure you have your recovery phrase saved. This cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    ) ?? false;

    if (!confirmed) return;

    await ref.read(secureStorageProvider).clearWallet();

    if (mounted) {
      unawaited(Navigator.pushNamedAndRemoveUntil(context, '/welcome', (route) => false));
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
      appBar: AppBar(title: const Text('Wallet Account')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          VerdisCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Wallet Address', style: Theme.of(context).textTheme.titleSmall),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: SelectableText(
                          _address ?? 'No wallet found',
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.copy, size: 18),
                        onPressed: _copyAddress,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                if (_publicKey != null)
                  Text('Public Key: ${WalletCrypto.shortenAddress(_publicKey!, prefix: 8, suffix: 8)}',
                    style: Theme.of(context).textTheme.bodySmall,),
              ],
            ),
          ),
          const SizedBox(height: 16),

          VerdisCard(
            onTap: () => Navigator.pushNamed(context, '/explorer'),
            child: const ListTile(
              leading: Icon(Icons.search),
              title: Text('View on Explorer'),
              subtitle: Text('See your address on Verdiscan'),
              trailing: Icon(Icons.chevron_right),
            ),
          ),
          const SizedBox(height: 16),

          VerdisCard(
            onTap: _revealBackupPhrase,
            child: const ListTile(
              leading: Icon(Icons.key),
              title: Text('Reveal Recovery Phrase'),
              subtitle: Text('Requires PIN confirmation'),
              trailing: Icon(Icons.chevron_right),
            ),
          ),
          if (_showBackup) ...[
            const SizedBox(height: 8),
            VerdisCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Recovery Phrase', style: Theme.of(context).textTheme.titleSmall),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(_backupPhrase ?? '', style: Theme.of(context).textTheme.bodyMedium),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 16),

          VerdisCard(
            onTap: () {
              // Export wallet functionality
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Export requires PIN authentication')),
              );
            },
            child: const ListTile(
              leading: Icon(Icons.download),
              title: Text('Export Wallet'),
              subtitle: Text('Export keystore for backup'),
              trailing: Icon(Icons.chevron_right),
            ),
          ),
          const SizedBox(height: 32),

          // Delete wallet
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.error,
                foregroundColor: Colors.black,
              ),
              onPressed: _deleteWallet,
              child: const Text('Delete Wallet'),
            ),
          ),
        ],
      ),
    );
  }
}
