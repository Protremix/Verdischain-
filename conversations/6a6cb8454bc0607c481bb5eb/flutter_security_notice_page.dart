import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

/// Security Notice page — user must read and agree to security rules
/// before accessing or creating a wallet.
///
/// This page appears:
/// - On first wallet creation
/// - On wallet import
/// - When opening the app if not yet agreed (per session)
class SecurityNoticePage extends ConsumerStatefulWidget {
  const SecurityNoticePage({super.key});

  @override
  ConsumerState<SecurityNoticePage> createState() => _SecurityNoticePageState();
}

class _SecurityNoticePageState extends ConsumerState<SecurityNoticePage> {
  bool _hasAgreed = false;

  void _handleContinue() {
    if (!_hasAgreed) return;

    // Navigate to PIN setup page
    context.go('/pin-setup');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E0A),
      appBar: AppBar(
        title: const Text('Security Notice'),
        centerTitle: true,
        automaticallyImplyLeading: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Warning icon
              Center(
                child: Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    color: const Color(0xFFEF4444).withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.warning_amber_rounded,
                    size: 32,
                    color: Color(0xFFEF4444),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Title
              const Center(
                child: Text(
                  'Security Notice',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFFE8F0E8),
                  ),
                ),
              ),
              const Center(
                child: Text(
                  'Read carefully before proceeding',
                  style: TextStyle(
                    fontSize: 14,
                    color: Color(0xFF8B9D8B),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Main security content
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFF1A1F1A),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF2A3A2A)),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '🔒 Your PIN is the key to your wallet.',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFFE8F0E8),
                      ),
                    ),
                    SizedBox(height: 12),
                    Text(
                      'Your wallet is protected by a PIN that you set. Even if someone obtains your 12-word mnemonic or your email, they cannot access your wallet without your PIN.',
                      style: TextStyle(
                        fontSize: 14,
                        color: Color(0xFFC8D8C8),
                        height: 1.5,
                      ),
                    ),
                    SizedBox(height: 12),
                    Text(
                      'If you lose your PIN, you will permanently lose access to your wallet. No one — not even Verdis Chain staff — can recover it for you.',
                      style: TextStyle(
                        fontSize: 14,
                        color: Color(0xFFC8D8C8),
                        height: 1.5,
                      ),
                    ),
                    SizedBox(height: 16),
                    Text(
                      'Rules:',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFFE8F0E8),
                      ),
                    ),
                    SizedBox(height: 8),
                    _SecurityRule(text: 'Never share your PIN with anyone'),
                    _SecurityRule(text: 'Never share your 12-word mnemonic with anyone'),
                    _SecurityRule(text: 'Verdis Chain staff will never ask for your PIN or mnemonic'),
                    _SecurityRule(text: 'Write down your PIN and mnemonic in a secure offline location'),
                    _SecurityRule(text: 'After 5 failed PIN attempts, your wallet will be locked for 15 minutes'),
                    SizedBox(height: 12),
                    Text(
                      'By proceeding, you acknowledge that you are solely responsible for keeping your PIN and mnemonic secure.',
                      style: TextStyle(
                        fontSize: 13,
                        color: Color(0xFF8B9D8B),
                        height: 1.5,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Agreement checkbox
              GestureDetector(
                onTap: () {
                  setState(() {
                    _hasAgreed = !_hasAgreed;
                  });
                },
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Checkbox(
                      value: _hasAgreed,
                      onChanged: (value) {
                        setState(() {
                          _hasAgreed = value ?? false;
                        });
                      },
                      activeColor: const Color(0xFF00A86B),
                      checkColor: Colors.white,
                    ),
                    const Expanded(
                      child: Padding(
                        padding: EdgeInsets.only(top: 12),
                        child: Text(
                          'I have read and understand these security rules. I know that losing my PIN means losing access to my wallet permanently.',
                          style: TextStyle(
                            fontSize: 14,
                            color: Color(0xFFE8F0E8),
                            height: 1.4,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Continue button
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: _hasAgreed ? _handleContinue : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF00A86B),
                    disabledBackgroundColor: const Color(0xFF00A86B).withOpacity(0.3),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text(
                    'I Agree — Continue',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SecurityRule extends StatelessWidget {
  const _SecurityRule({required this.text});
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.only(top: 6, right: 8),
            child: Icon(
              Icons.fiber_manual_record,
              size: 6,
              color: Color(0xFF00FF88),
            ),
          ),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                fontSize: 14,
                color: Color(0xFFC8D8C8),
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
