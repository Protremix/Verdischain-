import 'package:flutter/material.dart';
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
            textTheme: ThemeData.dark().textTheme.apply(
              bodyColor: VerdisColors.text,
              displayColor: VerdisColors.text,
              fontSizeFactor: 1.0,
            ),
            appBarTheme: AppBarTheme(
              backgroundColor: VerdisColors.background,
              elevation: 0,
              iconTheme: const IconThemeData(color: VerdisColors.text),
              titleTextStyle: TextStyle(
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
