import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'tokens_providers.dart';

/// Import Token Screen for looking up custom tokens by ID/address and importing them
class ImportTokenPage extends ConsumerStatefulWidget {
  const ImportTokenPage({super.key});

  @override
  ConsumerState<ImportTokenPage> createState() => _ImportTokenPageState();
}

class _ImportTokenPageState extends ConsumerState<ImportTokenPage> {
  final TextEditingController _inputController = TextEditingController();

  @override
  void dispose() {
    _inputController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final importState = ref.watch(importTokenNotifierProvider);
    final notifier = ref.read(importTokenNotifierProvider.notifier);

    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Info Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: theme.colorScheme.outline),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    color: theme.colorScheme.primary,
                    size: 24,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Import custom tokens or assets on the Verdis network by pasting their Asset ID or smart contract address.',
                      style: theme.textTheme.bodyMedium,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Token ID / Address Input Field
            Text(
              'Token ID or Contract Address',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _inputController,
              onChanged: (val) {
                if (val.trim().length >= 3) {
                  notifier.fetchTokenMetadata(val);
                }
              },
              decoration: InputDecoration(
                hintText: 'e.g. 1024 or 0x7e8f...9d0c',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.paste_rounded),
                      tooltip: 'Paste from clipboard',
                      onPressed: () {
                        // Simulated paste
                        _inputController.text =
                            '0x8f3c2b1a9e0d7c6b5a4321098765432109876543';
                        notifier.fetchTokenMetadata(_inputController.text);
                      },
                    ),
                    if (_inputController.text.isNotEmpty)
                      IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _inputController.clear();
                          notifier.reset();
                        },
                      ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Loading state
            if (importState.isLoading) ...[
              const ShimmerPlaceholder(height: 140),
            ],

            // Error state
            if (importState.errorMessage != null && !importState.isLoading) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: theme.colorScheme.error.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: theme.colorScheme.error),
                ),
                child: Row(
                  children: [
                    Icon(Icons.warning_amber_rounded,
                        color: theme.colorScheme.error,),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        importState.errorMessage!,
                        style: TextStyle(color: theme.colorScheme.error),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            // Preview Token Card when fetched
            if (importState.previewToken != null && !importState.isLoading) ...[
              Text(
                'Token Preview',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),

              VerdisCard(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 52,
                          height: 52,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: LinearGradient(
                              colors: importState.previewToken!.gradientColors
                                  .map((c) => Color(c))
                                  .toList(),
                            ),
                          ),
                          child: Center(
                            child: Text(
                              importState.previewToken!.symbol,
                              style: const TextStyle(
                                color: Colors.black,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                importState.previewToken!.name,
                                style: theme.textTheme.headlineSmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                importState.previewToken!.symbol,
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  color: theme.colorScheme.onSurfaceVariant,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 12),
                    _buildPreviewRow(context, 'Decimals',
                        '${importState.previewToken!.decimals}',),
                    const SizedBox(height: 8),
                    _buildPreviewRow(context, 'Contract/Asset ID',
                        importState.previewToken!.id,),
                    const SizedBox(height: 8),
                    _buildPreviewRow(
                      context,
                      'Estimated Price',
                      '\$${importState.previewToken!.usdPrice.toStringAsFixed(2)} USD',
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Security Warning Box
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: theme.colorScheme.outline),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.shield_outlined,
                      size: 20,
                      color: theme.colorScheme.primary,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Anyone can create custom tokens. Always verify the contract address before importing.',
                        style: theme.textTheme.bodySmall,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              // Add to Wallet Action Button
              VerdisButton(
                label: 'Add Token to Wallet',
                icon: Icons.add_circle_outline,
                isLoading: importState.isLoading,
                onPressed: () async {
                  final success = await notifier.confirmImport();
                  if (success && context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                          '${importState.previewToken!.name} successfully added to wallet!',
                        ),
                        backgroundColor: theme.colorScheme.primary,
                      ),
                    );
                    _inputController.clear();
                    notifier.reset();
                  }
                },
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPreviewRow(BuildContext context, String label, String value) {
    final theme = Theme.of(context);
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: theme.textTheme.bodySmall),
        Text(
          value,
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}
