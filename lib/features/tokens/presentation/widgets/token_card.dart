import 'package:flutter/material.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../../domain/token_repository.dart';

/// Card widget representing a single fungible token
class TokenCard extends StatelessWidget {

  const TokenCard({
    super.key,
    required this.token,
    this.onTap,
    this.onTransfer,
  });
  final TokenModel token;
  final VoidCallback? onTap;
  final VoidCallback? onTransfer;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isPositive = token.change24h >= 0;

    return VerdisCard(
      onTap: onTap,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      child: Row(
        children: [
          // Circular gradient token avatar
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: token.gradientColors.map((c) => Color(c)).toList(),
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              boxShadow: [
                BoxShadow(
                  color: Color(token.gradientColors.first).withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Center(
              child: Text(
                token.symbol.isNotEmpty ? token.symbol.substring(0, token.symbol.length > 3 ? 3 : token.symbol.length) : 'T',
                style: const TextStyle(
                  color: Colors.black,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ),
          ),
          const SizedBox(width: 14),

          // Name and Symbol
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    Flexible(
                      child: Text(
                        token.name,
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    if (token.isCustom) ...[
                      const SizedBox(width: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          'CUSTOM',
                          style: theme.textTheme.labelSmall?.copyWith(fontSize: 9),
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Text(
                      token.symbol,
                      style: theme.textTheme.bodySmall,
                    ),
                    const SizedBox(width: 8),
                    // 24h Change Chip
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: (isPositive
                                ? theme.colorScheme.primary
                                : theme.colorScheme.error)
                            .withOpacity(0.15),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            isPositive
                                ? Icons.arrow_drop_up
                                : Icons.arrow_drop_down,
                            size: 14,
                            color: isPositive
                                ? theme.colorScheme.primary
                                : theme.colorScheme.error,
                          ),
                          Text(
                            '${isPositive ? '+' : ''}${token.change24h.toStringAsFixed(2)}%',
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: isPositive
                                  ? theme.colorScheme.primary
                                  : theme.colorScheme.error,
                              fontWeight: FontWeight.bold,
                              fontSize: 10,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Balance & USD Value
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                _formatBalance(token.balance),
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                '\$${_formatUsd(token.usdValue)}',
                style: theme.textTheme.bodySmall,
              ),
            ],
          ),

          // Quick Transfer Action
          if (onTransfer != null) ...[
            const SizedBox(width: 8),
            IconButton(
              icon: Icon(
                Icons.send_rounded,
                size: 18,
                color: theme.colorScheme.primary,
              ),
              onPressed: onTransfer,
              tooltip: 'Transfer ${token.symbol}',
            ),
          ],
        ],
      ),
    );
  }

  String _formatBalance(double balance) {
    if (balance >= 1e6) {
      return '${(balance / 1e6).toStringAsFixed(2)}M';
    } else if (balance >= 1e3) {
      return '${(balance / 1e3).toStringAsFixed(2)}k';
    }
    return balance.toStringAsFixed(balance.truncateToDouble() == balance ? 0 : 2);
  }

  String _formatUsd(double value) {
    return value.toStringAsFixed(2);
  }
}
