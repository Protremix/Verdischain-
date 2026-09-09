import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dex_providers.dart';
import 'widgets/price_chart.dart';
import 'widgets/swap_settings.dart';
import 'widgets/transaction_preview.dart';

/// Swap Page for executing token swaps on Verdis AMM DEX
class SwapPage extends ConsumerStatefulWidget {
  const SwapPage({super.key});

  @override
  ConsumerState<SwapPage> createState() => _SwapPageState();
}

class _SwapPageState extends ConsumerState<SwapPage> {
  final TextEditingController _amountController = TextEditingController();
  bool _showChart = false;

  final List<String> _availableTokens = ['VRD', 'USDT', 'ETH', 'BTC', 'SOL', 'USDC'];

  @override
  void initState() {
    super.initState();
    _amountController.addListener(() {
      final val = double.tryParse(_amountController.text) ?? 0.0;
      ref.read(swapAmountInputProvider.notifier).state = val;
    });
  }

  @override
  void dispose() {
    _amountController.dispose();
    super.dispose();
  }

  void _switchDirection() {
    final tokenIn = ref.read(swapInputTokenProvider);
    final tokenOut = ref.read(swapOutputTokenProvider);

    ref.read(swapInputTokenProvider.notifier).state = tokenOut;
    ref.read(swapOutputTokenProvider.notifier).state = tokenIn;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final primary = theme.colorScheme.primary;

    final tokenIn = ref.watch(swapInputTokenProvider);
    final tokenOut = ref.watch(swapOutputTokenProvider);
    final preview = ref.watch(swapPreviewProvider);
    final slippage = ref.watch(slippageProvider);
    final selectedPool = ref.watch(selectedPoolProvider);

    final impactPct = (preview?.priceImpact ?? 0.0) * 100;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Chart toggle header bar
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Swap Tokens',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              Row(
                children: [
                  IconButton(
                    icon: Icon(_showChart ? Icons.show_chart : Icons.show_chart_outlined, color: primary),
                    tooltip: 'Toggle Price Chart',
                    onPressed: () {
                      setState(() {
                        _showChart = !_showChart;
                      });
                    },
                  ),
                  IconButton(
                    icon: const Icon(Icons.tune_rounded),
                    tooltip: 'Swap Settings',
                    onPressed: () => SwapSettingsSheet.show(context),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Collapsible Price Chart
          if (_showChart && selectedPool != null) ...[
            PriceChart(
              poolId: selectedPool.poolId,
              tokenPair: '${selectedPool.tokenA} / ${selectedPool.tokenB}',
            ),
            const SizedBox(height: 16),
          ],

          // Token A Input Card (Pay)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: theme.colorScheme.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: theme.colorScheme.outline),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('You Pay', style: theme.textTheme.bodySmall),
                    Row(
                      children: [
                        Text('Balance: 12,500.00 $tokenIn', style: theme.textTheme.labelSmall),
                        const SizedBox(width: 6),
                        GestureDetector(
                          onTap: () {
                            _amountController.text = '1000';
                          },
                          child: Text(
                            'MAX',
                            style: TextStyle(
                              color: primary,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _amountController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        style: theme.textTheme.headlineMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                        decoration: const InputDecoration(
                          hintText: '0.0',
                          border: InputBorder.none,
                          enabledBorder: InputBorder.none,
                          focusedBorder: InputBorder.none,
                          contentPadding: EdgeInsets.zero,
                          fillColor: Colors.transparent,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    _buildTokenDropdown(
                      context,
                      selected: tokenIn,
                      onChanged: (val) {
                        if (val != null) {
                          if (val == tokenOut) {
                            _switchDirection();
                          } else {
                            ref.read(swapInputTokenProvider.notifier).state = val;
                          }
                        }
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Switch Direction Button
          Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: InkWell(
                onTap: _switchDirection,
                borderRadius: BorderRadius.circular(24),
                child: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surface,
                    shape: BoxShape.circle,
                    border: Border.all(color: primary, width: 1.5),
                    boxShadow: [
                      BoxShadow(
                        color: primary.withOpacity(0.2),
                        blurRadius: 8,
                        spreadRadius: 1,
                      ),
                    ],
                  ),
                  child: Icon(Icons.swap_vert_rounded, color: primary, size: 24),
                ),
              ),
            ),
          ),

          // Token B Output Card (Receive)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: theme.colorScheme.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: theme.colorScheme.outline),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('You Receive (Estimated)', style: theme.textTheme.bodySmall),
                    Text('Balance: 4,820.50 $tokenOut', style: theme.textTheme.labelSmall),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        preview != null ? preview.expectedAmountOut.toStringAsFixed(4) : '0.0',
                        style: theme.textTheme.headlineMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: preview != null ? primary : theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    _buildTokenDropdown(
                      context,
                      selected: tokenOut,
                      onChanged: (val) {
                        if (val != null) {
                          if (val == tokenIn) {
                            _switchDirection();
                          } else {
                            ref.read(swapOutputTokenProvider.notifier).state = val;
                          }
                        }
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Price impact warning card
          if (impactPct > 1.0) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: (impactPct > 3.0 ? theme.colorScheme.error : Colors.orange)
                    .withOpacity(0.12),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: (impactPct > 3.0 ? theme.colorScheme.error : Colors.orange)
                      .withOpacity(0.4),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.warning_amber_rounded,
                    color: impactPct > 3.0 ? theme.colorScheme.error : Colors.orange,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      impactPct > 3.0
                          ? 'High Price Impact (${impactPct.toStringAsFixed(2)}%)! Expect significant value loss.'
                          : 'Moderate Price Impact (${impactPct.toStringAsFixed(2)}%).',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: impactPct > 3.0 ? theme.colorScheme.error : Colors.orange,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],

          // Details Drawer (Rate, Slippage, Fee, Route, Minimum Received)
          if (preview != null) ...[
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: theme.colorScheme.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: theme.colorScheme.outline),
              ),
              child: Column(
                children: [
                  _buildDetailRow(
                    context,
                    'Rate',
                    '1 $tokenIn = ${preview.priceRatio.toStringAsFixed(4)} $tokenOut',
                  ),
                  const SizedBox(height: 8),
                  _buildDetailRow(
                    context,
                    'Slippage Tolerance',
                    '${slippage.toStringAsFixed(1)}%',
                    onTap: () => SwapSettingsSheet.show(context),
                  ),
                  const SizedBox(height: 8),
                  _buildDetailRow(
                    context,
                    'Minimum Received',
                    '${preview.minAmountOut.toStringAsFixed(4)} $tokenOut',
                  ),
                  const SizedBox(height: 8),
                  _buildDetailRow(
                    context,
                    'Estimated Fee',
                    '${preview.fee.toStringAsFixed(4)} $tokenIn (0.3%)',
                  ),
                  const SizedBox(height: 8),
                  _buildDetailRow(
                    context,
                    'Route',
                    preview.route.join(' → '),
                    isHighlight: true,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
          ],

          // Swap Action Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: preview == null
                  ? null
                  : () {
                      final repo = ref.read(dexRepositoryProvider);
                      TransactionPreviewSheet.show(
                        context,
                        title: 'Confirm Swap',
                        swapPreview: preview,
                        onConfirm: () async {
                          return repo.swap(
                            poolId: selectedPool?.poolId ?? 1,
                            tokenIn: preview.tokenIn,
                            tokenOut: preview.tokenOut,
                            amountIn: preview.amountIn,
                            minAmountOut: preview.minAmountOut,
                            recipient: '5GrwvaEF5zXb26Fz9rcQpDWS5CTERHpNehXCPcNoHGKutQY',
                          );
                        },
                      );
                    },
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: primary,
                foregroundColor: Colors.black,
              ),
              child: Text(
                _amountController.text.isEmpty || double.tryParse(_amountController.text) == 0
                    ? 'Enter an amount'
                    : 'Preview Swap',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTokenDropdown(
    BuildContext context, {
    required String selected,
    required ValueChanged<String?> onChanged,
  }) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: theme.colorScheme.outline),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: selected,
          icon: const Icon(Icons.keyboard_arrow_down, size: 20),
          dropdownColor: theme.colorScheme.surface,
          items: _availableTokens.map((token) {
            return DropdownMenuItem<String>(
              value: token,
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircleAvatar(
                    radius: 10,
                    backgroundColor: theme.colorScheme.primary,
                    child: Text(
                      token.substring(0, 1),
                      style: const TextStyle(fontSize: 10, color: Colors.black, fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(token, style: const TextStyle(fontWeight: FontWeight.bold)),
                ],
              ),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }

  Widget _buildDetailRow(
    BuildContext context,
    String label,
    String value, {
    VoidCallback? onTap,
    bool isHighlight = false,
  }) {
    final theme = Theme.of(context);
    return InkWell(
      onTap: onTap,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Text(label, style: theme.textTheme.bodySmall),
              if (onTap != null) ...[
                const SizedBox(width: 4),
                Icon(Icons.edit, size: 12, color: theme.colorScheme.primary),
              ],
            ],
          ),
          Text(
            value,
            style: theme.textTheme.bodySmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: isHighlight ? theme.colorScheme.primary : theme.colorScheme.onSurface,
            ),
          ),
        ],
      ),
    );
  }
}
