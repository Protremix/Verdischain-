import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import 'package:verdis_wallet/core/config/network_config.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'transactions_providers.dart';
import 'utils/address_validator.dart';

/// Confirmation screen presenting transfer breakdown prior to RPC dispatch.
class ConfirmationPage extends ConsumerWidget {

  const ConfirmationPage({
    super.key,
    required this.recipient,
    required this.amount,
    required this.feeSpeed,
  });
  final String recipient;
  final double amount;
  final String feeSpeed;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final fromAddress = ref.watch(userWalletAddressProvider);
    final sendState = ref.watch(sendTransactionProvider);

    final feeAsync = ref.watch(feeEstimateProvider({
      'recipient': recipient,
      'amount': amount,
      'speed': feeSpeed,
    }),);

    final fee = feeAsync.valueOrNull ?? 0.0012;
    final total = amount + fee;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Confirm Transaction'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: sendState.isSuccess
              ? _buildSuccessView(context, ref, sendState)
              : sendState.errorMessage != null
                  ? _buildFailureView(context, ref, sendState)
                  : Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Amount Header Banner
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            color: theme.colorScheme.surfaceContainerHighest,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(
                              color: theme.colorScheme.primary.withOpacity(0.3),
                            ),
                          ),
                          child: Column(
                            children: [
                              Text(
                                'Send Amount',
                                style: theme.textTheme.labelMedium?.copyWith(
                                  color: theme.colorScheme.onSurfaceVariant,
                                ),
                              ),
                              const SizedBox(height: 6),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                crossAxisAlignment: CrossAxisAlignment.center,
                                textBaseline: TextBaseline.alphabetic,
                                children: [
                                  Text(
                                    amount.toStringAsFixed(4),
                                    style: theme.textTheme.displayMedium?.copyWith(
                                      fontWeight: FontWeight.bold,
                                      color: theme.colorScheme.primary,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    'VRDX',
                                    style: theme.textTheme.headlineSmall?.copyWith(
                                      color: theme.colorScheme.primary,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 24),

                        // Transaction Summary Card
                        VerdisCard(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            children: [
                              _buildSummaryRow(
                                context,
                                label: 'From (Your Address)',
                                value: AddressValidator.formatAddress(fromAddress),
                                isMonospace: true,
                              ),
                              const Divider(height: 24),
                              _buildSummaryRow(
                                context,
                                label: 'To (Recipient)',
                                value: AddressValidator.formatAddress(recipient),
                                isMonospace: true,
                              ),
                              const Divider(height: 24),
                              _buildSummaryRow(
                                context,
                                label: 'Speed Priority',
                                value: feeSpeed.toUpperCase(),
                              ),
                              const Divider(height: 24),
                              _buildSummaryRow(
                                context,
                                label: 'Estimated Fee',
                                value: '${fee.toStringAsFixed(4)} VRDX',
                                valueColor: theme.colorScheme.primary,
                              ),
                              const Divider(height: 24),
                              _buildSummaryRow(
                                context,
                                label: 'Total Deduction',
                                value: '${total.toStringAsFixed(4)} VRDX',
                                isBold: true,
                              ),
                            ],
                          ),
                        ),

                        const Spacer(),

                        // Submit Button
                        VerdisButton(
                          label: sendState.isSubmitting ? 'Submitting...' : 'Confirm & Submit',
                          isLoading: sendState.isSubmitting,
                          icon: Icons.send_rounded,
                          onPressed: sendState.isSubmitting
                              ? null
                              : () async {
                                  await ref
                                      .read(sendTransactionProvider.notifier)
                                      .sendTransfer(
                                        recipient: recipient,
                                        amount: amount,
                                        speed: feeSpeed,
                                      );
                                },
                        ),
                      ],
                    ),
        ),
      ),
    );
  }

  Widget _buildSummaryRow(
    BuildContext context, {
    required String label,
    required String value,
    Color? valueColor,
    bool isBold = false,
    bool isMonospace = false,
  }) {
    final theme = Theme.of(context);
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        Text(
          value,
          style: theme.textTheme.bodyMedium?.copyWith(
            color: valueColor ?? theme.colorScheme.onSurface,
            fontWeight: isBold ? FontWeight.bold : FontWeight.w500,
            fontFamily: isMonospace ? 'monospace' : null,
          ),
        ),
      ],
    );
  }

  Widget _buildSuccessView(
      BuildContext context, WidgetRef ref, SendTransactionState state,) {
    final theme = Theme.of(context);

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Spacer(),
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: theme.colorScheme.primary.withOpacity(0.15),
            shape: BoxShape.circle,
          ),
          child: Icon(
            Icons.check_circle_rounded,
            size: 64,
            color: theme.colorScheme.primary,
          ),
        ),
        const SizedBox(height: 20),
        Text(
          'Transaction Submitted!',
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Your transfer of $amount VRDX has been broadcast to the Verdis network.',
          textAlign: TextAlign.center,
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 24),

        // Tx Hash Box
        VerdisCard(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Transaction Hash',
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.copy, size: 16),
                    onPressed: () {
                      if (state.txHash != null) {
                        Clipboard.setData(ClipboardData(text: state.txHash!));
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Transaction hash copied')),
                        );
                      }
                    },
                  ),
                ],
              ),
              const SizedBox(height: 4),
              SelectableText(
                state.txHash ?? '',
                style: theme.textTheme.bodySmall?.copyWith(
                  fontFamily: 'monospace',
                  color: theme.colorScheme.primary,
                ),
              ),
              if (state.blockNumber != null) ...[
                const Divider(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Included in Block', style: theme.textTheme.bodySmall),
                    Text('#${state.blockNumber}',
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),),
                  ],
                ),
              ],
            ],
          ),
        ),

        const Spacer(),

        // Action Buttons
        VerdisButton(
          label: 'View in Explorer',
          isOutlined: true,
          icon: Icons.open_in_new,
          onPressed: () async {
            final url = Uri.parse(
                '${NetworkConfig.explorerUrl}/tx/${state.txHash}',);
            if (await canLaunchUrl(url)) {
              await launchUrl(url);
            }
          },
        ),
        const SizedBox(height: 12),
        VerdisButton(
          label: 'Done',
          icon: Icons.done_all,
          onPressed: () {
            ref.read(sendTransactionProvider.notifier).reset();
            Navigator.of(context).popUntil((route) => route.isFirst);
          },
        ),
      ],
    );
  }

  Widget _buildFailureView(
      BuildContext context, WidgetRef ref, SendTransactionState state,) {
    final theme = Theme.of(context);

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Spacer(),
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: theme.colorScheme.error.withOpacity(0.15),
            shape: BoxShape.circle,
          ),
          child: Icon(
            Icons.error_outline_rounded,
            size: 64,
            color: theme.colorScheme.error,
          ),
        ),
        const SizedBox(height: 20),
        Text(
          'Transaction Failed',
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: theme.colorScheme.error,
          ),
        ),
        const SizedBox(height: 12),
        VerdisCard(
          padding: const EdgeInsets.all(16),
          child: Text(
            state.errorMessage ?? 'An unknown RPC network error occurred.',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurface,
            ),
            textAlign: TextAlign.center,
          ),
        ),
        const Spacer(),
        VerdisButton(
          label: 'Retry Transaction',
          icon: Icons.refresh,
          onPressed: () {
            ref.read(sendTransactionProvider.notifier).sendTransfer(
                  recipient: recipient,
                  amount: amount,
                  speed: feeSpeed,
                );
          },
        ),
        const SizedBox(height: 12),
        VerdisButton(
          label: 'Cancel',
          isOutlined: true,
          icon: Icons.close,
          onPressed: () {
            ref.read(sendTransactionProvider.notifier).reset();
            Navigator.of(context).pop();
          },
        ),
      ],
    );
  }
}
