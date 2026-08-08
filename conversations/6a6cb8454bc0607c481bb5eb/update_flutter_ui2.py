#!/usr/bin/env python3
"""Update Flutter wallet screens to match Verdis Chain website design."""

BASE = '/opt/verdis-wallet/mobile'

# 4. Update onboarding_screen.dart
onboarding = '''import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/wallet_service.dart';
import '../widgets/verdis_button.dart';
import 'dashboard_screen.dart';

// ignore_for_file: use_build_context_synchronously

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fade;
  late Animation<Offset> _slide;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _fade = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );
    _slide = Tween<Offset>(begin: const Offset(0, 0.3), end: Offset.zero).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
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
        child: SafeArea(
          child: FadeTransition(
            opacity: _fade,
            child: SlideTransition(
              position: _slide,
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Logo with glow
                    Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF16a34a).withOpacity(0.25),
                            blurRadius: 25,
                            spreadRadius: 3,
                          ),
                        ],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(20),
                        child: Image.asset(
                          'assets/images/verdis-logo-white.png',
                          fit: BoxFit.contain,
                        ),
                      ),
                    ),
                    const SizedBox(height: 32),
                    ShaderMask(
                      shaderCallback: (bounds) => const LinearGradient(
                        colors: [Color(0xFF16a34a), Color(0xFF84fe87)],
                      ).createShader(bounds),
                      child: Text(
                        'Verdis Wallet',
                        style: GoogleFonts.spaceGrotesk(
                          fontSize: 28,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Your gateway to the Verdis Chain ecosystem. Create a new wallet or import an existing one.',
                      textAlign: TextAlign.center,
                      style: GoogleFonts.inter(
                        color: const Color(0xFF94a3b8),
                        fontSize: 14,
                        height: 1.5,
                      ),
                    ),
                    const SizedBox(height: 48),
                    _buildActionCard(
                      icon: Icons.add_circle_outline,
                      title: 'Create New Wallet',
                      subtitle: 'Generate a new 12-word mnemonic',
                      onTap: () => _showCreateWallet(context),
                    ),
                    const SizedBox(height: 16),
                    _buildActionCard(
                      icon: Icons.download_for_offline_outlined,
                      title: 'Import Wallet',
                      subtitle: 'Restore from 12-word mnemonic',
                      onTap: () => _showImportWallet(context),
                    ),
                    const SizedBox(height: 32),
                    Text(
                      'Powered by sr25519 \\u2022 SS58 909 \\u2022 BIP39',
                      style: GoogleFonts.inter(
                        color: const Color(0xFF475569),
                        fontSize: 11,
                      ),
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

  Widget _buildActionCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0D1410), Color(0xFF152017)],
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.2)),
        ),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF16a34a), Color(0xFF15803d)],
                ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: Colors.white, size: 24),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: GoogleFonts.spaceGrotesk(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      color: const Color(0xFF94a3b8),
                    ),
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Color(0xFF16a34a), size: 24),
          ],
        ),
      ),
    );
  }

  void _showCreateWallet(BuildContext context) {
    final walletService = Provider.of<WalletService>(context, listen: false);
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => AlertDialog(
        backgroundColor: const Color(0xFF0D1410),
        title: Text('Creating Wallet', style: GoogleFonts.spaceGrotesk(color: Colors.white)),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(color: Color(0xFF16a34a)),
            SizedBox(height: 16),
            Text(
              'Generating BIP39 mnemonic and deriving sr25519 address...',
              style: TextStyle(color: Color(0xFF94a3b8), fontSize: 13),
            ),
          ],
        ),
      ),
    );

    walletService.createNewWallet('My Wallet').then((account) {
      Navigator.pop(context);
      if (account != null) {
        _showMnemonicDialog(context, walletService.lastGeneratedMnemonic);
      } else if (walletService.errorMessage != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(walletService.errorMessage!),
            backgroundColor: const Color(0xFFEF4444),
          ),
        );
      }
    });
  }

  void _showMnemonicDialog(BuildContext context, String mnemonic) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => AlertDialog(
        backgroundColor: const Color(0xFF0D1410),
        title: Text('Save Your Mnemonic', style: GoogleFonts.spaceGrotesk(color: Colors.white)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF152017), Color(0xFF0D1410)],
                ),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.3)),
              ),
              child: Text(
                mnemonic,
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 14,
                  color: Colors.white,
                  height: 1.8,
                  letterSpacing: 0.5,
                ),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Write down these 12 words and keep them safe. Never share them with anyone.',
              style: TextStyle(color: Color(0xFFEF4444), fontSize: 12),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(dialogContext);
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const DashboardScreen()),
              );
            },
            child: const Text('I Saved It', style: TextStyle(color: Color(0xFF16a34a))),
          ),
        ],
      ),
    );
  }

  void _showImportWallet(BuildContext context) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        backgroundColor: const Color(0xFF0D1410),
        title: Text('Import Wallet', style: GoogleFonts.spaceGrotesk(color: Colors.white)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Enter your 12-word mnemonic phrase',
              style: GoogleFonts.inter(color: const Color(0xFF94a3b8), fontSize: 13),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: controller,
              maxLines: 3,
              style: GoogleFonts.jetBrainsMono(fontSize: 13, color: Colors.white),
              decoration: InputDecoration(
                hintText: 'word1 word2 word3...',
                hintStyle: TextStyle(color: const Color(0xFF475569), fontSize: 13),
                filled: true,
                fillColor: const Color(0xFF152017),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: const Color(0xFF16a34a).withOpacity(0.3)),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Color(0xFF16a34a)),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF94a3b8))),
          ),
          TextButton(
            onPressed: () async {
              final walletService = Provider.of<WalletService>(context, listen: false);
              Navigator.pop(dialogContext);
              final account = await walletService.importWallet('Imported', controller.text.trim());
              if (account != null && context.mounted) {
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(builder: (_) => const DashboardScreen()),
                );
              } else if (walletService.errorMessage != null && context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(walletService.errorMessage!),
                    backgroundColor: const Color(0xFFEF4444),
                  ),
                );
              }
            },
            child: const Text('Import', style: TextStyle(color: Color(0xFF16a34a))),
          ),
        ],
      ),
    );
  }
}
'''
open(f'{BASE}/lib/screens/onboarding_screen.dart', 'w').write(onboarding)
print("Updated onboarding_screen.dart")

