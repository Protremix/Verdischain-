import 'package:verdis_wallet/core/router/route_names.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'onboarding_providers.dart';

/// Page to generate a new 12-word wallet mnemonic and preview generated address
class CreateWalletPage extends ConsumerStatefulWidget {
  const CreateWalletPage({super.key});

  @override
  ConsumerState<CreateWalletPage> createState() => _CreateWalletPageState();
}

class _CreateWalletPageState extends ConsumerState<CreateWalletPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final state = ref.read(walletCreationProvider);
      if (state.mnemonic.isEmpty) {
        ref.read(walletCreationProvider.notifier).generateNewWallet();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final creationState = ref.watch(walletCreationProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E0A),
      appBar: AppBar(
        title: const Text('Create New Wallet'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: creationState.isLoading
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(color: Color(0xFF00FF88)),
                      SizedBox(height: 16),
                      Text(
                        'Generating secure cryptographic seed...',
                        style: TextStyle(color: Color(0xFF8B9D8B)),
                      ),
                    ],
                  ),
                )
              : Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header Card
                    VerdisCard(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(10),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF00FF88).withOpacity(0.15),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Icon(
                                  Icons.shield_outlined,
                                  color: Color(0xFF00FF88),
                                  size: 28,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Wallet Generated',
                                      style: theme.textTheme.headlineSmall?.copyWith(
                                        fontWeight: FontWeight.bold,
                                        color: const Color(0xFFE8F0E8),
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      'SR25519 keypair derived — matches web wallet',
                                      style: theme.textTheme.bodySmall?.copyWith(
                                        color: const Color(0xFF8B9D8B),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 20),
                          const Divider(),
                          const SizedBox(height: 12),

                          Text(
                            'Your Verdis Wallet Address',
                            style: theme.textTheme.labelMedium?.copyWith(
                              color: const Color(0xFF8B9D8B),
                            ),
                          ),
                          const SizedBox(height: 8),

                          // Display derived address
                          AddressChip(
                            address: creationState.address.isNotEmpty
                                ? creationState.address
                                : 'vrdx1...',
                            showCopy: true,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Information Box
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1A211A),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF2A332A)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Row(
                            children: [
                              Icon(Icons.info_outline, color: Color(0xFF00FF88), size: 20),
                              SizedBox(width: 8),
                              Text(
                                'Important Security Notice',
                                style: TextStyle(
                                  color: Color(0xFFE8F0E8),
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Next, you will be shown your 12-word secret recovery phrase. You must write it down and keep it in a safe, offline location.',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: const Color(0xFF8B9D8B),
                              height: 1.4,
                            ),
                          ),
                        ],
                      ),
                    ),

                    const Spacer(),

                    // Re-generate button (optional)
                    Center(
                      child: TextButton.icon(
                        onPressed: () {
                          ref.read(walletCreationProvider.notifier).generateNewWallet();
                        },
                        icon: const Icon(Icons.refresh, size: 18),
                        label: const Text('Generate Different Phrase'),
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Proceed to backup
                    VerdisButton(
                      label: 'Backup Recovery Phrase',
                      icon: Icons.lock_reset_rounded,
                      onPressed: creationState.mnemonic.isEmpty
                          ? null
                          : () {
                              context.push(RouteNames.backupPhrase);
                            },
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}
