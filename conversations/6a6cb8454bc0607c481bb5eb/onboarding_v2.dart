import 'dart:async';
import 'dart:math' as math;
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../services/wallet_service.dart';
import '../services/auth_service.dart';
import '../widgets/verdis_button.dart';
import 'dashboard_screen.dart';
import '../services/email_recovery_service.dart';

// Color Palette Constants
const Color _kPrimary = Color(0xFF16A34A);
const Color _kLightPrimary = Color(0xFF84FE87);
const Color _kDarkPrimary = Color(0xFF15803D);
const Color _kBackground = Color(0xFF040806);
const Color _kSurface = Color(0xFF0D1410);
const Color _kSurfaceLight = Color(0xFF152017);
const Color _kTextMuted = Color(0xFF94A3B8);

enum _OnboardingMode {
  create,
  importMnemonic,
  emailRecovery,
}

enum _PinStep {
  enter,
  confirm,
}

class OnboardingScreenV2 extends StatefulWidget {
  const OnboardingScreenV2({super.key});

  @override
  State<OnboardingScreenV2> createState() => _OnboardingScreenV2State();
}

// Support both OnboardingScreenV2 and OnboardingScreen names
typedef OnboardingScreen = OnboardingScreenV2;

class _OnboardingScreenV2State extends State<OnboardingScreenV2>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;

  // View state management
  // 0: Main menu, 1: Mnemonic view (display/input), 2: Email recovery, 3: PIN Setup
  int _currentView = 0;
  _OnboardingMode _selectedMode = _OnboardingMode.create;

  // Mnemonic & Recovery state
  String _generatedMnemonic = "";
  final TextEditingController _importMnemonicController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  bool _isLoading = false;
  String? _errorMessage;

  // PIN Setup state
  _PinStep _pinStep = _PinStep.enter;
  String _firstPin = "";
  String _confirmPin = "";
  String? _pinError;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      duration: const Duration(seconds: 6),
      vsync: this,
    )..repeat();
  }

  @override
  void dispose() {
    _animController.dispose();
    _importMnemonicController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _resetToMainMenu() {
    setState(() {
      _currentView = 0;
      _errorMessage = null;
      _pinError = null;
      _isLoading = false;
      _firstPin = "";
      _confirmPin = "";
      _pinStep = _PinStep.enter;
      _generatedMnemonic = "";
      _importMnemonicController.clear();
      _emailController.clear();
      _passwordController.clear();
    });
  }

  // --- Step 1: Handle Create New Wallet Flow ---
  Future<void> _handleStartCreateWallet() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final walletService = Provider.of<WalletService>(context, listen: false);
    final mnemonic = walletService.generateSeedPhrase();

    setState(() {
      _generatedMnemonic = mnemonic;
      _selectedMode = _OnboardingMode.create;
      _isLoading = false;
      _currentView = 1; // Show Mnemonic display view
    });
  }

  // --- Step 2: Handle Import Wallet Flow ---
  void _handleStartImportWallet() {
    setState(() {
      _selectedMode = _OnboardingMode.importMnemonic;
      _errorMessage = null;
      _currentView = 1; // Show Mnemonic input view
    });
  }

  // --- Step 3: Handle Email Recovery Flow ---
  void _handleStartEmailRecovery() {
    setState(() {
      _selectedMode = _OnboardingMode.emailRecovery;
      _errorMessage = null;
      _currentView = 2; // Show Email recovery view
    });
  }

  // Validate Mnemonic Input & Go to PIN Setup
  void _validateImportMnemonicAndProceed() {
    final text = _importMnemonicController.text.trim();
    final words = text.split(RegExp(r'\s+')).where((w) => w.isNotEmpty).toList();

    if (words.length != 12 && words.length != 24) {
      setState(() {
        _errorMessage = "Please enter a valid 12 or 24-word recovery phrase.";
      });
      return;
    }

    setState(() {
      _generatedMnemonic = words.join(" ");
      _errorMessage = null;
      _pinStep = _PinStep.enter;
      _firstPin = "";
      _confirmPin = "";
      _currentView = 3; // Go to PIN setup
    });
  }

  // Execute Email Recovery API & Go to PIN Setup
  Future<void> _executeEmailRecovery() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text;

    if (email.isEmpty || !email.contains('@')) {
      setState(() {
        _errorMessage = "Please enter a valid email address.";
      });
      return;
    }
    if (password.isEmpty) {
      setState(() {
        _errorMessage = "Please enter your password.";
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final mnemonic = await EmailRecoveryService.recoverWallet(
        email: email,
        password: password,
      );

      setState(() {
        _generatedMnemonic = mnemonic;
        _isLoading = false;
        _pinStep = _PinStep.enter;
        _firstPin = "";
        _confirmPin = "";
        _currentView = 3; // Go to PIN setup
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString().replaceAll("Exception: ", "");
      });
    }
  }

  // --- PIN Setup Logic ---
  void _handlePinInput(String digit) {
    setState(() {
      _pinError = null;
    });

    if (_pinStep == _PinStep.enter) {
      if (_firstPin.length < 6) {
        setState(() {
          _firstPin += digit;
        });
        if (_firstPin.length == 6) {
          // Transition smoothly to confirm step
          Future.delayed(const Duration(milliseconds: 200), () {
            if (!mounted) return;
            setState(() {
              _pinStep = _PinStep.confirm;
            });
          });
        }
      }
    } else {
      if (_confirmPin.length < 6) {
        setState(() {
          _confirmPin += digit;
        });
        if (_confirmPin.length == 6) {
          _finalizeWalletCreation();
        }
      }
    }
  }

  void _handlePinBackspace() {
    setState(() {
      _pinError = null;
      if (_pinStep == _PinStep.enter) {
        if (_firstPin.isNotEmpty) {
          _firstPin = _firstPin.substring(0, _firstPin.length - 1);
        }
      } else {
        if (_confirmPin.isNotEmpty) {
          _confirmPin = _confirmPin.substring(0, _confirmPin.length - 1);
        }
      }
    });
  }

  // Finalize Wallet Creation / Import / Recovery after PIN verification
  Future<void> _finalizeWalletCreation() async {
    if (_firstPin != _confirmPin) {
      setState(() {
        _pinError = "PINs do not match. Please try again.";
        _confirmPin = "";
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _pinError = null;
    });

    try {
      final walletService = Provider.of<WalletService>(context, listen: false);

      // CRITICAL REQUIREMENT: Pass PIN to walletService BEFORE creating/importing wallet
      walletService.setWalletPin(_firstPin);

      // Try setting PIN in AuthService as well if present
      try {
        final authService = Provider.of<AuthService>(context, listen: false);
        await authService.setPin(_firstPin);
      } catch (_) {}

      // Create or import wallet with verified mnemonic
      if (_selectedMode == _OnboardingMode.create) {
        await walletService.createNewWallet(
          'Main Wallet',
          seedPhrase: _generatedMnemonic,
        );
      } else {
        await walletService.importWallet(
          'Main Wallet',
          _generatedMnemonic,
        );
      }

      if (!mounted) return;

      // Navigate to Dashboard
      Navigator.pushReplacement(
        context,
        PageRouteBuilder(
          pageBuilder: (_, animation, __) => const DashboardScreen(),
          transitionsBuilder: (_, animation, __, child) {
            return FadeTransition(
              opacity: CurvedAnimation(
                parent: animation,
                curve: Curves.easeOut,
              ),
              child: child,
            );
          },
          transitionDuration: const Duration(milliseconds: 500),
        ),
      );
    } catch (e) {
      setState(() {
        _isLoading = false;
        _pinError = "Failed to create wallet: $e";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _kBackground,
      body: AnimatedBuilder(
        animation: _animController,
        builder: (context, child) {
          final t = _animController.value;
          final color1 = Color.lerp(
            _kBackground,
            const Color(0xFF0A1410),
            (math.sin(t * math.pi * 2) + 1) / 2,
          )!;
          final color2 = Color.lerp(
            const Color(0xFF0A1410),
            _kSurface,
            (math.cos(t * math.pi * 2) + 1) / 2,
          )!;
          final color3 = Color.lerp(
            _kSurface,
            _kBackground,
            (math.sin(t * math.pi * 2 + 1) + 1) / 2,
          )!;

          return Container(
            width: double.infinity,
            height: double.infinity,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [color1, color2, color3],
              ),
            ),
            child: SafeArea(
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 400),
                switchInCurve: Curves.easeOutCubic,
                switchOutCurve: Curves.easeInCubic,
                child: _buildCurrentView(),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildCurrentView() {
    switch (_currentView) {
      case 1:
        return _selectedMode == _OnboardingMode.create
            ? _buildMnemonicDisplayView()
            : _buildMnemonicInputView();
      case 2:
        return _buildEmailRecoveryView();
      case 3:
        return _buildPinSetupView();
      case 0:
      default:
        return _buildMainMenuView();
    }
  }

  // --- Main Onboarding Menu View ---
  Widget _buildMainMenuView() {
    final pulseVal = (math.sin(_animController.value * math.pi * 6) + 1) / 2;
    final logoScale = 1.0 + (pulseVal * 0.05);
    final glowOpacity = 0.3 + (pulseVal * 0.2);

    return SingleChildScrollView(
      key: const ValueKey('main_menu_view'),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
      child: Column(
        children: [
          const SizedBox(height: 16),
          // Logo with Glow Animation
          Transform.scale(
            scale: logoScale,
            child: Container(
              width: 96,
              height: 96,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(24),
                boxShadow: [
                  BoxShadow(
                    color: _kPrimary.withOpacity(glowOpacity),
                    blurRadius: 30,
                    spreadRadius: 6,
                  ),
                ],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(24),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.05),
                      borderRadius: BorderRadius.circular(24),
                      border: Border.all(
                        color: _kPrimary.withOpacity(0.3),
                        width: 1.5,
                      ),
                    ),
                    padding: const EdgeInsets.all(16),
                    child: Image.asset(
                      'assets/images/verdis-logo-white.png',
                      fit: BoxFit.contain,
                      errorBuilder: (_, __, ___) => const Icon(
                        Icons.eco_rounded,
                        size: 48,
                        color: _kLightPrimary,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Title with Gradient ShaderMask
          ShaderMask(
            shaderCallback: (bounds) => const LinearGradient(
              colors: [_kPrimary, _kLightPrimary],
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
            ).createShader(bounds),
            child: const Text(
              'Verdis Wallet',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.w800,
                letterSpacing: 1.5,
                color: Colors.white,
              ),
            ),
          ),
          const SizedBox(height: 8),

          const Text(
            'Eco-Friendly Blockchain Wallet',
            style: TextStyle(
              color: _kTextMuted,
              fontSize: 13,
              fontWeight: FontWeight.w400,
            ),
          ),
          const SizedBox(height: 48),

          // Three Action Cards
          _buildActionCard(
            title: 'Create New Wallet',
            subtitle: 'Generate a new seed phrase & set up your secure wallet',
            icon: Icons.add_circle_outline_rounded,
            onTap: _handleStartCreateWallet,
          ),
          const SizedBox(height: 16),

          _buildActionCard(
            title: 'Import Wallet',
            subtitle: 'Restore using an existing 12 or 24-word recovery phrase',
            icon: Icons.download_rounded,
            onTap: _handleStartImportWallet,
          ),
          const SizedBox(height: 16),

          _buildActionCard(
            title: 'Recover with Email',
            subtitle: 'Restore your wallet from encrypted cloud backup',
            icon: Icons.mark_email_read_outlined,
            onTap: _handleStartEmailRecovery,
          ),
          const SizedBox(height: 48),

          // Footer Text
          const Text(
            'Verdis Network • Powered by Proof-of-Green',
            style: TextStyle(
              color: _kTextMuted,
              fontSize: 11,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }

  // Helper Widget for Action Cards with Glassmorphism
  Widget _buildActionCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [_kSurface, _kSurfaceLight],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _kPrimary.withOpacity(0.2),
          width: 1.5,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: _isLoading ? null : onTap,
              borderRadius: BorderRadius.circular(16),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: _kPrimary.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: _kPrimary.withOpacity(0.3),
                        ),
                      ),
                      child: Icon(
                        icon,
                        color: _kLightPrimary,
                        size: 26,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAlignment.start,
                        children: [
                          Text(
                            title,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            subtitle,
                            style: const TextStyle(
                              color: _kTextMuted,
                              fontSize: 13,
                              height: 1.3,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const Icon(
                      Icons.chevron_right_rounded,
                      color: _kTextMuted,
                      size: 24,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  // --- Mnemonic Display View (Create New Wallet Flow) ---
  Widget _buildMnemonicDisplayView() {
    final words = _generatedMnemonic.split(" ");

    return SingleChildScrollView(
      key: const ValueKey('mnemonic_display_view'),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      child: Column(
        crossAxisAlignment: CrossAlignment.start,
        children: [
          IconButton(
            onPressed: _resetToMainMenu,
            icon: const Icon(Icons.arrow_back_rounded, color: Colors.white),
          ),
          const SizedBox(height: 16),

          const Text(
            'Secret Recovery Phrase',
            style: TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),

          const Text(
            'Write down these 12 words in order and store them in a secure place. Never share them with anyone.',
            style: TextStyle(
              color: _kTextMuted,
              fontSize: 13,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 24),

          // Glassmorphic 12-Word Grid
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.05),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: _kPrimary.withOpacity(0.2),
              ),
            ),
            child: GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3,
                childAspectRatio: 2.2,
                crossAxisSpacing: 10,
                mainAxisSpacing: 10,
              ),
              itemCount: words.length,
              itemBuilder: (context, index) {
                return Container(
                  decoration: BoxDecoration(
                    color: _kSurfaceLight,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: _kPrimary.withOpacity(0.15),
                    ),
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: Row(
                    children: [
                      Text(
                        '${index + 1}.',
                        style: const TextStyle(
                          color: _kTextMuted,
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          words[index],
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 24),

          // Copy Button
          Center(
            child: TextButton.icon(
              onPressed: () {
                Clipboard.setData(ClipboardData(text: _generatedMnemonic));
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: const Text('Recovery phrase copied to clipboard'),
                    backgroundColor: _kDarkPrimary,
                    behavior: SnackBarBehavior.floating,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                );
              },
              icon: const Icon(Icons.copy_rounded, color: _kLightPrimary, size: 18),
              label: const Text(
                'Copy to Clipboard',
                style: TextStyle(
                  color: _kLightPrimary,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
          const SizedBox(height: 32),

          // Action Button -> Proceed to PIN Setup
          VerdisButton(
            label: 'I Saved My Phrase',
            onPressed: () {
              setState(() {
                _pinStep = _PinStep.enter;
                _firstPin = "";
                _confirmPin = "";
                _currentView = 3; // PIN Setup view
              });
            },
          ),
        ],
      ),
    );
  }

  // --- Mnemonic Input View (Import Wallet Flow) ---
  Widget _buildMnemonicInputView() {
    return SingleChildScrollView(
      key: const ValueKey('mnemonic_input_view'),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      child: Column(
        crossAxisAlignment: CrossAlignment.start,
        children: [
          IconButton(
            onPressed: _resetToMainMenu,
            icon: const Icon(Icons.arrow_back_rounded, color: Colors.white),
          ),
          const SizedBox(height: 16),

          const Text(
            'Import Wallet',
            style: TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),

          const Text(
            'Enter your 12 or 24-word secret recovery phrase separated by spaces.',
            style: TextStyle(
              color: _kTextMuted,
              fontSize: 13,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 24),

          if (_errorMessage != null) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFEF4444).withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFEF4444).withOpacity(0.4)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline_rounded, color: Color(0xFFEF4444), size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(color: Color(0xFFEF4444), fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],

          // Mnemonic TextField Container
          Container(
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.05),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: _kPrimary.withOpacity(0.3),
              ),
            ),
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _importMnemonicController,
              maxLines: 4,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                height: 1.5,
              ),
              decoration: const InputDecoration(
                hintText: 'word1 word2 word3 ...',
                hintStyle: TextStyle(color: _kTextMuted),
                border: InputBorder.none,
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Paste Button
          Align(
            alignment: Alignment.centerRight,
            child: TextButton.icon(
              onPressed: () async {
                final data = await Clipboard.getData(Clipboard.kTextPlain);
                if (data?.text != null) {
                  _importMnemonicController.text = data!.text!.trim();
                }
              },
              icon: const Icon(Icons.content_paste_rounded, color: _kLightPrimary, size: 16),
              label: const Text(
                'Paste from Clipboard',
                style: TextStyle(color: _kLightPrimary, fontSize: 13),
              ),
            ),
          ),
          const SizedBox(height: 32),

          VerdisButton(
            label: 'Continue',
            onPressed: _validateImportMnemonicAndProceed,
          ),
        ],
      ),
    );
  }

  // --- Email Recovery View ---
  Widget _buildEmailRecoveryView() {
    return SingleChildScrollView(
      key: const ValueKey('email_recovery_view'),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      child: Column(
        crossAxisAlignment: CrossAlignment.start,
        children: [
          IconButton(
            onPressed: _resetToMainMenu,
            icon: const Icon(Icons.arrow_back_rounded, color: Colors.white),
          ),
          const SizedBox(height: 16),

          const Text(
            'Recover with Email',
            style: TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),

          const Text(
            'Enter your registered email and backup password to decrypt your cloud recovery backup.',
            style: TextStyle(
              color: _kTextMuted,
              fontSize: 13,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 24),

          if (_errorMessage != null) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFEF4444).withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFEF4444).withOpacity(0.4)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline_rounded, color: Color(0xFFEF4444), size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(color: Color(0xFFEF4444), fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],

          // Email Field
          Container(
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.05),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: _kPrimary.withOpacity(0.2)),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: TextField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              style: const TextStyle(color: Colors.white, fontSize: 14),
              decoration: const InputDecoration(
                icon: Icon(Icons.email_outlined, color: _kTextMuted),
                hintText: 'Email Address',
                hintStyle: TextStyle(color: _kTextMuted),
                border: InputBorder.none,
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Password Field
          Container(
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.05),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: _kPrimary.withOpacity(0.2)),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: TextField(
              controller: _passwordController,
              obscureText: true,
              style: const TextStyle(color: Colors.white, fontSize: 14),
              decoration: const InputDecoration(
                icon: Icon(Icons.lock_outline_rounded, color: _kTextMuted),
                hintText: 'Backup Password',
                hintStyle: TextStyle(color: _kTextMuted),
                border: InputBorder.none,
              ),
            ),
          ),
          const SizedBox(height: 32),

          VerdisButton(
            label: 'Recover Wallet',
            isLoading: _isLoading,
            onPressed: _executeEmailRecovery,
          ),
        ],
      ),
    );
  }

  // --- PIN Setup View (CRITICAL Flow) ---
  Widget _buildPinSetupView() {
    final isConfirmStep = _pinStep == _PinStep.confirm;
    final currentPin = isConfirmStep ? _confirmPin : _firstPin;

    return Center(
      key: const ValueKey('pin_setup_view'),
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Header Icon Card
            ClipRRect(
              borderRadius: BorderRadius.circular(24),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                child: Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(
                      color: _kPrimary.withOpacity(0.2),
                      width: 1.5,
                    ),
                  ),
                  child: Icon(
                    isConfirmStep ? Icons.verified_user_outlined : Icons.shield_outlined,
                    size: 40,
                    color: _kLightPrimary,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),

            Text(
              isConfirmStep ? 'Confirm Your PIN' : 'Create 6-Digit PIN',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),

            Text(
              isConfirmStep
                  ? 'Re-enter your 6-digit PIN to verify.'
                  : 'Choose a PIN to secure your wallet & encrypt private keys.',
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: _kTextMuted,
                fontSize: 13,
              ),
            ),
            const SizedBox(height: 16),

            // Error Message Display
            AnimatedOpacity(
              duration: const Duration(milliseconds: 300),
              opacity: _pinError != null ? 1.0 : 0.0,
              child: Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Text(
                  _pinError ?? '',
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    color: Color(0xFFEF4444),
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ),

            // PIN Dots Indicator (6 dots)
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(6, (index) {
                final isFilled = index < currentPin.length;
                return AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  margin: const EdgeInsets.symmetric(horizontal: 8),
                  width: 16,
                  height: 16,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isFilled ? _kPrimary : Colors.transparent,
                    border: Border.all(
                      color: isFilled ? _kLightPrimary : _kSurfaceLight,
                      width: 2,
                    ),
                    boxShadow: isFilled
                        ? [
                            BoxShadow(
                              color: _kPrimary.withOpacity(0.5),
                              blurRadius: 8,
                              spreadRadius: 1,
                            )
                          ]
                        : null,
                  ),
                );
              }),
            ),
            const SizedBox(height: 32),

            // Glassmorphic Number Pad
            _buildPinNumberPad(),

            if (isConfirmStep) ...[
              const SizedBox(height: 16),
              TextButton(
                onPressed: () {
                  setState(() {
                    _pinStep = _PinStep.enter;
                    _firstPin = "";
                    _confirmPin = "";
                    _pinError = null;
                  });
                },
                child: const Text(
                  'Start Over',
                  style: TextStyle(color: _kLightPrimary, fontSize: 13),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPinNumberPad() {
    return Container(
      constraints: const BoxConstraints(maxWidth: 280),
      child: Column(
        children: [
          _buildPinPadRow(['1', '2', '3']),
          const SizedBox(height: 16),
          _buildPinPadRow(['4', '5', '6']),
          const SizedBox(height: 16),
          _buildPinPadRow(['7', '8', '9']),
          const SizedBox(height: 16),
          _buildPinPadRow(['', '0', 'backspace']),
        ],
      ),
    );
  }

  Widget _buildPinPadRow(List<String> keys) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: keys.map((key) {
        if (key.isEmpty) {
          return const SizedBox(width: 72, height: 72);
        }
        return _buildPinPadButton(key);
      }).toList(),
    );
  }

  Widget _buildPinPadButton(String key) {
    final isBackspace = key == 'backspace';

    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          width: 72,
          height: 72,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.05),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: _kPrimary.withOpacity(0.2),
              width: 1,
            ),
          ),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: _isLoading
                  ? null
                  : () {
                      if (isBackspace) {
                        _handlePinBackspace();
                      } else {
                        _handlePinInput(key);
                      }
                    },
              borderRadius: BorderRadius.circular(16),
              child: Center(
                child: isBackspace
                    ? const Icon(
                        Icons.backspace_outlined,
                        color: _kTextMuted,
                        size: 22,
                      )
                    : Text(
                        key,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
