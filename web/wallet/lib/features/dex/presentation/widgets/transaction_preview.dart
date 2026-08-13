import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/dex_repository.dart';

/// Modal dialog or bottom sheet for reviewing and confirming DEX transactions
class TransactionPreviewSheet extends ConsumerStatefulWidget {

  const TransactionPreviewSheet({
    super.key,
    required this.title,
    this.swapPreview,
    this.liquidityPreview,
    required this.onConfirm,
  });
  final String title;
  final SwapPreview? swapPreview;
  final LiquidityPreview? liquidityPreview;
  final Future<String> Function() onConfirm;

  static Future<void> show(
    BuildContext context, {
    required String title,
    SwapPreview? swapPreview,
    LiquidityPreview? liquidityPreview,
    required Future<String> Function() onConfirm,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => TransactionPreviewSheet(
        title: title,
        swapPreview: swapPreview,
        liquidityPreview: liquidityPreview,
        onConfirm: onConfirm,
      ),
    );
  }

  @override
  ConsumerState<TransactionPreviewSheet> createState() => _TransactionPreviewSheetState();
}

class _TransactionPreviewSheetState extends ConsumerState<TransactionPreviewSheet> {
  bool _isLoading = false;
  String? _txHash;
  String? _errorMessage;

  Future<void> _handleConfirm() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final hash = await widget.onConfirm();
      setState(() {
        _isLoading = false;
        _txHash = hash;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final primary = theme.colorScheme.primary;

    if (_txHash != null) {
      return _buildSuccessView(context, theme);
    }

    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Drag indicator
          Center(
            child: Container(
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: theme.colorScheme.onSurfaceVariant.withOpacity(0.3),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Title
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                widget.title,
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.close),
                onPressed: () => Navigator.of(context).pop(),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Content body depending on Swap or Liquidity
          if (widget.swapPreview != null)
            _buildSwapContent(widget.swapPreview!, theme)
          else if (widget.liquidityPreview != null)
            _buildLiquidityContent(widget.liquidityPreview!, theme),

          const SizedBox(height: 16),

          if (_errorMessage != null) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: theme.colorScheme.error.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                _errorMessage!,
                style: TextStyle(color: theme.colorScheme.error, fontSize: 13),
              ),
            ),
            const SizedBox(height: 16),
          ],

          // Action Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _handleConfirm,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: primary,
                foregroundColor: Colors.black,
              ),
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
                    )
                  : const Text(
                      'Confirm Transaction',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSwapContent(SwapPreview preview, ThemeData theme) {
    final impactPct = preview.priceImpact * 100;
    Color impactColor = theme.colorScheme.primary;
    if (impactPct > 3.0) {
      impactColor = theme.colorScheme.error;
    } else if (impactPct > 1.0) {
      impactColor = Colors.orange;
    }

    return Column(
      children: [
        // Main Input/Output Exchange Summary
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('You Pay', style: theme.textTheme.bodySmall),
                  Text(
                    '${preview.amountIn.toStringAsFixed(4)} ${preview.tokenIn}',
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 8),
                child: Icon(Icons.arrow_downward, size: 20, color: Colors.grey),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('You Receive (est.)', style: theme.textTheme.bodySmall),
                  Text(
                    '${preview.expectedAmountOut.toStringAsFixed(4)} ${preview.tokenOut}',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Details list
        _buildRow('Exchange Rate', '1 ${preview.tokenIn} ≈ ${preview.priceRatio.toStringAsFixed(4)} ${preview.tokenOut}', theme),
        _buildRow('Minimum Received', '${preview.minAmountOut.toStringAsFixed(4)} ${preview.tokenOut}', theme),
        _buildRow('Price Impact', '${impactPct.toStringAsFixed(2)}%', theme, valueColor: impactColor),
        _buildRow('Liquidity Fee', '${preview.fee.toStringAsFixed(4)} ${preview.tokenIn}', theme),
        _buildRow('Route', preview.route.join(' → '), theme),
      ],
    );
  }

  Widget _buildLiquidityContent(LiquidityPreview preview, ThemeData theme) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Deposit ${preview.tokenA}', style: theme.textTheme.bodySmall),
                  Text(
                    '${preview.amountA.toStringAsFixed(4)} ${preview.tokenA}',
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Deposit ${preview.tokenB}', style: theme.textTheme.bodySmall),
                  Text(
                    '${preview.amountB.toStringAsFixed(4)} ${preview.tokenB}',
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        _buildRow('LP Tokens Minted', preview.lpTokens.toStringAsFixed(4), theme),
        _buildRow('Pool Share', '${preview.poolSharePercent.toStringAsFixed(4)}%', theme),
        _buildRow('Updated Pool Reserves', '${preview.reserveAAfter.toStringAsFixed(0)} ${preview.tokenA} / ${preview.reserveBAfter.toStringAsFixed(0)} ${preview.tokenB}', theme),
      ],
    );
  }

  Widget _buildRow(String label, String value, ThemeData theme, {Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: theme.textTheme.bodySmall),
          Flexible(
            child: Text(
              value,
              style: theme.textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: valueColor ?? theme.colorScheme.onSurface,
              ),
              textAlign: TextAlign.end,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuccessView(BuildContext context, ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          CircleAvatar(
            radius: 36,
            backgroundColor: theme.colorScheme.primary.withOpacity(0.15),
            child: Icon(Icons.check_circle, size: 48, color: theme.colorScheme.primary),
          ),
          const SizedBox(height: 16),
          Text(
            'Transaction Submitted!',
            style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            'Your extrinsic has been broadcast to the Verdis network.',
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium,
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: theme.colorScheme.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    _txHash!,
                    style: theme.textTheme.labelSmall?.copyWith(fontFamily: 'monospace'),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.copy, size: 16),
                  onPressed: () {},
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Done'),
            ),
          ),
        ],
      ),
    );
  }
}
