import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'staking_providers.dart';

class UnstakeDialog extends ConsumerStatefulWidget {

  const UnstakeDialog({
    super.key,
    required this.validatorName,
    required this.validatorAddress,
    this.currentStakedAmount = 2500,
  });
  final String validatorName;
  final String validatorAddress;
  final int currentStakedAmount;

  @override
  ConsumerState<UnstakeDialog> createState() => _UnstakeDialogState();
}

class _UnstakeDialogState extends ConsumerState<UnstakeDialog> {
  final _amountController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  final double _networkFee = 0.005;

  @override
  void dispose() {
    _amountController.dispose();
    super.dispose();
  }

  double get _enteredAmount {
    return double.tryParse(_amountController.text) ?? 0.0;
  }

  Future<void> _handleConfirm() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;

    setState(() => _isLoading = true);

    try {
      final repository = ref.read(stakingRepositoryProvider);
      final amountInt = _enteredAmount.toInt();

      await repository.unstake(
        validatorAddress: widget.validatorAddress,
        amount: amountInt,
      );

      ref.invalidate(stakingPositionsProvider);
      ref.invalidate(validatorsProvider);

      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Unstaking request submitted for $amountInt VRD.'),
            backgroundColor: Theme.of(context).colorScheme.primary,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Unstake failed: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Dialog(
      backgroundColor: theme.colorScheme.surface,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: SingleChildScrollView(
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Unstake VRD',
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close_rounded),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Target Position Info
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: theme.colorScheme.outline),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.output_rounded, color: theme.colorScheme.primary),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              widget.validatorName,
                              style: theme.textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              'Staked Position: ${widget.currentStakedAmount} VRD',
                              style: theme.textTheme.bodySmall,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // Amount Input Label & Max Button
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Amount to Unstake',
                      style: theme.textTheme.labelMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'Max: ${widget.currentStakedAmount} VRD',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.primary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),

                TextFormField(
                  controller: _amountController,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration(
                    hintText: '0.00',
                    prefixIcon: const Icon(Icons.token_rounded),
                    suffixIcon: TextButton(
                      onPressed: () {
                        setState(() {
                          _amountController.text = widget.currentStakedAmount.toString();
                        });
                      },
                      child: const Text('MAX'),
                    ),
                  ),
                  onChanged: (_) => setState(() {}),
                  validator: (val) {
                    if (val == null || val.isEmpty) return 'Enter amount';
                    final d = double.tryParse(val);
                    if (d == null || d <= 0) return 'Enter valid amount';
                    if (d > widget.currentStakedAmount) return 'Exceeds staked amount';
                    return null;
                  },
                ),

                const SizedBox(height: 16),

                // Unlocking Period Warning Box
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFF9800).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFFFF9800).withOpacity(0.4)),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.info_outline_rounded, color: Color(0xFFFF9800), size: 20),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '7-Day Unbonding Period',
                              style: theme.textTheme.labelMedium?.copyWith(
                                color: const Color(0xFFFF9800),
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'Unstaked VRD tokens enter a 7-day unbonding lockup. During this period, tokens do not generate rewards.',
                              style: theme.textTheme.bodySmall,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Network Fee', style: theme.textTheme.bodySmall),
                    Text('$_networkFee VRD', style: theme.textTheme.bodySmall),
                  ],
                ),

                const SizedBox(height: 20),

                VerdisButton(
                  label: 'Confirm Unstake',
                  isLoading: _isLoading,
                  icon: Icons.lock_open_rounded,
                  onPressed: _enteredAmount > 0 ? _handleConfirm : null,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
