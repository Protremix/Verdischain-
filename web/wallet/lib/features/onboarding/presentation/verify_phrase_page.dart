import 'package:verdis_wallet/core/router/route_names.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'onboarding_providers.dart';

/// Interactive seed phrase verification page (shuffled word selection)
class VerifyPhrasePage extends ConsumerStatefulWidget {
  const VerifyPhrasePage({super.key});

  @override
  ConsumerState<VerifyPhrasePage> createState() => _VerifyPhrasePageState();
}

class _VerifyPhrasePageState extends ConsumerState<VerifyPhrasePage> {
  List<String> _shuffledWords = [];
  final List<String> _selectedWords = [];
  bool _isVerified = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _initShuffledWords();
  }

  void _initShuffledWords() {
    final originalWords = ref.read(walletCreationProvider).mnemonicWords;
    _shuffledWords = List<String>.from(originalWords)..shuffle();
    _selectedWords.clear();
    _isVerified = false;
    _errorMessage = null;
  }

  void _selectWord(String word) {
    if (_selectedWords.contains(word)) return;
    setState(() {
      _selectedWords.add(word);
      _errorMessage = null;
    });

    _checkVerification();
  }

  void _unselectWord(String word) {
    setState(() {
      _selectedWords.remove(word);
      _isVerified = false;
      _errorMessage = null;
    });
  }

  void _checkVerification() {
    final originalWords = ref.read(walletCreationProvider).mnemonicWords;
    if (_selectedWords.length == originalWords.length) {
      bool matches = true;
      for (int i = 0; i < originalWords.length; i++) {
        if (_selectedWords[i] != originalWords[i]) {
          matches = false;
          break;
        }
      }

      setState(() {
        _isVerified = matches;
        if (!matches) {
          _errorMessage = 'Incorrect word order. Please tap Reset and try again.';
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final originalWords = ref.watch(walletCreationProvider).mnemonicWords;
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E0A),
      appBar: AppBar(
        title: const Text('Verify Recovery Phrase'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Reset order',
            onPressed: () {
              setState(() {
                _initShuffledWords();
              });
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Confirm Your Words',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFFE8F0E8),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Tap each word in the exact numbered order you wrote them down.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFF8B9D8B),
                ),
              ),
              const SizedBox(height: 20),

              // Selected Slots Container
              Container(
                constraints: const BoxConstraints(minHeight: 160),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF121712),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: _isVerified
                        ? const Color(0xFF00FF88)
                        : _errorMessage != null
                            ? const Color(0xFFCF6679)
                            : const Color(0xFF2A332A),
                    width: _isVerified || _errorMessage != null ? 2 : 1,
                  ),
                ),
                child: Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: List.generate(originalWords.length, (index) {
                    final hasWord = index < _selectedWords.length;
                    final word = hasWord ? _selectedWords[index] : '';

                    return InkWell(
                      onTap: hasWord ? () => _unselectWord(word) : null,
                      borderRadius: BorderRadius.circular(8),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: hasWord
                              ? const Color(0xFF00FF88).withOpacity(0.2)
                              : const Color(0xFF1A211A),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: hasWord ? const Color(0xFF00FF88) : const Color(0xFF2A332A),
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              '${index + 1}. ',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: hasWord ? const Color(0xFF00FF88) : const Color(0xFF8B9D8B),
                              ),
                            ),
                            Text(
                              word.isNotEmpty ? word : '___',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: hasWord ? const Color(0xFFE8F0E8) : const Color(0xFF8B9D8B),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }),
                ),
              ),

              if (_errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(
                  _errorMessage!,
                  style: const TextStyle(
                    color: Color(0xFFCF6679),
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],

              const SizedBox(height: 24),
              Text(
                'Available Words',
                style: theme.textTheme.labelMedium?.copyWith(
                  color: const Color(0xFF8B9D8B),
                ),
              ),
              const SizedBox(height: 12),

              // Shuffled Bank Chips
              Expanded(
                child: SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  child: Wrap(
                    spacing: 10,
                    runSpacing: 10,
                    children: _shuffledWords.map((word) {
                      final isSelected = _selectedWords.contains(word);
                      return FilterChip(
                        label: Text(word),
                        selected: isSelected,
                        onSelected: isSelected ? null : (_) => _selectWord(word),
                        selectedColor: const Color(0xFF2A332A),
                        backgroundColor: const Color(0xFF1A211A),
                        labelStyle: TextStyle(
                          color: isSelected ? const Color(0xFF8B9D8B) : const Color(0xFFE8F0E8),
                          fontWeight: FontWeight.w600,
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ),

              // Proceed Button
              VerdisButton(
                label: 'Continue to Biometrics',
                icon: Icons.fingerprint,
                onPressed: _isVerified
                    ? () {
                        context.push(RouteNames.biometricSetup);
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
