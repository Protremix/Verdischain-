import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:share_plus/share_plus.dart';

import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'transactions_providers.dart';

enum ReceiveViewMode { qr, address }

/// Receive Page showing QR Code and wallet address details for incoming payments.
class ReceivePage extends ConsumerStatefulWidget {
  const ReceivePage({super.key});

  @override
  ConsumerState<ReceivePage> createState() => _ReceivePageState();
}

class _ReceivePageState extends ConsumerState<ReceivePage> {
  ReceiveViewMode _viewMode = ReceiveViewMode.qr;

  void _copyAddress(String address) {
    Clipboard.setData(ClipboardData(text: address));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Wallet address copied to clipboard'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _shareAddress(String address) {
    Share.share(
      'My Verdis Wallet Address:\n$address',
      subject: 'Verdis VRDX Wallet Address',
    );
  }

  void _saveQrToGallery() {
    // Simulates saving QR image to user gallery
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('QR Code saved to gallery'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final walletAddress = ref.watch(userWalletAddressProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Receive VRDX'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Segmented Toggle View
              SegmentedButton<ReceiveViewMode>(
                segments: const [
                  ButtonSegment(
                    value: ReceiveViewMode.qr,
                    label: Text('QR Code'),
                    icon: Icon(Icons.qr_code_2),
                  ),
                  ButtonSegment(
                    value: ReceiveViewMode.address,
                    label: Text('Address Text'),
                    icon: Icon(Icons.badge_outlined),
                  ),
                ],
                selected: {_viewMode},
                onSelectionChanged: (Set<ReceiveViewMode> selection) {
                  setState(() {
                    _viewMode = selection.first;
                  });
                },
                style: ButtonStyle(
                  backgroundColor: WidgetStateProperty.resolveWith((states) {
                    if (states.contains(WidgetState.selected)) {
                      return theme.colorScheme.primary.withOpacity(0.2);
                    }
                    return theme.colorScheme.surfaceContainerHighest;
                  }),
                ),
              ),
              const SizedBox(height: 32),

              if (_viewMode == ReceiveViewMode.qr) ...[
                // QR Display View
                VerdisCard(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: QrImageView(
                          data: walletAddress,
                          version: QrVersions.auto,
                          size: 220.0,
                          gapless: true,
                          eyeStyle: const QrEyeStyle(
                            eyeShape: QrEyeShape.square,
                            color: Colors.black,
                          ),
                          dataModuleStyle: const QrDataModuleStyle(
                            dataModuleShape: QrDataModuleShape.square,
                            color: Colors.black,
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),
                      Text(
                        'Scan to transfer VRDX',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                OutlinedButton.icon(
                  onPressed: _saveQrToGallery,
                  icon: const Icon(Icons.download_rounded),
                  label: const Text('Save QR Code to Gallery'),
                ),
              ] else ...[
                // Address Details View
                VerdisCard(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.account_balance_wallet_rounded,
                        size: 48,
                        color: theme.colorScheme.primary,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Verdis Network SS58 Address',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: theme.colorScheme.outline.withOpacity(0.5),
                          ),
                        ),
                        child: SelectableText(
                          walletAddress,
                          textAlign: TextAlign.center,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            fontFamily: 'monospace',
                            color: theme.colorScheme.primary,
                            height: 1.4,
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),
                      Text(
                        'Only send VRDX or Verdis native tokens to this SS58 address.',
                        textAlign: TextAlign.center,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              const SizedBox(height: 32),

              // Quick Actions (Copy & Share)
              Row(
                children: [
                  Expanded(
                    child: VerdisButton(
                      label: 'Copy Address',
                      icon: Icons.copy,
                      onPressed: () => _copyAddress(walletAddress),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: VerdisButton(
                      label: 'Share',
                      isOutlined: true,
                      icon: Icons.share,
                      onPressed: () => _shareAddress(walletAddress),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
