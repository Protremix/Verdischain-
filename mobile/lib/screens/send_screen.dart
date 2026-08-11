import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../services/wallet_service.dart';
import '../widgets/verdis_button.dart';

class SendScreen extends StatefulWidget {
  const SendScreen({super.key});

  @override
  State<SendScreen> createState() => _SendScreenState();
}

class _SendScreenState extends State<SendScreen> {
  final TextEditingController _recipientController = TextEditingController();
  final TextEditingController _amountController = TextEditingController();

  final double _estimatedFee = 0.0012;
  String? _errorText;

  @override
  void dispose() {
    _recipientController.dispose();
    _amountController.dispose();
    super.dispose();
  }

  void _setMaxAmount(double available) {
    final maxAmt = available > _estimatedFee ? available - _estimatedFee : 0.0;
    _amountController.text = maxAmt.toStringAsFixed(4);
  }

  Future<void> _pasteAddress() async {
    final data = await Clipboard.getData(Clipboard.kTextPlain);
    if (data != null && data.text != null) {
      setState(() {
        _recipientController.text = data.text!.trim();
      });
    }
  }

  Future<void> _executeSend() async {
    final recipient = _recipientController.text.trim();
    final amountText = _amountController.text.trim();

    if (recipient.isEmpty) {
      setState(() => _errorText = 'Please enter a valid recipient address');
      return;
    }

    final amount = double.tryParse(amountText);
    if (amount == null || amount <= 0) {
      setState(() => _errorText = 'Please enter a valid amount');
      return;
    }

    final wallet = Provider.of<WalletService>(context, listen: false);

    if (amount + _estimatedFee > wallet.vrdxBalance) {
      setState(() => _errorText = 'Amount + fee exceeds total available VRDX balance');
      return;
    }

    setState(() => _errorText = null);

    final success = await wallet.sendTokens(recipient: recipient, amount: amount);

    if (mounted) {
      if (success) {
        showDialog(
          context: context,
          builder: (ctx) => AlertDialog(
            backgroundColor: const Color(0xFF0D1410),
            title: const Text('Transaction Submitted', style: TextStyle(color: Color(0xFFFFFFFF))),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.check_circle_outline, color: Color(0xFF16a34a), size: 48),
                const SizedBox(height: 12),
                Text(
                  'Sent $amount VRDX to $recipient',
                  style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 13),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Extrinsic successfully broadcasted to Substrate RPC.',
                  style: TextStyle(color: Color(0xFF94a3b8), fontSize: 11),
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.pop(ctx);
                  Navigator.pop(context);
                },
                child: const Text('Done', style: TextStyle(color: Color(0xFF16a34a))),
              ),
            ],
          ),
        );
      } else {
        setState(() {
          _errorText = wallet.errorMessage ?? 'Transaction broadcast failed';
        });
      }
    }
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
          'Send VRDX',
          style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 16, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFFFFFFFF)),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (_errorText != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFEF4444).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFFEF4444)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline, color: Color(0xFFEF4444), size: 18),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _errorText!,
                          style: const TextStyle(color: Color(0xFFEF4444), fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],
              Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Recipient Address',
                        style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 13, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _recipientController,
                        style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 13, fontFamily: 'monospace'),
                        decoration: InputDecoration(
                          hintText: 'Enter Verdis address (vrdx1...)',
                          hintStyle: const TextStyle(color: Color(0xFF94a3b8), fontSize: 12),
                          filled: true,
                          fillColor: const Color(0xFF0D1410),
                          enabledBorder: const OutlineInputBorder(
                            borderSide: BorderSide(color: Color(0xFF2E2E34)),
                          ),
                          focusedBorder: const OutlineInputBorder(
                            borderSide: BorderSide(color: Color(0xFF16a34a)),
                          ),
                          suffixIcon: IconButton(
                            icon: const Icon(Icons.content_paste, color: Color(0xFF16a34a), size: 18),
                            onPressed: _pasteAddress,
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Amount (VRDX)',
                            style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 13, fontWeight: FontWeight.w600),
                          ),
                          GestureDetector(
                            onTap: () => _setMaxAmount(wallet.vrdxBalance),
                            child: Text(
                              'Available: ${wallet.vrdxBalance.toStringAsFixed(2)} VRDX',
                              style: const TextStyle(color: Color(0xFF16a34a), fontSize: 12),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _amountController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 18, fontWeight: FontWeight.bold),
                        decoration: InputDecoration(
                          hintText: '0.00',
                          hintStyle: const TextStyle(color: Color(0xFF94a3b8), fontSize: 18),
                          filled: true,
                          fillColor: const Color(0xFF0D1410),
                          enabledBorder: const OutlineInputBorder(
                            borderSide: BorderSide(color: Color(0xFF2E2E34)),
                          ),
                          focusedBorder: const OutlineInputBorder(
                            borderSide: BorderSide(color: Color(0xFF16a34a)),
                          ),
                          suffixIcon: TextButton(
                            onPressed: () => _setMaxAmount(wallet.vrdxBalance),
                            child: const Text('MAX', style: TextStyle(color: Color(0xFF16a34a), fontSize: 12, fontWeight: FontWeight.bold)),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0D1410),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text('Estimated Fee', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12)),
                            Text('$_estimatedFee VRDX', style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 12)),
                          ],
                        ),
                      ),
                      const SizedBox(height: 32),
                      VerdisButton(
                        label: 'Send Transaction',
                        onPressed: _executeSend,
                        icon: Icons.send,
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