# 5. Update balance_card.dart with gradient
balance_card = '''import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class BalanceCard extends StatelessWidget {
  final double balance;
  final String address;
  final VoidCallback? onRefresh;

  const BalanceCard({
    super.key,
    required this.balance,
    required this.address,
    this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF0D1410), Color(0xFF152017), Color(0xFF0D1410)],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.15)),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF16a34a).withOpacity(0.08),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'TOTAL BALANCE',
                style: GoogleFonts.inter(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: const Color(0xFF94a3b8),
                  letterSpacing: 1.5,
                ),
              ),
              if (onRefresh != null)
                GestureDetector(
                  onTap: onRefresh,
                  child: const Icon(Icons.refresh, color: Color(0xFF16a34a), size: 18),
                ),
            ],
          ),
          const SizedBox(height: 8),
          ShaderMask(
            shaderCallback: (bounds) => const LinearGradient(
              colors: [Color(0xFF16a34a), Color(0xFF84fe87), Color(0xFF00a86b)],
            ).createShader(bounds),
            child: Text(
              balance.toStringAsFixed(4),
              style: GoogleFonts.spaceGrotesk(
                fontSize: 36,
                fontWeight: FontWeight.w700,
                color: Colors.white,
              ),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'VRDX',
            style: GoogleFonts.inter(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: const Color(0xFF16a34a),
            ),
          ),
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFF040806),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.1)),
            ),
            child: Row(
              children: [
                const Icon(Icons.account_circle, color: Color(0xFF16a34a), size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    address,
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 11,
                      color: const Color(0xFF94a3b8),
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
'''
open(f'{BASE}/lib/widgets/balance_card.dart', 'w').write(balance_card)
print("Updated balance_card.dart")

# 6. Update verdis_button.dart with gradient
verdis_btn = '''import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class VerdisButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;
  final bool isPrimary;
  final IconData? icon;
  final bool isLoading;

  const VerdisButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.isPrimary = true,
    this.icon,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isPrimary) {
      return Container(
        width: double.infinity,
        height: 52,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            begin: Alignment.centerLeft,
            end: Alignment.centerRight,
            colors: [Color(0xFF16a34a), Color(0xFF15803d)],
          ),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: const Color(0xFF16a34a).withOpacity(0.3),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: isLoading ? null : onPressed,
            borderRadius: BorderRadius.circular(12),
            child: Center(
              child: isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        if (icon != null) ...[
                          Icon(icon, color: Colors.white, size: 20),
                          const SizedBox(width: 8),
                        ],
                        Text(
                          label,
                          style: GoogleFonts.inter(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
            ),
          ),
        ),
      );
    } else {
      return Container(
        width: double.infinity,
        height: 52,
        decoration: BoxDecoration(
          color: const Color(0xFF0D1410),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.3)),
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: isLoading ? null : onPressed,
            borderRadius: BorderRadius.circular(12),
            child: Center(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (icon != null) ...[
                    Icon(icon, color: const Color(0xFF16a34a), size: 20),
                    const SizedBox(width: 8),
                  ],
                  Text(
                    label,
                    style: GoogleFonts.inter(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: const Color(0xFF16a34a),
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
}
'''
open(f'{BASE}/lib/widgets/verdis_button.dart', 'w').write(verdis_btn)
print("Updated verdis_button.dart")

print("Done with onboarding, balance_card, verdis_button")
