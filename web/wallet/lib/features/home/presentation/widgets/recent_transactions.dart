import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';

/// Widget rendering a list of the last 5 transactions with action icon, amount, address, status, and detail dialog.
class RecentTransactionsList extends StatelessWidget {

  const RecentTransactionsList({
    super.key,
    required this.transactions,
    this.onViewAllTap,
    this.onTransactionTap,
  });
  final List<TransactionRecord> transactions;
  final VoidCallback? onViewAllTap;
  final Function(TransactionRecord tx)? onTransactionTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Recent Activity',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            if (onViewAllTap != null)
              TextButton(
                onPressed: onViewAllTap,
                child: const Text('View All'),
              ),
          ],
        ),
        const SizedBox(height: 12),
        if (transactions.isEmpty)
          const EmptyState(
            icon: Icons.history,
            title: 'No Recent Transactions',
            subtitle: 'Your transaction history will appear here once you make a transfer or swap.',
          )
        else
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: transactions.length,
            separatorBuilder: (context, index) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final tx = transactions[index];
              return _TransactionTile(
                transaction: tx,
                onTap: () => onTransactionTap?.call(tx) ?? _showTransactionDetails(context, tx),
              );
            },
          ),
      ],
    );
  }

  void _showTransactionDetails(BuildContext context, TransactionRecord tx) {
    final theme = Theme.of(context);
    final amountFormatted = (tx.amount / 10000000000.0).toStringAsFixed(2);

    showModalBottomSheet(
      context: context,
      backgroundColor: theme.colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.onSurfaceVariant.withOpacity(0.4),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Transaction Details',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      tx.status.toUpperCase(),
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              _detailRow(context, 'Type', '${tx.module}.${tx.call}'),
              _detailRow(context, 'Amount', '$amountFormatted VRDX'),
              _detailRow(context, 'From', tx.from),
              _detailRow(context, 'To', tx.to),
              _detailRow(context, 'Block #', '#${tx.blockNumber}'),
              _detailRow(context, 'Tx Hash', tx.hash),
              _detailRow(context, 'Fee', '${(tx.fee / 10000000000.0).toStringAsFixed(4)} VRDX'),
              if (tx.timestamp != null)
                _detailRow(context, 'Time', DateFormat('yyyy-MM-dd HH:mm:ss').format(tx.timestamp!)),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: VerdisButton(
                  label: 'Close',
                  onPressed: () => Navigator.pop(context),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _detailRow(BuildContext context, String label, String value) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
          Flexible(
            child: Text(
              value,
              style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}

class _TransactionTile extends StatelessWidget {

  const _TransactionTile({
    required this.transaction,
    required this.onTap,
  });
  final TransactionRecord transaction;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isSend = transaction.call == 'transfer' && transaction.from == '0x71C7656EC7ab88b098defB751B7401B5f6d8976F';
    final isReceive = transaction.call == 'transfer' && !isSend;
    final isSwap = transaction.module == 'ammDex' || transaction.call.contains('swap');
    final isStake = transaction.module == 'staking' || transaction.call.contains('bond') || transaction.call.contains('payout');

    IconData icon;
    Color iconColor;
    String title;
    String counterparty;

    if (isSwap) {
      icon = Icons.swap_horiz;
      iconColor = const Color(0xFF40C4FF);
      title = 'Token Swap';
      counterparty = 'DEX Liquidity Pool';
    } else if (isStake) {
      icon = Icons.energy_savings_leaf;
      iconColor = const Color(0xFFFFB300);
      title = transaction.call == 'payoutStakers' ? 'Staking Reward' : 'Staked VRDX';
      counterparty = transaction.call == 'payoutStakers' ? 'Staking Reward Pool' : _shorten(transaction.to);
    } else if (isSend) {
      icon = Icons.arrow_outward;
      iconColor = theme.colorScheme.error;
      title = 'Sent VRDX';
      counterparty = _shorten(transaction.to);
    } else {
      icon = Icons.south_west;
      iconColor = theme.colorScheme.primary;
      title = 'Received VRDX';
      counterparty = _shorten(transaction.from);
    }

    final amountFormatted = (transaction.amount / 10000000000.0).toStringAsFixed(2);
    final sign = isReceive || (isStake && transaction.call == 'payoutStakers') ? '+' : (isSend ? '-' : '');

    final timeStr = transaction.timestamp != null
        ? _formatRelativeTime(transaction.timestamp!)
        : '#${transaction.blockNumber}';

    return VerdisCard(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      onTap: onTap,
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.12),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: iconColor, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  counterparty,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '$sign$amountFormatted VRDX',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: isReceive || (isStake && transaction.call == 'payoutStakers')
                      ? theme.colorScheme.primary
                      : theme.colorScheme.onSurface,
                ),
              ),
              const SizedBox(height: 2),
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 6,
                    height: 6,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: transaction.status == 'success'
                          ? const Color(0xFF00E676)
                          : const Color(0xFFFF9800),
                    ),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    timeStr,
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _shorten(String addr) {
    if (addr.length <= 10) return addr;
    return '${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}';
  }

  String _formatRelativeTime(DateTime dateTime) {
    final diff = DateTime.now().difference(dateTime);
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }
}
