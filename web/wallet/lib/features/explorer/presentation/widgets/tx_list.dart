import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../explorer_providers.dart';

class TxListWidget extends ConsumerWidget {
  const TxListWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final txsState = ref.watch(txsProvider);
    final theme = Theme.of(context);

    return txsState.when(
      loading: () => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: 8,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (_, __) => const ShimmerPlaceholder(height: 80),
      ),
      error: (error, _) => Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.redAccent),
            const SizedBox(height: 12),
            Text('Failed to load transactions', style: theme.textTheme.titleMedium),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => ref.read(txsProvider.notifier).refresh(),
              child: const Text('Retry'),
            ),
          ],
        ),
      ),
      data: (txs) {
        if (txs.isEmpty) {
          return const EmptyState(
            icon: Icons.swap_horiz_rounded,
            title: 'No transactions found',
            subtitle: 'Recent transaction history will appear here.',
          );
        }

        return RefreshIndicator(
          color: theme.colorScheme.primary,
          onRefresh: () => ref.read(txsProvider.notifier).refresh(),
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: txs.length,
            itemBuilder: (context, index) {
              final tx = txs[index];
              final isSuccess = tx.status == 'success';

              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: VerdisCard(
                  onTap: () => _showTxDetail(context, tx),
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: isSuccess
                              ? theme.colorScheme.primary.withOpacity(0.12)
                              : Colors.red.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: isSuccess
                                ? theme.colorScheme.primary.withOpacity(0.3)
                                : Colors.red.withOpacity(0.3),
                          ),
                        ),
                        child: Icon(
                          _getModuleIcon(tx.module),
                          color: isSuccess ? theme.colorScheme.primary : Colors.redAccent,
                          size: 22,
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  '${tx.module}.${tx.call}',
                                  style: theme.textTheme.titleSmall?.copyWith(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                Text(
                                  _formatAmount(tx.amount),
                                  style: theme.textTheme.titleSmall?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: theme.colorScheme.primary,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Hash: ${tx.hash}',
                              style: theme.textTheme.bodySmall?.copyWith(
                                fontFamily: 'Monospace',
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 6),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  'From: ${_shortenAddr(tx.from)}',
                                  style: theme.textTheme.labelSmall,
                                ),
                                Text(
                                  _formatTime(tx.timestamp),
                                  style: theme.textTheme.labelSmall,
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Icon(Icons.chevron_right, color: theme.colorScheme.onSurfaceVariant, size: 18),
                    ],
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }

  void _showTxDetail(BuildContext context, TransactionRecord tx) {
    final theme = Theme.of(context);
    final isSuccess = tx.status == 'success';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: theme.colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.outline,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Icon(
                    isSuccess ? Icons.check_circle_rounded : Icons.cancel_rounded,
                    color: isSuccess ? Colors.green : Colors.red,
                    size: 28,
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'Transaction Details',
                    style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              _buildDetailRow(context, 'Status', isSuccess ? 'Success (In Block #${tx.blockNumber})' : 'Failed'),
              _buildDetailRow(context, 'Module / Call', '${tx.module}.${tx.call}'),
              _buildDetailRow(context, 'Tx Hash', tx.hash, isMonospace: true),
              _buildDetailRow(context, 'Signer / From', tx.from, isMonospace: true),
              _buildDetailRow(context, 'Recipient / To', tx.to, isMonospace: true),
              _buildDetailRow(context, 'Amount', _formatAmount(tx.amount)),
              _buildDetailRow(context, 'Fee', '${(tx.fee / 1e18).toStringAsFixed(6)} VRDX'),
              _buildDetailRow(context, 'Block Number', '#${tx.blockNumber}'),
              if (tx.timestamp != null)
                _buildDetailRow(context, 'Timestamp', DateFormat('yyyy-MM-dd HH:mm:ss').format(tx.timestamp!)),
              const SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }

  Widget _buildDetailRow(BuildContext context, String label, String value, {bool isMonospace = false}) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: theme.textTheme.labelMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: theme.textTheme.bodyMedium?.copyWith(
                fontFamily: isMonospace ? 'Monospace' : null,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  IconData _getModuleIcon(String module) {
    switch (module) {
      case 'balances':
        return Icons.send_rounded;
      case 'staking':
        return Icons.lock_clock_rounded;
      case 'ammDex':
        return Icons.currency_exchange_rounded;
      case 'ecoCredits':
        return Icons.eco_rounded;
      case 'governance':
        return Icons.how_to_vote_rounded;
      default:
        return Icons.code_rounded;
    }
  }

  String _formatAmount(int planck) {
    final vrdx = planck / 1e18;
    return '${vrdx.toStringAsFixed(vrdx < 1 ? 4 : 2)} VRDX';
  }

  String _shortenAddr(String addr) {
    if (addr.length <= 14) return addr;
    return '${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}';
  }

  String _formatTime(DateTime? dt) {
    if (dt == null) return '';
    final diff = DateTime.now().difference(dt);
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return DateFormat('MMM d').format(dt);
  }
}
