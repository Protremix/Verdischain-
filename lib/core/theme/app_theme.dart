import 'package:flutter/material.dart';

/// Verdis Wallet Theme — Dark eco-green design
/// Primary: #00C853 (eco green)
/// Background: #0A0E0A (near black with green tint)
/// Surface: #121712
/// Accent: #00FF88
class AppTheme {
  AppTheme._();

  static const Color _primary = Color(0xFF00FF88);
  static const Color _primaryLight = Color(0xFF00FF88);
  static const Color _background = Color(0xFF0A0E0A);
  static const Color _surface = Color(0xFF121712);
  static const Color _surfaceVariant = Color(0xFF1A211A);
  static const Color _error = Color(0xFFCF6679);
  static const Color _onSurface = Color(0xFFE8F0E8);
  static const Color _onSurfaceVariant = Color(0xFF8B9D8B);
  static const Color _outline = Color(0xFF2A332A);

  static ThemeData get darkTheme {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: _primary,
      brightness: Brightness.dark,
      primary: _primary,
      onPrimary: Colors.black,
      secondary: _primaryLight,
      onSecondary: Colors.black,
      surface: _surface,
      onSurface: _onSurface,
      error: _error,
      onError: Colors.black,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: _background,
      canvasColor: _surface,
      fontFamily: 'VerdisSans',

      // App Bar
      appBarTheme: const AppBarTheme(
        backgroundColor: _background,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: _onSurface,
          fontSize: 20,
          fontWeight: FontWeight.w600,
        ),
        iconTheme: IconThemeData(color: _onSurface),
      ),

      // Card
      cardTheme: CardTheme(
        color: _surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: _outline, width: 1),
        ),
        margin: EdgeInsets.zero,
      ),

      // Elevated Button
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: _primary,
          foregroundColor: Colors.black,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      // Outlined Button
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: _primary,
          side: const BorderSide(color: _primary, width: 1.5),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),

      // Text Button
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: _primary,
        ),
      ),

      // Input Decoration
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: _surfaceVariant,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _outline),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _outline),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _error),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        labelStyle: const TextStyle(color: _onSurfaceVariant),
        hintStyle: const TextStyle(color: _onSurfaceVariant, fontSize: 14),
      ),

      // Bottom Navigation
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: _surface,
        selectedItemColor: _primary,
        unselectedItemColor: _onSurfaceVariant,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
        showUnselectedLabels: true,
        selectedLabelStyle: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
        unselectedLabelStyle: TextStyle(fontSize: 12),
      ),

      // Floating Action Button
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: _primary,
        foregroundColor: Colors.black,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),

      // Divider
      dividerTheme: const DividerThemeData(
        color: _outline,
        thickness: 1,
        space: 1,
      ),

      // ListTile
      listTileTheme: const ListTileThemeData(
        iconColor: _primary,
        textColor: _onSurface,
      ),

      // Snackbar
      snackBarTheme: SnackBarThemeData(
        backgroundColor: _surface,
        contentTextStyle: const TextStyle(color: _onSurface),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),

      // Chip
      chipTheme: ChipThemeData(
        backgroundColor: _surfaceVariant,
        selectedColor: _primary,
        labelStyle: const TextStyle(color: _onSurface, fontSize: 13),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        side: const BorderSide(color: _outline),
      ),

      // Progress Indicator
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: _primary,
        linearTrackColor: _surfaceVariant,
      ),

      // Switch
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) return _primary;
          return _onSurfaceVariant;
        }),
        trackColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) return _primary.withOpacity(0.3);
          return _surfaceVariant;
        }),
      ),

      // Text
      textTheme: const TextTheme(
        displayLarge: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: _onSurface),
        displayMedium: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: _onSurface),
        displaySmall: TextStyle(fontSize: 24, fontWeight: FontWeight.w600, color: _onSurface),
        headlineLarge: TextStyle(fontSize: 22, fontWeight: FontWeight.w600, color: _onSurface),
        headlineMedium: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: _onSurface),
        headlineSmall: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: _onSurface),
        titleLarge: TextStyle(fontSize: 18, fontWeight: FontWeight.w500, color: _onSurface),
        titleMedium: TextStyle(fontSize: 16, fontWeight: FontWeight.w500, color: _onSurface),
        titleSmall: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: _onSurface),
        bodyLarge: TextStyle(fontSize: 16, color: _onSurface),
        bodyMedium: TextStyle(fontSize: 14, color: _onSurface),
        bodySmall: TextStyle(fontSize: 12, color: _onSurfaceVariant),
        labelLarge: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: _onSurface),
        labelMedium: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: _onSurfaceVariant),
        labelSmall: TextStyle(fontSize: 11, color: _onSurfaceVariant),
      ),
    );
  }
}
