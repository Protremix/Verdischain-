import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'confirmation_page.dart';
import 'qr_scanner_page.dart';
import 'transactions_providers.dart';
import 'utils/address_validator.dart';
import 'widgets/fee_estimate.dart';

/// Send Page screen for initiating transfers on Verdis Network
class SendPage extends ConsumerStatefulWidget {

  const SendPage({
    super.key,
    this.initialRecipient,
    this.initialAmount,
  });
  final String? initialRecipient;
  final double? initialAmount;

  @override
  ConsumerState<SendPage> createState() => _SendPageState();
}

class _SendPageState extends ConsumerState<SendPage> {
  late final TextEditingController _recipientController;
  late final TextEditingController _amountController;
  final _formKey = GlobalKey<FormState>();

  String? _addressError;

  @override
  void initState() {
    super.initState();
    _recipientController =
        TextEditingController(text: widget.initialRecipient ?? '');
    _amountController = TextEditingController(
        text: widget.initialAmount != null ? widget.initialAmount.toString() : '',);
  }

  @override
  void dispose() {
    _recipientController.dispose();
    _amountController.dispose();
    super.dispose();
  }

  void _onScanQr() async {
    final scannedResult = await Navigator.push<String>(
      context,
      MaterialPageRoute(builder: (context) => const QrScannerPage()),
    );

    if (scannedResult != null && scannedResult.isNotEmpty) {
      setState(() {
        _recipientController.text = scannedResult;
        _addressError = AddressValidator.getValidationError(scannedResult);
      });
    }
  }

  void _onPasteRecipient() async {
    final clipboardData = await Clipboard.getData('text/plain');
    if (clipboardData != null && clipboardData.text != null) {
      final text = clipboardData.text!.trim();
      setState(() {
        _recipientController.text = text;
        _addressError = AddressValidator.getValidationError(text);
      });
    }
  }

  void _onSetMaxAmount(double availableBalance, double estimatedFee) {
    final maxAmount = (availableBalance - estimatedFee).clamp(0.0, availableBalance);
    setState(() {
      _amountController.text = maxAmount.toStringAsFixed(4);
    });
  }

  void _onSubmitSend() {
    final recipient = _recipientController.text.trim();
    final amountText = _amountController.text.trim();
    final amount = double.tryParse(amountText) ?? 0.0;
    final balance = ref.read(userWalletBalanceProvider);

    final error = AddressValidator.getValidationError(recipient);
    if (error != null) {
      setState(() {
        _addressError = error;
      });
      return;
    }

    if (amount <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a valid amount greater than 0')),
      );
      return;
    }

    if (amount > balance) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Amount exceeds available balance (${balance.toStringAsFixed(2)} VRDX)')),
      );
      return;
    }

    final speed = ref.read(selectedFeeSpeedProvider);

    // Show Confirmation dialog or navigate to ConfirmationPage
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ConfirmationPage(
          recipient: recipient,
          amount: amount,
          feeSpeed: speed,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final balance = ref.watch(userWalletBalanceProvider);
    final selectedSpeed = ref.watch(selectedFeeSpeedProvider);

    final currentAmount = double.tryParse(_amountController.text) ?? 0.0;
    final feeAsync = ref.watch(feeEstimateProvider({
      'recipient': _recipientController.text,
      'amount': currentAmount,
      'speed': selectedSpeed,
    }),);
    final fee = feeAsync.valueOrNull ?? 0.0012;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Send VRDX'),
        actions: [
          IconButton(
            icon: const Icon(Icons.qr_code_scanner),
            tooltip: 'Scan QR',
            onPressed: _onScanQr,
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Balance Banner Card
                VerdisCard(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Available Balance',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${balance.toStringAsFixed(2)} VRDX',
                            style: theme.textTheme.headlineSmall?.copyWith(
                              color: theme.colorScheme.primary,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      Icon(
                        Icons.account_balance_wallet_rounded,
                        color: theme.colorScheme.primary,
                        size: 32,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Recipient Address Input
                Text(
                  'Recipient Address',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _recipientController,
                  onChanged: (val) {
                    setState(() {
                      _addressError = AddressValidator.getValidationError(val);
                    });
                  },
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
                  decoration: InputDecoration(
                    hintText: 'Enter Verdis SS58 address',
                    errorText: _addressError,
                    suffixIcon: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.paste_rounded, size: 20),
                          tooltip: 'Paste from clipboard',
                          onPressed: _onPasteRecipient,
                        ),
                        IconButton(
                          icon: const Icon(Icons.qr_code_scanner_rounded, size: 20),
                          tooltip: 'Scan QR Code',
                          onPressed: _onScanQr,
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // Amount Input
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Amount',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    TextButton(
                      onPressed: () => _onSetMaxAmount(balance, fee),
                      style: TextButton.styleFrom(
                        padding: EdgeInsets.zero,
                        minimumSize: const Size(40, 24),
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      child: Text(
                        'MAX',
                        style: TextStyle(
                          color: theme.colorScheme.primary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _amountController,
                  keyboardType:
                      const TextInputType.numberWithOptions(decimal: true),
                  inputFormatters: [
                    FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*')),
                  ],
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  decoration: InputDecoration(
                    hintText: '0.00',
                    suffixIcon: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'VRDX',
                            style: theme.textTheme.titleSmall?.copyWith(
                              color: theme.colorScheme.primary,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // Fee Estimate Selector
                FeeEstimateWidget(
                  recipient: _recipientController.text,
                  amount: currentAmount,
                ),

                const SizedBox(height: 32),

                // Send Action Button
                VerdisButton(
                  label: 'Review Transfer',
                  icon: Icons.arrow_forward_rounded,
                  onPressed: _onSubmitSend,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
