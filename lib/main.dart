import 'package:flutter/material.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Set ErrorWidget GLOBALLY before runApp — catches ANY widget build failure
  ErrorWidget.builder = (FlutterErrorDetails details) {
    return Material(
      color: const Color(0xFF1A0000),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'RENDER ERROR: ${details.exception}',
            style: const TextStyle(color: Color(0xFFFF6B6B), fontSize: 14),
          ),
        ),
      ),
    );
  };

  // BYPASS everything — no providers, no router, no theme, no init
  // Just show a green screen with text. If this renders, Flutter works
  // and the issue is in our app structure. If not, the issue is native.
  runApp(
    const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        backgroundColor: Color(0xFF00C853),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'FLUTTER WORKS',
                style: TextStyle(
                  fontSize: 40,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              SizedBox(height: 20),
              Text(
                'Build 46 — Diagnostic',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.white70,
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}
