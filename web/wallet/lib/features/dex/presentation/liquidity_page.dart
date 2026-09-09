import 'package:verdis_wallet/features/dex/domain/dex_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'dex_providers.dart';
import 'widgets/transaction_preview.dart';

/// Liquidity Page providing Add Liquidity and Remove Liquidity tabs
class LiquidityPage extends ConsumerStatefulWidget {
  const LiquidityPage({super.key});

  @override
  ConsumerState<LiquidityPage> createState() => _LiquidityPageState();
}

class _LiquidityPageState extends ConsumerState<LiquidityPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _amountAController = TextEditingController();
  final TextEditingController _amountBController = TextEditingController();

  double _removeLpPercent = 50.0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);

    _amountAController.addListener(() {
      final val = double.tryParse(_amountAController.text) ?? 0.0;
      ref.read(liquidityAmountAProvider.notifier).state = val;

      final pool = ref.read(selectedPoolProvider);
      if (pool != null && pool.reserveA > 0) {
        final calculatedB = (val * pool.reserveB) / pool.reserveA;
        if (_amountBController.text != calculatedB.toStringAsFixed(4)) {
          _amountBController.text = calculatedB > 0 ? calculatedB.toStringAsFixed(4) : '';
        }
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _amountAController.dispose();
    _amountBController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final primary = theme.colorScheme.primary;

    final poolsAsync = ref.watch(poolsProvider);
    final selectedPool = ref.watch(selectedPoolProvider);
    final preview = ref.watch(liquidityPreviewProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Tab Switcher (Add Liquidity | Remove Liquidity)
          Container(
            decoration: BoxDecoration(
              color: theme.colorScheme.surface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: theme.colorScheme.outline),
            ),
            child: TabBar(
              controller: _tabController,
              indicator: BoxDecoration(
                color: primary,
                borderRadius: BorderRadius.circular(10),
              ),
              labelColor: Colors.black,
              unselectedLabelColor: theme.colorScheme.onSurface,
              labelStyle: const TextStyle(fontWeight: FontWeight.bold),
              tabs: const [
                Tab(text: 'Add Liquidity'),
                Tab(text: 'Remove Liquidity'),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Pool Selector Dropdown
          poolsAsync.when(
            data: (pools) {
              if (pools.isEmpty) return const SizedBox.shrink();

              final current = selectedPool ?? pools.first;

              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: theme.colorScheme.outline),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Select Pool:', style: theme.textTheme.bodyMedium),
                    DropdownButtonHideUnderline(
                      child: DropdownButton<DexPool>(
                        value: current,
                        dropdownColor: theme.colorScheme.surface,
                        items: pools.map((p) {
                          return DropdownMenuItem<DexPool>(
                            value: p,
                            child: Text(
                              '${p.tokenA} / ${p.tokenB}',
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                          );
                        }).toList(),
                        onChanged: (p) {
                          if (p != null) {
                            ref.read(selectedPoolProvider.notifier).state = p;
                            _amountAController.clear();
                            _amountBController.clear();
                          }
                        },
                      ),
                    ),
                  ],
                ),
              );
            },
            loading: () => const ShimmerPlaceholder(height: 56),
            error: (_, __) => const SizedBox.shrink(),
          ),

          const SizedBox(height: 16),

          // Animated Tab Views
          SizedBox(
            height: 480,
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildAddLiquidityView(context, theme, selectedPool, preview, primary),
                _buildRemoveLiquidityView(context, theme, selectedPool, primary),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAddLiquidityView(
    BuildContext context,
    ThemeData theme,
    DexPool? pool,
    LiquidityPreview? preview,
    Color primary,
  ) {
    if (pool == null) return const SizedBox.shrink();

    return Column(
      children: [
        // Token A Input Card
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
                  Text('Deposit ${pool.tokenA}', style: theme.textTheme.bodySmall),
                  Text('Balance: 10,000 ${pool.tokenA}', style: theme.textTheme.labelSmall),
                ],
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _amountAController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
                decoration: InputDecoration(
                  hintText: '0.0',
                  suffixIcon: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Text(pool.tokenA, style: const TextStyle(fontWeight: FontWeight.bold)),
                  ),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 12),
        const Icon(Icons.add, size: 24, color: Colors.grey),
        const SizedBox(height: 12),

        // Token B Input Card
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
                  Text('Deposit ${pool.tokenB}', style: theme.textTheme.bodySmall),
                  Text('Balance: 5,000 ${pool.tokenB}', style: theme.textTheme.labelSmall),
                ],
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _amountBController,
                readOnly: true,
                style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
                decoration: InputDecoration(
                  hintText: '0.0',
                  suffixIcon: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Text(pool.tokenB, style: const TextStyle(fontWeight: FontWeight.bold)),
                  ),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Pool position info
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: theme.colorScheme.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: theme.colorScheme.outline),
          ),
          child: Column(
            children: [
              _buildInfoRow('Current Pool Reserves', '${pool.reserveA} ${pool.tokenA} / ${pool.reserveB} ${pool.tokenB}', theme),
              const SizedBox(height: 8),
              _buildInfoRow('Pool Share After Deposit', '${(preview?.poolSharePercent ?? 0.0).toStringAsFixed(4)}%', theme, isPrimary: true),
              const SizedBox(height: 8),
              _buildInfoRow('Est. LP Tokens Received', (preview?.lpTokens ?? 0.0).toStringAsFixed(4), theme),
            ],
          ),
        ),

        const SizedBox(height: 20),

        // Action Button
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: preview == null
                ? null
                : () {
                    final repo = ref.read(dexRepositoryProvider);
                    TransactionPreviewSheet.show(
                      context,
                      title: 'Add Liquidity',
                      liquidityPreview: preview,
                      onConfirm: () async {
                        return repo.addLiquidity(
                          poolId: pool.poolId,
                          amountA: preview.amountA,
                          amountB: preview.amountB,
                          minAmountA: preview.amountA * 0.99,
                          minAmountB: preview.amountB * 0.99,
                        );
                      },
                    );
                  },
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
              backgroundColor: primary,
              foregroundColor: Colors.black,
            ),
            child: const Text('Supply Liquidity', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ),
        ),
      ],
    );
  }

  Widget _buildRemoveLiquidityView(
    BuildContext context,
    ThemeData theme,
    DexPool? pool,
    Color primary,
  ) {
    if (pool == null) return const SizedBox.shrink();

    // Mock total LP tokens held by user
    const double totalUserLp = 1200.0;
    final double lpToRemove = (totalUserLp * _removeLpPercent) / 100.0;

    final double tokenAReceived = (lpToRemove / totalUserLp) * (pool.reserveA * 0.05);
    final double tokenBReceived = (lpToRemove / totalUserLp) * (pool.reserveB * 0.05);

    return Column(
      children: [
        // LP Token Balance Box
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
                  Text('Your LP Token Balance', style: theme.textTheme.bodySmall),
                  Text('${totalUserLp.toStringAsFixed(2)} LP', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Amount to Remove', style: theme.textTheme.bodyMedium),
                  Text('${_removeLpPercent.toInt()}%', style: theme.textTheme.headlineMedium?.copyWith(color: primary, fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 12),
              Slider(
                value: _removeLpPercent,
                min: 0.0,
                max: 100.0,
                divisions: 20,
                activeColor: primary,
                label: '${_removeLpPercent.toInt()}%',
                onChanged: (val) {
                  setState(() {
                    _removeLpPercent = val;
                  });
                },
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [25, 50, 75, 100].map((pct) {
                  return ChoiceChip(
                    label: Text('$pct%'),
                    selected: _removeLpPercent == pct.toDouble(),
                    onSelected: (_) {
                      setState(() {
                        _removeLpPercent = pct.toDouble();
                      });
                    },
                    selectedColor: primary,
                  );
                }).toList(),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Tokens Received Summary
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
              Text('You Will Receive', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              _buildInfoRow('Receive ${pool.tokenA}', '${tokenAReceived.toStringAsFixed(4)} ${pool.tokenA}', theme, isPrimary: true),
              const SizedBox(height: 8),
              _buildInfoRow('Receive ${pool.tokenB}', '${tokenBReceived.toStringAsFixed(4)} ${pool.tokenB}', theme, isPrimary: true),
            ],
          ),
        ),

        const SizedBox(height: 24),

        // Action Button
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: _removeLpPercent <= 0
                ? null
                : () {
                    final repo = ref.read(dexRepositoryProvider);
                    TransactionPreviewSheet.show(
                      context,
                      title: 'Remove Liquidity',
                      liquidityPreview: LiquidityPreview(
                        poolId: pool.poolId,
                        tokenA: pool.tokenA,
                        tokenB: pool.tokenB,
                        amountA: tokenAReceived,
                        amountB: tokenBReceived,
                        lpTokens: lpToRemove,
                        poolSharePercent: 0.0,
                        reserveAAfter: pool.reserveA - tokenAReceived,
                        reserveBAfter: pool.reserveB - tokenBReceived,
                        fee: 0.0,
                      ),
                      onConfirm: () async {
                        return repo.removeLiquidity(
                          poolId: pool.poolId,
                          lpAmount: lpToRemove,
                          minAmountA: tokenAReceived * 0.99,
                          minAmountB: tokenBReceived * 0.99,
                        );
                      },
                    );
                  },
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
              backgroundColor: theme.colorScheme.error,
              foregroundColor: Colors.white,
            ),
            child: const Text('Remove Liquidity', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ),
        ),
      ],
    );
  }

  Widget _buildInfoRow(String label, String value, ThemeData theme, {bool isPrimary = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: theme.textTheme.bodySmall),
        Text(
          value,
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: isPrimary ? theme.colorScheme.primary : theme.colorScheme.onSurface,
          ),
        ),
      ],
    );
  }
}
