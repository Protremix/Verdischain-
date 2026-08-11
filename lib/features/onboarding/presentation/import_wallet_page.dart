import 'dart:async';
import 'package:verdis_wallet/core/router/route_names.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'onboarding_providers.dart';

/// Page to import an existing wallet via 12 or 24 word mnemonic phrase
class ImportWalletPage extends ConsumerStatefulWidget {
  const ImportWalletPage({super.key});

  @override
  ConsumerState<ImportWalletPage> createState() => _ImportWalletPageState();
}

class _ImportWalletPageState extends ConsumerState<ImportWalletPage> {
  final TextEditingController _mnemonicController = TextEditingController();

  @override
  void dispose() {
    _mnemonicController.dispose();
    super.dispose();
  }

  Future<void> _pasteFromClipboard() async {
    final data = await Clipboard.getData('text/plain');
    if (data != null && data.text != null) {
      _mnemonicController.text = data.text!;
      unawaited(ref.read(walletImportProvider.notifier).updateMnemonicInput(data.text!));
    }
  }

  @override
  Widget build(BuildContext context) {
    final importState = ref.watch(walletImportProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E0A),
      appBar: AppBar(
        title: const Text('Import Wallet'),
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
              Text(
                'Enter Secret Recovery Phrase',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFFE8F0E8),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Enter your 12 or 24-word seed phrase separated by spaces to restore your wallet.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFF8B9D8B),
                ),
              ),
              const SizedBox(height: 20),

              // Word count selector toggle
              Row(
                children: [
                  ChoiceChip(
                    label: const Text('12 Words'),
                    selected: importState.wordCount == 12,
                    onSelected: (selected) {
                      if (selected) {
                        ref.read(walletImportProvider.notifier).setWordCount(12);
                      }
                    },
                  ),
                  const SizedBox(width: 12),
                  ChoiceChip(
                    label: const Text('24 Words'),
                    selected: importState.wordCount == 24,
                    onSelected: (selected) {
                      if (selected) {
                        ref.read(walletImportProvider.notifier).setWordCount(24);
                      }
                    },
                  ),
                  const Spacer(),
                  TextButton.icon(
                    onPressed: _pasteFromClipboard,
                    icon: const Icon(Icons.content_paste, size: 18),
                    label: const Text('Paste'),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Mnemonic text field input
              TextField(
                controller: _mnemonicController,
                maxLines: 4,
                autocorrect: false,
                enableSuggestions: false,
                style: const TextStyle(
                  fontFamily: 'monospace',
                  fontSize: 15,
                  color: Color(0xFFE8F0E8),
                ),
                decoration: InputDecoration(
                  hintText: importState.wordCount == 12
                      ? 'apple banana cherry dragon elephant figure green horizon pulse solar token verdis'
                      : 'Enter 24 words separated by spaces...',
                  alignLabelWithHint: true,
                  errorText: importState.error,
                  suffixIcon: _mnemonicController.text.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear, size: 20),
                          onPressed: () {
                            _mnemonicController.clear();
                            ref
                                .read(walletImportProvider.notifier)
                                .updateMnemonicInput('');
                          },
                        )
                      : null,
                ),
                onChanged: (text) {
                  ref.read(walletImportProvider.notifier).updateMnemonicInput(text);
                },
              ),
              const SizedBox(height: 16),

              // Status card
              if (importState.isValid && importState.derivedAddress != null) ...[
                VerdisCard(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.check_circle, color: Color(0xFF00FF88), size: 20),
                          SizedBox(width: 8),
                          Text(
                            'Valid Recovery Phrase',
                            style: TextStyle(
                              color: Color(0xFF00FF88),
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Restored Address: ${importState.derivedAddress}',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: const Color(0xFF8B9D8B),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

              const Spacer(),

              // Submit button
              VerdisButton(
                label: 'Import & Continue',
                isLoading: importState.isLoading,
                onPressed: importState.isValid
                    ? () async {
                        final success = await ref
                            .read(walletImportProvider.notifier)
                            .importWallet();
                        if (success && context.mounted) {
                          // Pass imported keys to creation state or proceed to PIN setup
                          unawaited(context.push(RouteNames.pinSetup));
                        }
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
