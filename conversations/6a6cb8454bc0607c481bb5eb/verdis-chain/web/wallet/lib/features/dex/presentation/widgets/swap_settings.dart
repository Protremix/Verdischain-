import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../dex_providers.dart';

/// Modal bottom sheet for configuring DEX slippage, deadline, and expert mode
class SwapSettingsSheet extends ConsumerWidget {
  const SwapSettingsSheet({super.key});

  static Future<void> show(BuildContext context) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => const SwapSettingsSheet(),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final slippage = ref.watch(slippageProvider);
    final deadline = ref.watch(deadlineProvider);
    final expertMode = ref.watch(expertModeProvider);

    final presets = [0.1, 0.5, 1.0, 3.0];

    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: theme.colorScheme.onSurfaceVariant.withOpacity(0.3),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Title
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Swap Settings',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.close),
                onPressed: () => Navigator.of(context).pop(),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // Section 1: Slippage Tolerance
          Row(
            children: [
              Text(
                'Slippage Tolerance',
                style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
              ),
              const SizedBox(width: 6),
              Tooltip(
                message: 'Transaction reverts if price changes unfavorably by more than this percentage.',
                child: Icon(Icons.info_outline, size: 16, color: theme.colorScheme.onSurfaceVariant),
              ),
              const Spacer(),
              Text(
                '${slippage.toStringAsFixed(1)}%',
                style: theme.textTheme.titleMedium?.copyWith(
                  color: theme.colorScheme.primary,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Preset Chips
          Row(
            children: [
              ...presets.map((preset) {
                final isSelected = (slippage == preset);
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text('$preset%'),
                    selected: isSelected,
                    onSelected: (_) {
                      ref.read(slippageProvider.notifier).state = preset;
                    },
                    selectedColor: theme.colorScheme.primary,
                    labelStyle: TextStyle(
                      color: isSelected ? Colors.black : theme.colorScheme.onSurface,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                );
              }),
            ],
          ),
          const SizedBox(height: 12),

          // Slippage Slider (0.1% - 50.0%)
          Slider(
            value: slippage.clamp(0.1, 50.0),
            min: 0.1,
            max: 50.0,
            divisions: 499,
            activeColor: slippage > 5.0 ? theme.colorScheme.error : theme.colorScheme.primary,
            label: '${slippage.toStringAsFixed(1)}%',
            onChanged: (val) {
              ref.read(slippageProvider.notifier).state = double.parse(val.toStringAsFixed(1));
            },
          ),

          // Warning for high slippage
          if (slippage > 5.0) ...[
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: theme.colorScheme.error.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: theme.colorScheme.error.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  Icon(Icons.warning_amber_rounded, color: theme.colorScheme.error, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'High slippage tolerance! Your transaction may be frontrun.',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.error,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],

          const Divider(height: 32),

          // Section 2: Transaction Deadline Timer
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Tx Deadline',
                    style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
                  ),
                  Text(
                    'Reverts if pending for longer',
                    style: theme.textTheme.bodySmall,
                  ),
                ],
              ),
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.remove_circle_outline),
                    onPressed: deadline > 1
                        ? () => ref.read(deadlineProvider.notifier).state = deadline - 1
                        : null,
                  ),
                  Container(
                    width: 48,
                    alignment: Alignment.center,
                    child: Text(
                      '$deadline m',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.add_circle_outline),
                    onPressed: deadline < 60
                        ? () => ref.read(deadlineProvider.notifier).state = deadline + 1
                        : null,
                  ),
                ],
              ),
            ],
          ),

          const Divider(height: 32),

          // Section 3: Expert Mode Toggle
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Expert Mode',
                      style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Bypass high price impact warnings and confirmation popups.',
                      style: theme.textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              Switch(
                value: expertMode,
                onChanged: (val) {
                  ref.read(expertModeProvider.notifier).state = val;
                },
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Close / Apply Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Save & Close'),
            ),
          ),
        ],
      ),
    );
  }
}
