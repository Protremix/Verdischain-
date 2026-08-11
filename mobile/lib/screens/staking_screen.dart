import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/wallet_service.dart';
import '../widgets/verdis_button.dart';

class StakingScreen extends StatefulWidget {
  const StakingScreen({super.key});

  @override
  State<StakingScreen> createState() => _StakingScreenState();
}

class _StakingScreenState extends State<StakingScreen> {
  final TextEditingController _amountController = TextEditingController();

  void _showStakeModal(BuildContext context, ValidatorInfo validator) {
    _amountController.clear();
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF0D1410),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        return Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
            top: 20,
            left: 20,
            right: 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Stake with ${validator.name}',
                style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(
                'Green Score: ${validator.greenScore}/100 • APY: ${validator.apy}%',
                style: const TextStyle(color: Color(0xFF16a34a), fontSize: 12),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _amountController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 16),
                decoration: const InputDecoration(
                  labelText: 'Stake Amount (VRDX)',
                  labelStyle: TextStyle(color: Color(0xFF94a3b8)),
                  filled: true,
                  fillColor: Color(0xFF040806),
                  enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF2E2E34))),
                  focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF16a34a))),
                ),
              ),
              const SizedBox(height: 20),
              Consumer<WalletService>(
                builder: (context, wallet, child) {
                  return VerdisButton(
                    label: 'Confirm Staking',
                    isLoading: wallet.isLoading,
                    onPressed: () async {
                      final amt = double.tryParse(_amountController.text.trim());
                      if (amt == null || amt <= 0) return;
                      final success = await wallet.stakeTokens(
                        validatorAddress: validator.address,
                        amount: amt,
                      );
                      if (ctx.mounted) Navigator.pop(ctx);
                      if (success) {
                        if (!context.mounted) return;
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Successfully staked $amt VRDX with ${validator.name}'),
                            backgroundColor: const Color(0xFF0D1410),
                          ),
                        );
                      }
                    },
                  );
                },
              ),
            ],
          ),
        );
      },
    );
  }

  void _showUnbondModal(BuildContext context, ValidatorInfo validator) {
    _amountController.clear();
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF0D1410),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        return Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
            top: 20,
            left: 20,
            right: 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Unbond from ${validator.name}',
                style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _amountController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 16),
                decoration: const InputDecoration(
                  labelText: 'Unbond Amount (VRDX)',
                  labelStyle: TextStyle(color: Color(0xFF94a3b8)),
                  filled: true,
                  fillColor: Color(0xFF040806),
                  enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF2E2E34))),
                  focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF16a34a))),
                ),
              ),
              const SizedBox(height: 20),
              Consumer<WalletService>(
                builder: (context, wallet, child) {
                  return VerdisButton(
                    label: 'Confirm Unbonding',
                    variant: VerdisButtonVariant.secondary,
                    isLoading: wallet.isLoading,
                    onPressed: () async {
                      final amt = double.tryParse(_amountController.text.trim());
                      if (amt == null || amt <= 0) return;
                      final success = await wallet.unbondTokens(
                        validatorAddress: validator.address,
                        amount: amt,
                      );
                      if (ctx.mounted) Navigator.pop(ctx);
                      if (success) {
                        if (!context.mounted) return;
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Unbonded $amt VRDX'),
                            backgroundColor: const Color(0xFF0D1410),
                          ),
                        );
                      }
                    },
                  );
                },
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final wallet = Provider.of<WalletService>(context);

    return Scaffold(
      backgroundColor: const Color(0xFF040806),
      appBar: AppBar(
        backgroundColor: const Color(0xFF040806),
        elevation: 0,
        title: const Text(
          'Eco Staking & Proof-of-Stake',
          style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 16, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFFFFFFFF)),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Summary card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF0D1410), Color(0xFF282830)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF2E2E34)),
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Total Staked', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12)),
                            const SizedBox(height: 4),
                            Text(
                              '${wallet.stakedAmount.toStringAsFixed(2)} VRDX',
                              style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 20, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            const Text('Staking Rewards', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12)),
                            const SizedBox(height: 4),
                            Text(
                              '+${wallet.stakingRewards.toStringAsFixed(2)} VRDX',
                              style: const TextStyle(color: Color(0xFF16a34a), fontSize: 20, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              const Text(
                'Green Validators',
                style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 15, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              const Text(
                'Select a green-certified validator node to stake your VRDX and earn rewards.',
                style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12),
              ),
              const SizedBox(height: 16),
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: wallet.validators.length,
                separatorBuilder: (_, __) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final val = wallet.validators[index];
                  return Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF0D1410),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFF2E2E34)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              val.name,
                              style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 14, fontWeight: FontWeight.w600),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: const Color(0xFF16a34a).withOpacity(0.15),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                '${val.apy}% APY',
                                style: const TextStyle(color: Color(0xFF16a34a), fontSize: 11, fontWeight: FontWeight.bold),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            const Text('Green Score: ', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 11)),
                            Text('${val.greenScore}/100', style: const TextStyle(color: Color(0xFF16a34a), fontSize: 11, fontWeight: FontWeight.bold)),
                            const SizedBox(width: 12),
                            Expanded(
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(4),
                                child: LinearProgressIndicator(
                                  value: val.greenScore / 100.0,
                                  backgroundColor: const Color(0xFF2E2E34),
                                  valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF16a34a)),
                                  minHeight: 6,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Staked: ${(val.totalStaked / 1000).toStringAsFixed(0)}k VRDX',
                              style: const TextStyle(color: Color(0xFF94a3b8), fontSize: 11),
                            ),
                            Row(
                              children: [
                                SizedBox(
                                  height: 32,
                                  child: ElevatedButton(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: const Color(0xFF16a34a),
                                      foregroundColor: const Color(0xFF040806),
                                      padding: const EdgeInsets.symmetric(horizontal: 12),
                                    ),
                                    onPressed: () => _showStakeModal(context, val),
                                    child: const Text('Stake', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                SizedBox(
                                  height: 32,
                                  child: OutlinedButton(
                                    style: OutlinedButton.styleFrom(
                                      side: const BorderSide(color: Color(0xFF2E2E34)),
                                      foregroundColor: const Color(0xFFFFFFFF),
                                      padding: const EdgeInsets.symmetric(horizontal: 12),
                                    ),
                                    onPressed: () => _showUnbondModal(context, val),
                                    child: const Text('Unbond', style: TextStyle(fontSize: 11)),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
