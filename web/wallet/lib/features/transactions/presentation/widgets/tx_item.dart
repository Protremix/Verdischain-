import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import 'package:verdis_wallet/shared/models/wallet_models.dart';
import '../utils/address_validator.dart';

/// Transaction item widget for transaction list
class TxItem extends StatelessWidget {

  const TxItem({
    super.key,
    required this.transaction,
    this.currentUserAddress = 'verdis1q83f7k94a9z2m3v4x5y6z7w8v9u0a1b2c3d4e5f',
    this.onTap,
  });
  final TransactionRecord transaction;
  final String currentUserAddress;
  final VoidCallback? onTap;

  bool get isSend =>
      transaction.module == 'balances' &&
      transaction.from.toLowerCase() == currentUserAddress.toLowerCase();

  bool get isReceive =>
      transaction.module == 'balances' &&
      transaction.to.toLowerCase() == currentUserAddress.toLowerCase();

  bool get isSwap =>
      transaction.module == 'ammDex' ||
      transaction.call.toLowerCase().contains('swap');

  bool get isStake =>
      transaction.module == 'staking' ||
      transaction.call.toLowerCase().contains('bond');

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final iconData = _getIcon();
    final iconColor = _getIconColor(theme);
    final iconBgColor = _getIconBgColor(theme);
    final title = _getTitle();
    final counterparty = _getCounterparty();
    final formattedAmount = _getFormattedAmount();
    final isPositive = isReceive;

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4),
      color: theme.colorScheme.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(
          color: theme.colorScheme.outline.withOpacity(0.3),
        ),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          child: Row(
            children: [
              // Type Icon
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: iconBgColor,
                  shape: BoxShape.circle,
                ),
                child: Center(
                  child: Icon(
                    iconData,
                    color: iconColor,
                    size: 20,
                  ),
                ),
              ),
              const SizedBox(width: 12),

              // Title and Counterparty/Time
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          title,
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(width: 6),
                        _buildStatusDot(theme),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Row(
                      children: [
                        Text(
                          AddressValidator.formatAddress(counterparty, start: 6, end: 4),
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                            fontFamily: 'monospace',
                          ),
                        ),
                        Text(
                          ' • ',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                        Text(
                          _formatTimeAgo(transaction.timestamp),
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // Amount & Symbol
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '${isPositive ? '+' : (isSend ? '-' : '')}$formattedAmount',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isPositive
                          ? theme.colorScheme.primary
                          : (transaction.status == 'failed'
                              ? theme.colorScheme.error
                              : theme.colorScheme.onSurface),
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'VRDX',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                      fontWeight: FontWeight.w500,
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

  IconData _getIcon() {
    if (isSend) return Icons.north_east_rounded; // ↑
    if (isReceive) return Icons.south_west_rounded; // ↓
    if (isSwap) return Icons.swap_horiz_rounded; // ⇄
    if (isStake) return Icons.lock_rounded; // 🔒
    return Icons.sync_alt_rounded;
  }

  Color _getIconColor(ThemeData theme) {
    if (isSend) return Colors.orangeAccent;
    if (isReceive) return theme.colorScheme.primary; // #00C853
    if (isStake) return Colors.amber;
    if (isSwap) return const Color(0xFF40C4FF);
    return theme.colorScheme.onSurface;
  }

  Color _getIconBgColor(ThemeData theme) {
    return _getIconColor(theme).withOpacity(0.15);
  }

  String _getTitle() {
    if (isSend) return 'Send';
    if (isReceive) return 'Receive';
    if (isSwap) return 'Swap';
    if (isStake) return 'Stake';
    return '${transaction.module}.${transaction.call}';
  }

  String _getCounterparty() {
    if (isSend) return transaction.to;
    if (isReceive) return transaction.from;
    return transaction.to.isNotEmpty ? transaction.to : transaction.from;
  }

  String _getFormattedAmount() {
    final val = transaction.amount / 1e18;
    if (val >= 1000) {
      return NumberFormat('#,##0.00').format(val);
    }
    return val.toStringAsFixed(2);
  }

  Widget _buildStatusDot(ThemeData theme) {
    Color dotColor;
    switch (transaction.status.toLowerCase()) {
      case 'confirmed':
        dotColor = theme.colorScheme.primary;
        break;
      case 'pending':
        dotColor = Colors.amber;
        break;
      case 'failed':
      default:
        dotColor = theme.colorScheme.error;
        break;
    }

    return Container(
      width: 7,
      height: 7,
      decoration: BoxDecoration(
        color: dotColor,
        shape: BoxShape.circle,
      ),
    );
  }

  String _formatTimeAgo(DateTime? timestamp) {
    if (timestamp == null) return 'recently';
    final diff = DateTime.now().difference(timestamp);

    if (diff.inSeconds < 60) {
      return 'just now';
    } else if (diff.inMinutes < 60) {
      return '${diff.inMinutes}m ago';
    } else if (diff.inHours < 24) {
      return '${diff.inHours}h ago';
    } else if (diff.inDays < 7) {
      return '${diff.inDays}d ago';
    } else {
      return DateFormat('MMM d').format(timestamp);
    }
  }
}
