#!/usr/bin/env python3
"""Update Flutter wallet UI to match Verdis Chain website design."""

import os

BASE = '/opt/verdis-wallet/mobile'

# 1. Update pubspec.yaml to add assets
pubspec = open(f'{BASE}/pubspec.yaml').read()
if 'assets/' not in pubspec:
    pubspec = pubspec.replace(
        'flutter:\n  uses-material-design: true',
        'flutter:\n  uses-material-design: true\n  assets:\n    - assets/images/verdis-logo-white.png\n    - assets/images/verdis-logo-full.png'
    )
    # Also copy the white logo
    os.system(f'cp /opt/verdis-repo/dist/web/assets/verdis-logo-white.png {BASE}/assets/images/ 2>/dev/null || true')
    open(f'{BASE}/pubspec.yaml', 'w').write(pubspec)
    print("Updated pubspec.yaml with assets")
else:
    print("pubspec.yaml already has assets")

# 2. Update main.dart theme
main_dart = '''import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'services/wallet_service.dart';
import 'services/auth_service.dart';
import 'screens/splash_screen.dart';
import 'screens/onboarding_screen.dart';
import 'screens/dashboard_screen.dart';
import 'screens/send_screen.dart';
import 'screens/receive_screen.dart';
import 'screens/staking_screen.dart';
import 'screens/dex_screen.dart';
import 'screens/eco_screen.dart';
import 'screens/settings_screen.dart';
import 'widgets/verdis_button.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const VerdisWalletApp());
}

// Verdis Chain Design Tokens (matching website)
class VerdisColors {
  static const background = Color(0xFF040806);
  static const surface = Color(0xFF0D1410);
  static const surfaceLight = Color(0xFF152017);
  static const primary = Color(0xFF16a34a);
  static const primaryLight = Color(0xFF84fe87);
  static const primaryDark = Color(0xFF15803d);
  static const accent = Color(0xFF00a86b);
  static const text = Color(0xFFFFFFFF);
  static const textMuted = Color(0xFF94a3b8);
  static const error = Color(0xFFEF4444);
  static const warning = Color(0xFFF59E0B);
  static const success = Color(0xFF22c55e);
  
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF16a34a), Color(0xFF15803d), Color(0xFF00a86b)],
  );
  
  static const LinearGradient accentGradient = LinearGradient(
    begin: Alignment.centerLeft,
    end: Alignment.centerRight,
    colors: [Color(0xFF16a34a), Color(0xFF84fe87)],
  );
  
  static const LinearGradient cardGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF0D1410), Color(0xFF152017)],
  );
}

class VerdisWalletApp extends StatelessWidget {
  const VerdisWalletApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthService()),
        ChangeNotifierProvider(create: (_) => WalletService()),
      ],
      child: Consumer<AuthService>(
        builder: (context, authService, child) {
          final darkTheme = ThemeData(
            brightness: Brightness.dark,
            scaffoldBackgroundColor: VerdisColors.background,
            primaryColor: VerdisColors.primary,
            cardColor: VerdisColors.surface,
            colorScheme: const ColorScheme.dark(
              primary: VerdisColors.primary,
              secondary: VerdisColors.primaryLight,
              surface: VerdisColors.surface,
              error: VerdisColors.error,
            ),
            textTheme: GoogleFonts.interTextTheme(
              ThemeData.dark().textTheme,
            ).apply(
              bodyColor: VerdisColors.text,
              displayColor: VerdisColors.text,
              fontSizeFactor: 1.0,
            ),
            appBarTheme: AppBarTheme(
              backgroundColor: VerdisColors.background,
              elevation: 0,
              iconTheme: const IconThemeData(color: VerdisColors.text),
              titleTextStyle: GoogleFonts.spaceGrotesk(
                color: VerdisColors.text,
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
            bottomNavigationBarTheme: const BottomNavigationBarThemeData(
              backgroundColor: VerdisColors.surface,
              selectedItemColor: VerdisColors.primary,
              unselectedItemColor: VerdisColors.textMuted,
            ),
          );
          return MaterialApp(
            title: 'Verdis Wallet',
            debugShowCheckedModeBanner: false,
            theme: darkTheme,
            home: const SplashScreen(),
          );
        },
      ),
    );
  }
}
'''
open(f'{BASE}/lib/main.dart', 'w').write(main_dart)
print("Updated main.dart with Verdis theme")

# 3. Update splash_screen.dart with logo + fade animation
splash = '''import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
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
        if (authService.biometricEnabled) {
          await authService.authenticateBiometrics();
        }
      }
      if (!context.mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const DashboardScreen()),
      );
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
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Logo with glow
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
                    style: GoogleFonts.spaceGrotesk(
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
                  style: GoogleFonts.inter(
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
            ),
          ),
        ),
      ),
    );
  }
}
'''
open(f'{BASE}/lib/screens/splash_screen.dart', 'w').write(splash)
print("Updated splash_screen.dart with logo + animation")

print("Done with main.dart, splash_screen.dart")
