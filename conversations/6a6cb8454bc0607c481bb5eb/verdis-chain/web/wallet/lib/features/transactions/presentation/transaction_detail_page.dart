import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

import 'package:verdis_wallet/core/config/network_config.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'transactions_providers.dart';
import 'utils/address_validator.dart';

/// Transaction Detail Page showing deep inspection of extrinsic data
class TransactionDetailPage extends ConsumerWidget {

  const TransactionDetailPage({
    super.key,
    this.transaction,
    this.txHash,
  });
  final TransactionRecord? transaction;
  final String? txHash;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (transaction != null) {
      return _buildContent(context, ref, transaction!);
    }

    if (txHash != null) {
      final detailAsync = ref.watch(transactionDetailProvider(txHash!));
      return Scaffold(
        appBar: AppBar(title: const Text('Transaction Details')),
        body: detailAsync.when(
          data: (tx) {
            if (tx == null) {
              return const EmptyState(
                icon: Icons.search_off_rounded,
                title: 'Transaction Not Found',
                subtitle: 'Could not find details for this hash on the network.',
              );
            }
            return _buildContent(context, ref, tx);
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (err, _) => Center(child: Text('Error loading details: $err')),
        ),
      );
    }

    return const Scaffold(
      body: Center(child: Text('No transaction provided')),
    );
  }

  Widget _buildContent(
      BuildContext context, WidgetRef ref, TransactionRecord tx,) {
    final theme = Theme.of(context);
    final userAddress = ref.watch(userWalletAddressProvider);

    final isSend = tx.module == 'balances' &&
        tx.from.toLowerCase() == userAddress.toLowerCase();
    final isReceive = tx.module == 'balances' &&
        tx.to.toLowerCase() == userAddress.toLowerCase();

    final amountVRDX = tx.amount / 1e18;
    final feeVRDX = tx.fee / 1e18;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Transaction Details'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Top Status & Amount Card
              VerdisCard(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    _buildStatusChip(theme, tx.status),
                    const SizedBox(height: 16),
                    Text(
                      '${isReceive ? '+' : (isSend ? '-' : '')}${amountVRDX.toStringAsFixed(4)} VRDX',
                      style: theme.textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: isReceive
                            ? theme.colorScheme.primary
                            : theme.colorScheme.onSurface,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${tx.module}.${tx.call}',
                      style: theme.textTheme.titleSmall?.copyWith(
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Overview Key-Value Details
              VerdisCard(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    _buildDetailRow(
                      context,
                      label: 'Transaction Hash',
                      value: AddressValidator.formatAddress(tx.hash, start: 8, end: 8),
                      fullValueToCopy: tx.hash,
                      isMonospace: true,
                    ),
                    const Divider(height: 24),
                    _buildDetailRow(
                      context,
                      label: 'Block Number',
                      value: '#${tx.blockNumber}',
                    ),
                    const Divider(height: 24),
                    _buildDetailRow(
                      context,
                      label: 'Block Hash',
                      value: AddressValidator.formatAddress(tx.blockHash, start: 8, end: 8),
                      fullValueToCopy: tx.blockHash,
                      isMonospace: true,
                    ),
                    const Divider(height: 24),
                    _buildDetailRow(
                      context,
                      label: 'Timestamp',
                      value: tx.timestamp != null
                          ? DateFormat('yyyy-MM-dd HH:mm:ss')
                              .format(tx.timestamp!)
                          : 'N/A',
                    ),
                    const Divider(height: 24),
                    _buildDetailRow(
                      context,
                      label: 'From',
                      value: AddressValidator.formatAddress(tx.from),
                      fullValueToCopy: tx.from,
                      isMonospace: true,
                    ),
                    const Divider(height: 24),
                    _buildDetailRow(
                      context,
                      label: 'To',
                      value: AddressValidator.formatAddress(tx.to),
                      fullValueToCopy: tx.to,
                      isMonospace: true,
                    ),
                    const Divider(height: 24),
                    _buildDetailRow(
                      context,
                      label: 'Network Fee',
                      value: '${feeVRDX.toStringAsFixed(6)} VRDX',
                    ),
                    const Divider(height: 24),
                    _buildDetailRow(
                      context,
                      label: 'Pallet / Module Call',
                      value: '${tx.module}.${tx.call}',
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Decoded Arguments Section
              if (tx.args != null && tx.args!.isNotEmpty) ...[
                Text(
                  'Decoded Extrinsic Arguments',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                VerdisCard(
                  padding: const EdgeInsets.all(16),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: SelectableText(
                      const JsonEncoder.withIndent('  ').convert(tx.args),
                      style: theme.textTheme.bodySmall?.copyWith(
                        fontFamily: 'monospace',
                        color: theme.colorScheme.onSurface,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
              ],

              // View in Block Explorer Button
              VerdisButton(
                label: 'View in Block Explorer',
                icon: Icons.open_in_new_rounded,
                isOutlined: true,
                onPressed: () async {
                  final url =
                      Uri.parse('${NetworkConfig.explorerUrl}/tx/${tx.hash}');
                  if (await canLaunchUrl(url)) {
                    await launchUrl(url);
                  }
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChip(ThemeData theme, String status) {
    Color bg;
    Color fg;
    IconData icon;

    switch (status.toLowerCase()) {
      case 'confirmed':
        bg = theme.colorScheme.primary.withOpacity(0.15);
        fg = theme.colorScheme.primary;
        icon = Icons.check_circle_rounded;
        break;
      case 'pending':
        bg = Colors.amber.withOpacity(0.15);
        fg = Colors.amber;
        icon = Icons.access_time_filled_rounded;
        break;
      case 'failed':
      default:
        bg = theme.colorScheme.error.withOpacity(0.15);
        fg = theme.colorScheme.error;
        icon = Icons.cancel_rounded;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: fg),
          const SizedBox(width: 8),
          Text(
            status.toUpperCase(),
            style: TextStyle(
              color: fg,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(
    BuildContext context, {
    required String label,
    required String value,
    String? fullValueToCopy,
    bool isMonospace = false,
  }) {
    final theme = Theme.of(context);
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              value,
              style: theme.textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w600,
                fontFamily: isMonospace ? 'monospace' : null,
              ),
            ),
            if (fullValueToCopy != null) ...[
              const SizedBox(width: 4),
              IconButton(
                icon: const Icon(Icons.copy, size: 14),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: fullValueToCopy));
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('$label copied to clipboard')),
                  );
                },
              ),
            ],
          ],
        ),
      ],
    );
  }
}
