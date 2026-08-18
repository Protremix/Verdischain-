import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:verdis_wallet/core/router/route_names.dart';
import 'package:verdis_wallet/core/security/biometric_auth.dart';
import 'package:verdis_wallet/core/security/persistent_storage.dart';
import 'package:verdis_wallet/core/security/pin_security_service.dart';
import 'onboarding_providers.dart';
import 'package:verdis_wallet/features/home/presentation/home_providers.dart';

/// Lock screen that appears when the app reopens and a wallet already exists.
/// Offers biometric unlock (if enabled) and PIN entry.
///
/// Uses dual verification:
/// 1. Local PIN hash (flutter_secure_storage) — fast, offline
/// 2. Server-side PIN verification (TX Relay) — fallback if local hash lost
class LockScreenPage extends ConsumerStatefulWidget {
  const LockScreenPage({super.key});

  @override
  ConsumerState<LockScreenPage> createState() => _LockScreenPageState();
}

class _LockScreenPageState extends ConsumerState<LockScreenPage> {
  String _enteredPin = '';
  bool _isLoading = false;
  String? _error;
  int _attempts = 0;
  String? _walletAddress;

  @override
  void initState() {
    super.initState();
    _initAndTryBiometric();
  }

  Future<void> _initAndTryBiometric() async {
    // Get wallet address from PersistentStorage (always reliable)
    _walletAddress = await PersistentStorage.getWalletAddress();
    
    // Try biometric unlock if enabled
    final biometricEnabled = await PersistentStorage.isBiometricEnabled();
    if (biometricEnabled && mounted) {
      await _tryBiometric();
    }
  }

  Future<void> _tryBiometric() async {
    try {
      final biometricManager = ref.read(biometricAuthProvider);
      final available = await biometricManager.isAvailable();
      if (!available || !mounted) return;

      final success = await biometricManager.authenticate(
        reason: 'Unlock your Verdis Wallet',
      );

      if (success && mounted) {
        _unlockAndGoHome();
      }
    } catch (_) {
      // Silent fail — user can enter PIN manually
    }
  }

  Future<void> _unlockAndGoHome() async {
    // Load wallet address from PersistentStorage (reliable) or secure storage
    try {
      final repo = ref.read(onboardingWalletProvider);
      final wallet = await repo.loadWallet();
      if (wallet != null && wallet.containsKey('address') && mounted) {
        ref.read(selectedAddressProvider.notifier).state = wallet['address']!;
      } else if (_walletAddress != null && mounted) {
        // Fall back to PersistentStorage address
        ref.read(selectedAddressProvider.notifier).state = _walletAddress!;
      }
    } catch (_) {
      if (_walletAddress != null && mounted) {
        ref.read(selectedAddressProvider.notifier).state = _walletAddress!;
      }
    }

    if (!mounted) return;
    context.go(RouteNames.home);
  }

  Future<void> _handlePinDigit(String digit) async {
    if (_isLoading || _enteredPin.length >= 6) return;

    setState(() {
      _enteredPin = _enteredPin + digit;
      _error = null;
    });

    if (_enteredPin.length == 6) {
      await _verifyPin();
    }
  }

  Future<void> _verifyPin() async {
    setState(() => _isLoading = true);

    try {
      // Step 1: Try local PIN hash verification (fast, offline)
      final repo = ref.read(onboardingWalletProvider);
      final localCorrect = await repo.verifyPin(_enteredPin);

      if (localCorrect) {
        if (!mounted) return;
        await _unlockAndGoHome();
        return;
      }

      // Step 2: Fall back to server-side PIN verification
      // (handles case where local hash was wiped but server still has it)
      if (_walletAddress != null) {
        final (success, message, remaining) = await PinSecurityService.verifyPin(
          address: _walletAddress!,
          pin: _enteredPin,
        );

        if (success) {
          if (!mounted) return;
          await _unlockAndGoHome();
          return;
        }

        _attempts++;
        setState(() {
          _isLoading = false;
          _enteredPin = '';
          if (message == 'locked') {
            _error = 'Too many failed attempts. Wallet locked for 15 minutes.';
          } else if (remaining > 0) {
            _error = 'Wrong PIN. $remaining attempts remaining.';
          } else {
            _error = 'Wrong PIN. Try again.';
          }
        });
        return;
      }

      // No wallet address available — can't verify server-side
      _attempts++;
      setState(() {
        _isLoading = false;
        _enteredPin = '';
        _error = 'Wrong PIN. Try again.';
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _enteredPin = '';
        _error = 'Error: $e';
      });
    }
  }

  void _deleteDigit() {
    if (_enteredPin.isNotEmpty) {
      setState(() {
        _enteredPin = _enteredPin.substring(0, _enteredPin.length - 1);
        _error = null;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E0A),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            children: [
              const SizedBox(height: 60),

              // Logo
              Image.asset(
                'assets/images/verdis-logo-white.png',
                width: 80,
                height: 80,
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 24),

              Text(
                'Verdis Wallet',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFFE8F0E8),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Enter your PIN to unlock',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFF8B9D8B),
                ),
              ),
              const SizedBox(height: 40),

              // 6 Dot Indicators
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(6, (index) {
                  final isFilled = index < _enteredPin.length;
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

              // Error message
              if (_error != null)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: Text(
                    _error!,
                    style: const TextStyle(
                      color: Color(0xFFCF6679),
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),

              const Spacer(),

              // Keypad
              if (_isLoading)
                const CircularProgressIndicator(color: Color(0xFF00FF88))
              else
                Container(
                  constraints: const BoxConstraints(maxWidth: 320),
                  child: Column(
                    children: [
                      _buildRow(['1', '2', '3']),
                      const SizedBox(height: 16),
                      _buildRow(['4', '5', '6']),
                      const SizedBox(height: 16),
                      _buildRow(['7', '8', '9']),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          _buildKeyButton(
                            icon: Icons.fingerprint,
                            onPressed: _tryBiometric,
                          ),
                          _buildKeyButton(
                            label: '0',
                            onPressed: () => _handlePinDigit('0'),
                          ),
                          _buildKeyButton(
                            icon: Icons.backspace_outlined,
                            onPressed: _deleteDigit,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

              const SizedBox(height: 32),

              // Import wallet link
              TextButton(
                onPressed: () {
                  context.go('/welcome');
                },
                child: Text(
                  'Import different wallet',
                  style: TextStyle(
                    color: const Color(0xFF8B9D8B).withOpacity(0.7),
                    fontSize: 13,
                  ),
                ),
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRow(List<String> digits) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: digits
          .map((d) => _buildKeyButton(
                label: d,
                onPressed: () => _handlePinDigit(d),
              ))
          .toList(),
    );
  }

  Widget _buildKeyButton({String? label, IconData? icon, VoidCallback? onPressed}) {
    return Container(
      width: 70,
      height: 70,
      decoration: BoxDecoration(
        color: const Color(0xFF1A211A),
        borderRadius: BorderRadius.circular(35),
        border: Border.all(color: const Color(0xFF2A332A)),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(35),
          onTap: onPressed,
          child: Center(
            child: icon != null
                ? Icon(icon, color: const Color(0xFFE8F0E8), size: 28)
                : Text(
                    label ?? '',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w500,
                      color: Color(0xFFE8F0E8),
                    ),
                  ),
          ),
        ),
      ),
    );
  }
}
