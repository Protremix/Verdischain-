import 'package:flutter/material.dart';
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
                      'Powered by sr25519 \u2022 SS58 909 \u2022 BIP39',
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
