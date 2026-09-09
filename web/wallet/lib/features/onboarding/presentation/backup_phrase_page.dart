import 'package:verdis_wallet/core/router/route_names.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'onboarding_providers.dart';

/// Page displaying generated 12-word seed phrase for backup with security warning
class BackupPhrasePage extends ConsumerStatefulWidget {
  const BackupPhrasePage({super.key});

  @override
  ConsumerState<BackupPhrasePage> createState() => _BackupPhrasePageState();
}

class _BackupPhrasePageState extends ConsumerState<BackupPhrasePage> {
  bool _isObscured = true;

  void _copyToClipboard(String phrase) {
    Clipboard.setData(ClipboardData(text: phrase));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Seed phrase copied to clipboard. Secure it immediately!'),
        duration: Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final creationState = ref.watch(walletCreationProvider);
    final theme = Theme.of(context);
    final words = creationState.mnemonicWords;

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E0A),
      appBar: AppBar(
        title: const Text('Secret Recovery Phrase'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title & Warning
              Text(
                'Write Down Your Seed Phrase',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFFE8F0E8),
                ),
              ),
              const SizedBox(height: 8),

              // Red Warning Box
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFFCF6679).withOpacity(0.12),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFCF6679).withOpacity(0.4)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.warning_amber_rounded, color: Color(0xFFCF6679), size: 24),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'NEVER share these 12 words with anyone. Anyone with this phrase can steal your funds permanently.',
                        style: TextStyle(
                          color: Color(0xFFCF6679),
                          fontSize: 12.5,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Obscure toggle bar
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Your 12 Words',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFFE8F0E8),
                    ),
                  ),
                  TextButton.icon(
                    onPressed: () {
                      setState(() {
                        _isObscured = !_isObscured;
                      });
                    },
                    icon: Icon(_isObscured ? Icons.visibility : Icons.visibility_off, size: 18),
                    label: Text(_isObscured ? 'Reveal' : 'Hide'),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              // Grid of 12 words
              Expanded(
                child: Stack(
                  children: [
                    GridView.builder(
                      physics: const BouncingScrollPhysics(),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        childAspectRatio: 2.8,
                        crossAxisSpacing: 12,
                        mainAxisSpacing: 12,
                      ),
                      itemCount: words.length,
                      itemBuilder: (context, index) {
                        return Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            color: const Color(0xFF121712),
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: const Color(0xFF2A332A)),
                          ),
                          child: Row(
                            children: [
                              Text(
                                '${index + 1}.',
                                style: const TextStyle(
                                  color: Color(0xFF00FF88),
                                  fontWeight: FontWeight.bold,
                                  fontSize: 13,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  _isObscured ? '••••••' : words[index],
                                  style: const TextStyle(
                                    color: Color(0xFFE8F0E8),
                                    fontWeight: FontWeight.w600,
                                    fontSize: 15,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),

                    // Copy phrase floating button
                    Positioned(
                      bottom: 8,
                      right: 8,
                      child: FloatingActionButton.extended(
                        heroTag: 'copy_phrase_fab',
                        onPressed: () => _copyToClipboard(creationState.mnemonic),
                        backgroundColor: const Color(0xFF1A211A),
                        foregroundColor: const Color(0xFF00FF88),
                        icon: const Icon(Icons.copy, size: 18),
                        label: const Text('Copy Words'),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Confirmation Checkbox
              InkWell(
                onTap: () {
                  ref
                      .read(walletCreationProvider.notifier)
                      .toggleSavedConfirmed(!creationState.isSavedConfirmed);
                },
                borderRadius: BorderRadius.circular(8),
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: Row(
                    children: [
                      Checkbox(
                        value: creationState.isSavedConfirmed,
                        activeColor: const Color(0xFF00FF88),
                        onChanged: (val) {
                          ref
                              .read(walletCreationProvider.notifier)
                              .toggleSavedConfirmed(val ?? false);
                        },
                      ),
                      const Expanded(
                        child: Text(
                          'I have written down or saved my 12-word recovery phrase in a secure offline location.',
                          style: TextStyle(
                            color: Color(0xFF8B9D8B),
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Proceed Button
              VerdisButton(
                label: 'Verify Phrase',
                icon: Icons.check_circle_outline,
                onPressed: creationState.isSavedConfirmed
                    ? () {
                        context.push(RouteNames.verifyPhrase);
                      }
                    : null,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
