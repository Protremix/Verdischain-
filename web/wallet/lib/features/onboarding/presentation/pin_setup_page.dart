import 'package:verdis_wallet/core/router/route_names.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'onboarding_providers.dart';

/// 6-Digit PIN Setup and Confirmation screen
class PinSetupPage extends ConsumerStatefulWidget {
  const PinSetupPage({super.key});

  @override
  ConsumerState<PinSetupPage> createState() => _PinSetupPageState();
}

class _PinSetupPageState extends ConsumerState<PinSetupPage> {
  Future<void> _handlePinDigit(String digit) async {
    final notifier = ref.read(pinSetupProvider.notifier);
    notifier.appendDigit(digit);

    final state = ref.read(pinSetupProvider);

    // If step 2 (confirmation) PIN reached 6 digits, auto-submit
    if (state.isConfirming && state.confirmPin.length == 6) {
      await _finalizePinSetup();
    }
  }

  Future<void> _finalizePinSetup() async {
    final creationState = ref.read(walletCreationProvider);
    final importState = ref.read(walletImportProvider);

    String mnemonic = creationState.mnemonic;
    String privateKey = creationState.privateKey;
    String publicKey = creationState.publicKey;
    String address = creationState.address;

    // Fallback to imported wallet if creation state is empty
    if (mnemonic.isEmpty && importState.derivedPrivateKey != null) {
      mnemonic = importState.mnemonicInput;
      privateKey = importState.derivedPrivateKey!;
      publicKey = importState.derivedPublicKey ?? '';
      address = importState.derivedAddress ?? '';
    }

    final success = await ref.read(pinSetupProvider.notifier).submitAndFinalizePin(
          mnemonic: mnemonic,
          privateKey: privateKey,
          publicKey: publicKey,
          address: address,
        );

    if (success && mounted) {
      // Clear navigation history and go to Home
      context.go(RouteNames.home);
    }
  }

  @override
  Widget build(BuildContext context) {
    final pinState = ref.watch(pinSetupProvider);
    final theme = Theme.of(context);

    final activePin = pinState.isConfirming ? pinState.confirmPin : pinState.pin;

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E0A),
      appBar: AppBar(
        title: const Text('Set Security PIN'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            ref.read(pinSetupProvider.notifier).clearPin();
            context.pop();
          },
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Column(
            children: [
              const SizedBox(height: 20),

              // Status Title
              Text(
                pinState.isConfirming ? 'Confirm Your 6-Digit PIN' : 'Create 6-Digit Security PIN',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFFE8F0E8),
                ),
              ),
              const SizedBox(height: 8),

              Text(
                pinState.isConfirming
                    ? 'Re-enter your 6-digit PIN to verify'
                    : 'This PIN will unlock your wallet and approve transactions',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFF8B9D8B),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),

              // 6 Dot Indicators
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(6, (index) {
                  final isFilled = index < activePin.length;
                  return AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    margin: const EdgeInsets.symmetric(horizontal: 10),
                    width: 18,
                    height: 18,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: isFilled ? const Color(0xFF00FF88) : const Color(0xFF1A211A),
                      border: Border.all(
                        color: isFilled ? const Color(0xFF00FF88) : const Color(0xFF2A332A),
                        width: 2,
                      ),
                      boxShadow: isFilled
                          ? [
                              BoxShadow(
                                color: const Color(0xFF00FF88).withOpacity(0.4),
                                blurRadius: 8,
                                spreadRadius: 1,
                              ),
                            ]
                          : null,
                    ),
                  );
                }),
              ),
              const SizedBox(height: 16),

              // Error Message
              if (pinState.error != null)
                Text(
                  pinState.error!,
                  style: const TextStyle(
                    color: Color(0xFFCF6679),
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                  ),
                ),

              const Spacer(),

              // Custom Keypad (0-9, backspace, clear)
              Container(
                constraints: const BoxConstraints(maxWidth: 320),
                child: Column(
                  children: [
                    _buildKeypadRow(['1', '2', '3']),
                    const SizedBox(height: 16),
                    _buildKeypadRow(['4', '5', '6']),
                    const SizedBox(height: 16),
                    _buildKeypadRow(['7', '8', '9']),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        _buildKeypadButton(
                          icon: Icons.clear_all,
                          onPressed: () {
                            ref.read(pinSetupProvider.notifier).clearPin();
                          },
                        ),
                        _buildKeypadButton(
                          label: '0',
                          onPressed: () => _handlePinDigit('0'),
                        ),
                        _buildKeypadButton(
                          icon: Icons.backspace_outlined,
                          onPressed: () {
                            ref.read(pinSetupProvider.notifier).deleteDigit();
                          },
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              if (pinState.isLoading)
                const CircularProgressIndicator(color: Color(0xFF00FF88)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildKeypadRow(List<String> digits) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: digits
          .map((d) => _buildKeypadButton(
                label: d,
                onPressed: () => _handlePinDigit(d),
              ),)
          .toList(),
    );
  }

  Widget _buildKeypadButton({
    String? label,
    IconData? icon,
    required VoidCallback onPressed,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(40),
        child: Container(
          width: 72,
          height: 72,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: const Color(0xFF121712),
            border: Border.all(color: const Color(0xFF2A332A)),
          ),
          child: Center(
            child: label != null
                ? Text(
                    label,
                    style: const TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFFE8F0E8),
                    ),
                  )
                : Icon(
                    icon,
                    size: 24,
                    color: const Color(0xFF8B9D8B),
                  ),
          ),
        ),
      ),
    );
  }
}
