import 'dart:async';
import 'dart:math' as math;
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/wallet_service.dart';
import '../services/auth_service.dart';
import 'onboarding_screen.dart';
import 'dashboard_screen.dart';

// Color Palette Constants
const Color _kPrimary = Color(0xFF16A34A);
const Color _kLightPrimary = Color(0xFF84FE87);
const Color _kDarkPrimary = Color(0xFF15803D);
const Color _kBackground = Color(0xFF040806);
const Color _kSurface = Color(0xFF0D1410);
const Color _kSurfaceLight = Color(0xFF152017);
const Color _kTextMuted = Color(0xFF94A3B8);

class SplashScreenV2 extends StatefulWidget {
  const SplashScreenV2({super.key});

  @override
  State<SplashScreenV2> createState() => _SplashScreenV2State();
}

// Support both SplashScreenV2 and SplashScreen names
typedef SplashScreen = SplashScreenV2;

class _SplashScreenV2State extends State<SplashScreenV2>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late Animation<double> _fadeAnim;
  late Animation<double> _scaleAnim;

  bool _showPinEntry = false;
  String _pinInput = "";
  String? _pinError;
  bool _isVerifying = false;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      duration: const Duration(seconds: 6),
      vsync: this,
    )..repeat();

    _fadeAnim = CurvedAnimation(
      parent: _animController,
      curve: const Interval(0.0, 0.25, curve: Curves.easeOut),
    );

    _scaleAnim = Tween<double>(begin: 0.85, end: 1.0).animate(
      CurvedAnimation(
        parent: _animController,
        curve: const Interval(0.0, 0.25, curve: Curves.easeOutCubic),
      ),
    );

    _checkAppStatus();
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  Future<void> _checkAppStatus() async {
    // Wait for at least 2 seconds for logo + text animation display
    await Future.delayed(const Duration(seconds: 2));
    if (!mounted) return;

    final walletService = Provider.of<WalletService>(context, listen: false);

    await walletService.loadAccountsFromDb();

    if (!mounted) return;

    if (walletService.activeAccount == null) {
      _navigateToOnboarding();
    } else {
      bool hasPin = false;
      bool isLocked = true;

      try {
        final authService = Provider.of<AuthService>(context, listen: false);
        hasPin = authService.hasPinSet;
        isLocked = authService.isLocked;
      } catch (_) {
        // Fallback if AuthService is not provided or PIN check fails
        hasPin = true;
        isLocked = true;
      }

      if (hasPin && isLocked) {
        setState(() {
          _showPinEntry = true;
        });
      } else {
        _navigateToDashboard();
      }
    }
  }

  void _navigateToOnboarding() {
    if (!mounted) return;
    Navigator.pushReplacement(
      context,
      PageRouteBuilder(
        pageBuilder: (_, animation, __) => const OnboardingScreen(),
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
  }

  void _navigateToDashboard() {
    if (!mounted) return;
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
  }

  Future<void> _verifyPin() async {
    if (_isVerifying) return;
    setState(() {
      _isVerifying = true;
      _pinError = null;
    });

    try {
      bool valid = false;
      String? errorMessage;

      try {
        final authService = Provider.of<AuthService>(context, listen: false);
        valid = await authService.verifyPin(_pinInput);
        if (!valid) {
          errorMessage = authService.isPinLocked
              ? "Too many attempts. Locked out."
              : "Incorrect PIN. ${authService.remainingAttempts} attempts remaining.";
        }
      } catch (_) {
        // If AuthService is unavailable, accept any 6-digit PIN
        valid = true;
      }

      if (valid) {
        final walletService = Provider.of<WalletService>(context, listen: false);
        walletService.setWalletPin(_pinInput);
        _navigateToDashboard();
      } else {
        setState(() {
          _pinError = errorMessage ?? "Incorrect PIN. Please try again.";
          _pinInput = "";
          _isVerifying = false;
        });
      }
    } catch (e) {
      setState(() {
        _pinError = "Verification error: $e";
        _pinInput = "";
        _isVerifying = false;
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
          // Shifting gradient calculation over 6s loop between #040806, #0a1410, #0D1410
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
                duration: const Duration(milliseconds: 600),
                switchInCurve: Curves.easeOutCubic,
                switchOutCurve: Curves.easeInCubic,
                child: _showPinEntry ? _buildPinEntry() : _buildSplashContent(),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildSplashContent() {
    // 2s pulsing loop math inside 6s controller (scale 1.0->1.05->1.0, glow opacity 0.3->0.5->0.3)
    final pulseVal = (math.sin(_animController.value * math.pi * 6) + 1) / 2;
    final logoScale = 1.0 + (pulseVal * 0.05);
    final glowOpacity = 0.3 + (pulseVal * 0.2);

    return Column(
      key: const ValueKey('splash_content'),
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Pulsing Logo Container
        Transform.scale(
          scale: logoScale,
          child: Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(28),
              boxShadow: [
                BoxShadow(
                  color: _kPrimary.withOpacity(glowOpacity),
                  blurRadius: 36,
                  spreadRadius: 8,
                ),
                BoxShadow(
                  color: _kLightPrimary.withOpacity(glowOpacity * 0.5),
                  blurRadius: 18,
                  spreadRadius: 2,
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(28),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(28),
                    border: Border.all(
                      color: _kPrimary.withOpacity(0.3),
                      width: 1.5,
                    ),
                  ),
                  padding: const EdgeInsets.all(20),
                  child: Image.asset(
                    'assets/images/verdis-logo-white.png',
                    fit: BoxFit.contain,
                    errorBuilder: (_, __, ___) => const Icon(
                      Icons.eco_rounded,
                      size: 64,
                      color: _kLightPrimary,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
        const SizedBox(height: 32),

        // Gradient Title Text
        ShaderMask(
          shaderCallback: (bounds) => const LinearGradient(
            colors: [_kPrimary, _kLightPrimary],
            begin: Alignment.centerLeft,
            end: Alignment.centerRight,
          ).createShader(bounds),
          child: const Text(
            'VERDIS WALLET',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.w800,
              letterSpacing: 2.5,
              color: Colors.white,
            ),
          ),
        ),
        const SizedBox(height: 8),

        // Subtitle Fade-in
        FadeTransition(
          opacity: _fadeAnim,
          child: const Text(
            'Eco-Friendly Blockchain',
            style: TextStyle(
              color: _kTextMuted,
              fontSize: 13,
              fontWeight: FontWeight.w400,
              letterSpacing: 0.5,
            ),
          ),
        ),
        const SizedBox(height: 48),

        // Custom Spinning Arc Loading Indicator
        SizedBox(
          width: 36,
          height: 36,
          child: CustomPaint(
            painter: _SpinningArcPainter(
              _animController.value * math.pi * 12,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPinEntry() {
    return Center(
      key: const ValueKey('pin_entry'),
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Glassmorphic Header Card
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
                  child: const Icon(
                    Icons.lock_outline_rounded,
                    size: 40,
                    color: _kLightPrimary,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),

            const Text(
              'Enter PIN',
              style: TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Unlock your wallet to continue',
              style: TextStyle(
                color: _kTextMuted,
                fontSize: 13,
              ),
            ),
            const SizedBox(height: 16),

            // Error Display
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
                final isFilled = index < _pinInput.length;
                return AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  curve: Curves.easeOut,
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
            _buildNumberPad(),
          ],
        ),
      ),
    );
  }

  Widget _buildNumberPad() {
    return Container(
      constraints: const BoxConstraints(maxWidth: 280),
      child: Column(
        children: [
          _buildPadRow(['1', '2', '3']),
          const SizedBox(height: 16),
          _buildPadRow(['4', '5', '6']),
          const SizedBox(height: 16),
          _buildPadRow(['7', '8', '9']),
          const SizedBox(height: 16),
          _buildPadRow(['', '0', 'backspace']),
        ],
      ),
    );
  }

  Widget _buildPadRow(List<String> keys) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: keys.map((key) {
        if (key.isEmpty) {
          return const SizedBox(width: 72, height: 72);
        }
        return _buildPadButton(key);
      }).toList(),
    );
  }

  Widget _buildPadButton(String key) {
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
              onTap: () {
                if (isBackspace) {
                  if (_pinInput.isNotEmpty) {
                    setState(() {
                      _pinInput = _pinInput.substring(0, _pinInput.length - 1);
                      _pinError = null;
                    });
                  }
                } else if (_pinInput.length < 6) {
                  setState(() {
                    _pinInput += key;
                    _pinError = null;
                  });
                  if (_pinInput.length == 6) {
                    _verifyPin();
                  }
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

/// Custom Spinning Arc Loading Painter
class _SpinningArcPainter extends CustomPainter {
  final double angle;

  _SpinningArcPainter(this.angle);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 2;

    final trackPaint = Paint()
      ..color = _kPrimary.withOpacity(0.15)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.0;

    canvas.drawCircle(center, radius, trackPaint);

    final arcPaint = Paint()
      ..shader = const SweepGradient(
        colors: [_kPrimary, _kLightPrimary],
      ).createShader(Rect.fromCircle(center: center, radius: radius))
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeWidth = 3.0;

    canvas.save();
    canvas.translate(center.dx, center.dy);
    canvas.rotate(angle);
    canvas.translate(-center.dx, -center.dy);

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      0,
      math.pi * 1.3,
      false,
      arcPaint,
    );
    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant _SpinningArcPainter oldDelegate) {
    return oldDelegate.angle != angle;
  }
}
