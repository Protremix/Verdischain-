import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/wallet_service.dart';
import '../services/auth_service.dart';
import 'onboarding_screen.dart';
import 'dashboard_screen.dart';

// ignore_for_file: use_build_context_synchronously

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late Animation<double> _fadeAnim;
  late Animation<double> _scaleAnim;
  bool _showPinEntry = false;
  String _pinInput = "";
  String? _pinError;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _fadeAnim = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeOut),
    );
    _scaleAnim = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeOutCubic),
    );
    _animController.forward();
    _checkAppStatus();
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  Future<void> _checkAppStatus() async {
    await Future.delayed(const Duration(seconds: 2));
    if (!context.mounted) return;

    final walletService = Provider.of<WalletService>(context, listen: false);
    final authService = Provider.of<AuthService>(context, listen: false);

    await walletService.loadAccountsFromDb();

    if (!context.mounted) return;

    if (walletService.activeAccount == null) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const OnboardingScreen()),
      );
    } else {
      if (authService.hasPinSet && authService.isLocked) {
        // Try biometric first if enabled
        if (authService.biometricEnabled) {
          final bioSuccess = await authService.authenticateBiometrics();
          if (bioSuccess && mounted) {
            walletService.setWalletPin("");  // biometric unlocks the app, PIN not needed
            _navigateToDashboard();
            return;
          }
        }
        // Show PIN entry if biometric not enabled or failed
        setState(() {
          _showPinEntry = true;
        });
      } else {
        _navigateToDashboard();
      }
    }
  }

  void _navigateToDashboard() {
    if (!context.mounted) return;
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const DashboardScreen()),
    );
  }

  Future<void> _tryBiometric() async {
    final authService = Provider.of<AuthService>(context, listen: false);
    final walletService = Provider.of<WalletService>(context, listen: false);
    final success = await authService.authenticateBiometrics();
    if (success && mounted) {
      walletService.setWalletPin("");
      _navigateToDashboard();
    }
  }

  Future<void> _verifyPin() async {
    final authService = Provider.of<AuthService>(context, listen: false);
    final walletService = Provider.of<WalletService>(context, listen: false);

    final valid = await authService.verifyPin(_pinInput);

    if (valid) {
      // Pass the PIN to the wallet service so it can decrypt mnemonics
      walletService.setWalletPin(_pinInput);
      _navigateToDashboard();
    } else {
      setState(() {
        _pinError = authService.isPinLocked
            ? "Too many attempts. Please restart the app."
            : "Incorrect PIN. ${authService.remainingAttempts} attempts remaining.";
        _pinInput = "";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF040806), Color(0xFF0a1410), Color(0xFF040806)],
          ),
        ),
        child: Center(
          child: AnimatedBuilder(
            animation: _animController,
            builder: (context, child) {
              return FadeTransition(
                opacity: _fadeAnim,
                child: ScaleTransition(
                  scale: _scaleAnim,
                  child: child,
                ),
              );
            },
            child: _showPinEntry ? _buildPinEntry() : _buildSplashContent(),
          ),
        ),
      ),
    );
  }

  Widget _buildSplashContent() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          width: 120,
          height: 120,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF16a34a).withOpacity(0.3),
                blurRadius: 30,
                spreadRadius: 5,
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(24),
            child: Image.asset(
              'assets/images/verdis-logo-white.png',
              fit: BoxFit.contain,
            ),
          ),
        ),
        const SizedBox(height: 28),
        ShaderMask(
          shaderCallback: (bounds) => const LinearGradient(
            colors: [Color(0xFF16a34a), Color(0xFF84fe87)],
          ).createShader(bounds),
          child: Text(
            'VERDIS WALLET',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w700,
              letterSpacing: 2.0,
              color: Colors.white,
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Eco-Friendly Blockchain',
          style: TextStyle(
            color: const Color(0xFF94a3b8),
            fontSize: 13,
            fontWeight: FontWeight.w400,
          ),
        ),
        const SizedBox(height: 48),
        SizedBox(
          width: 28,
          height: 28,
          child: CircularProgressIndicator(
            strokeWidth: 2.5,
            valueColor: AlwaysStoppedAnimation<Color>(
              const Color(0xFF16a34a),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPinEntry() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.lock_outline,
          size: 48,
          color: Color(0xFF16a34a),
        ),
        const SizedBox(height: 20),
        Text(
          'Enter PIN',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        if (_pinError != null)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40),
            child: Text(
              _pinError!,
              textAlign: TextAlign.center,
              style: TextStyle(color: Color(0xFFEF4444), fontSize: 13),
            ),
          ),
        const SizedBox(height: 24),
        // PIN dots
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(6, (i) {
            return Container(
              margin: EdgeInsets.symmetric(horizontal: 6),
              width: 16,
              height: 16,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: i < _pinInput.length
                    ? Color(0xFF16a34a)
                    : Colors.transparent,
                border: Border.all(
                  color: i < _pinInput.length
                      ? Color(0xFF16a34a)
                      : Color(0xFF2E2E34),
                  width: 2,
                ),
              ),
            );
          }),
        ),
        const SizedBox(height: 16),
        // Biometric unlock button (only shows if enabled)
        Consumer<AuthService>(
          builder: (context, auth, _) {
            if (!auth.biometricEnabled) return const SizedBox.shrink();
            return TextButton.icon(
              onPressed: _tryBiometric,
              icon: Icon(Icons.fingerprint, color: Color(0xFF16a34a), size: 28),
              label: Text(
                'Use Biometric',
                style: TextStyle(color: Color(0xFF16a34a), fontSize: 13),
              ),
            );
          },
        ),
        const SizedBox(height: 16),
        // Number pad
        Container(
          width: 260,
          child: GridView.builder(
            shrinkWrap: true,
            physics: NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 3,
              childAspectRatio: 1.5,
              mainAxisSpacing: 8,
              crossAxisSpacing: 8,
            ),
            itemCount: 12,
            itemBuilder: (context, index) {
              if (index == 9) return SizedBox();
              if (index == 11) {
                return Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    IconButton(
                      onPressed: _pinInput.isNotEmpty
                          ? () => setState(() {
                                _pinInput = _pinInput.substring(0, _pinInput.length - 1);
                                _pinError = null;
                              })
                          : null,
                      icon: Icon(Icons.backspace_outlined, color: Color(0xFF94a3b8)),
                    ),
                  ],
                );
              }
              final num = index == 10 ? 0 : index + 1;
              return InkWell(
                onTap: _pinInput.length < 6
                    ? () {
                        setState(() {
                          _pinInput += num.toString();
                          _pinError = null;
                        });
                        if (_pinInput.length == 6) {
                          _verifyPin();
                        }
                      }
                    : null,
                borderRadius: BorderRadius.circular(12),
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Color(0xFF2E2E34)),
                  ),
                  child: Center(
                    child: Text(
                      '$num',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 22,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
