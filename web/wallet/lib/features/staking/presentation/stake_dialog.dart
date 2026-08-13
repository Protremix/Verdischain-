import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'staking_providers.dart';

class StakeDialog extends ConsumerStatefulWidget {

  const StakeDialog({
    super.key,
    required this.validator,
  });
  final ValidatorInfo validator;

  @override
  ConsumerState<StakeDialog> createState() => _StakeDialogState();
}

class _StakeDialogState extends ConsumerState<StakeDialog> {
  final _amountController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  final double _userBalance = 5000.0; // Available balance in VRD
  final double _networkFee = 0.005; // VRD fee
  final double _baseApy = 12.5; // Base APY %

  @override
  void dispose() {
    _amountController.dispose();
    super.dispose();
  }

  double get _enteredAmount {
    return double.tryParse(_amountController.text) ?? 0.0;
  }

  // APY includes green score bonus: max +2.5% for 100 green score
  double get _effectiveApy {
    final greenBonus = (widget.validator.greenScore / 100.0) * 2.5;
    return _baseApy + greenBonus;
  }

  double get _dailyReward {
    return (_enteredAmount * (_effectiveApy / 100.0)) / 365.0;
  }

  double get _yearlyReward {
    return _enteredAmount * (_effectiveApy / 100.0);
  }

  Future<void> _handleConfirm() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;

    setState(() => _isLoading = true);

    try {
      final repository = ref.read(stakingRepositoryProvider);
      final amountInt = _enteredAmount.toInt();

      await repository.stake(
        validatorAddress: widget.validator.address,
        amount: amountInt,
      );

      // Refresh positions & validator lists
      ref.invalidate(stakingPositionsProvider);
      ref.invalidate(validatorsProvider);
      ref.invalidate(rewardsProvider);

      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Successfully staked $amountInt VRD with ${widget.validator.name}!'),
            backgroundColor: Theme.of(context).colorScheme.primary,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Staking failed: $e'),
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
                      'Stake VRD',
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

                // Validator Target Info Card
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: theme.colorScheme.outline),
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: theme.colorScheme.primary.withOpacity(0.15),
                        ),
                        child: Icon(Icons.shield_outlined, color: theme.colorScheme.primary),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              widget.validator.name,
                              style: theme.textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'Green Score: ${widget.validator.greenScore}/100 • Energy: ${widget.validator.energySource}',
                              style: theme.textTheme.bodySmall,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // Available Balance Info
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Amount to Stake',
                      style: theme.textTheme.labelMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'Available: ${_userBalance.toStringAsFixed(2)} VRD',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.primary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),

                // Amount Input Field with MAX Button
                TextFormField(
                  controller: _amountController,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration(
                    hintText: '0.00',
                    suffixIcon: TextButton(
                      onPressed: () {
                        setState(() {
                          final maxAmount = _userBalance - _networkFee;
                          _amountController.text = (maxAmount > 0 ? maxAmount : 0).toStringAsFixed(0);
                        });
                      },
                      child: const Text('MAX'),
                    ),
                    prefixIcon: const Icon(Icons.token_rounded),
                  ),
                  onChanged: (_) => setState(() {}),
                  validator: (val) {
                    if (val == null || val.isEmpty) return 'Enter amount';
                    final d = double.tryParse(val);
                    if (d == null || d <= 0) return 'Enter valid amount';
                    if (d > _userBalance - _networkFee) return 'Exceeds available balance';
                    return null;
                  },
                ),

                const SizedBox(height: 16),

                // Expected Rewards Calculation Box
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primary.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: theme.colorScheme.primary.withOpacity(0.3)),
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.bolt_rounded, size: 18, color: theme.colorScheme.primary),
                              const SizedBox(width: 6),
                              Text('Effective APY', style: theme.textTheme.bodyMedium),
                            ],
                          ),
                          Text(
                            '${_effectiveApy.toStringAsFixed(2)}%',
                            style: theme.textTheme.titleMedium?.copyWith(
                              color: theme.colorScheme.primary,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const Divider(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Est. Daily Rewards:', style: theme.textTheme.bodySmall),
                          Text(
                            '+${_dailyReward.toStringAsFixed(4)} VRD',
                            style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Est. Yearly Rewards:', style: theme.textTheme.bodySmall),
                          Text(
                            '+${_yearlyReward.toStringAsFixed(2)} VRD',
                            style: theme.textTheme.bodyMedium?.copyWith(
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

                // Network Fee Breakdown
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Network Fee', style: theme.textTheme.bodySmall),
                    Text('$_networkFee VRD', style: theme.textTheme.bodySmall),
                  ],
                ),

                const SizedBox(height: 20),

                // Confirm Button
                VerdisButton(
                  label: 'Confirm Staking',
                  isLoading: _isLoading,
                  icon: Icons.lock_outline_rounded,
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
