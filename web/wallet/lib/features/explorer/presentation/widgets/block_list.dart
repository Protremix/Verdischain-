import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../explorer_providers.dart';

class BlockListWidget extends ConsumerStatefulWidget {
  const BlockListWidget({super.key});

  @override
  ConsumerState<BlockListWidget> createState() => _BlockListWidgetState();
}

class _BlockListWidgetState extends ConsumerState<BlockListWidget> {
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 300) {
      ref.read(blocksProvider.notifier).loadMore();
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final blocksState = ref.watch(blocksProvider);
    final theme = Theme.of(context);

    return blocksState.when(
      loading: () => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: 8,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (_, __) => const ShimmerPlaceholder(height: 84),
      ),
      error: (error, _) => Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.redAccent),
            const SizedBox(height: 12),
            Text('Failed to load blocks', style: theme.textTheme.titleMedium),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => ref.read(blocksProvider.notifier).refresh(),
              child: const Text('Retry'),
            ),
          ],
        ),
      ),
      data: (blocks) {
        if (blocks.isEmpty) {
          return const EmptyState(
            icon: Icons.view_compact_outlined,
            title: 'No blocks found',
            subtitle: 'Waiting for new blocks from Verdis consensus...',
          );
        }

        return RefreshIndicator(
          color: theme.colorScheme.primary,
          onRefresh: () => ref.read(blocksProvider.notifier).refresh(),
          child: ListView.builder(
            controller: _scrollController,
            padding: const EdgeInsets.all(16),
            itemCount: blocks.length + 1,
            itemBuilder: (context, index) {
              if (index == blocks.length) {
                final notifier = ref.read(blocksProvider.notifier);
                if (notifier.hasMore) {
                  return const Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: Center(
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  );
                }
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  child: Center(
                    child: Text(
                      'Reached beginning of chain history',
                      style: theme.textTheme.bodySmall,
                    ),
                  ),
                );
              }

              final block = blocks[index];
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: VerdisCard(
                  onTap: () => _showBlockDetail(context, block),
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primary.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: theme.colorScheme.primary.withOpacity(0.3),
                          ),
                        ),
                        child: Icon(
                          Icons.dns_rounded,
                          color: theme.colorScheme.primary,
                          size: 22,
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  '#${block.number}',
                                  style: theme.textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: theme.colorScheme.primary,
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: theme.colorScheme.surfaceContainerHighest,
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    '${block.extrinsicCount} txs',
                                    style: theme.textTheme.labelSmall?.copyWith(
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              _shortenHash(block.hash),
                              style: theme.textTheme.bodyMedium?.copyWith(
                                fontFamily: 'Monospace',
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                            ),
                            const SizedBox(height: 6),
                            Row(
                              children: [
                                Icon(Icons.shield_outlined, size: 13, color: theme.colorScheme.primary),
                                const SizedBox(width: 4),
                                Expanded(
                                  child: Text(
                                    block.validator,
                                    style: theme.textTheme.labelSmall,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  _formatTime(block.timestamp),
                                  style: theme.textTheme.labelSmall,
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Icon(Icons.chevron_right, color: theme.colorScheme.onSurfaceVariant, size: 18),
                    ],
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }

  void _showBlockDetail(BuildContext context, BlockInfo block) {
    final theme = Theme.of(context);
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: theme.colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return DraggableScrollableSheet(
          expand: false,
          initialChildSize: 0.7,
          maxChildSize: 0.9,
          minChildSize: 0.4,
          builder: (context, scrollController) {
            return Padding(
              padding: const EdgeInsets.all(20),
              child: ListView(
                controller: scrollController,
                children: [
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: theme.colorScheme.outline,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Icon(Icons.dns_rounded, color: theme.colorScheme.primary, size: 28),
                      const SizedBox(width: 12),
                      Text(
                        'Block #${block.number}',
                        style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  _buildDetailRow(context, 'Block Height', '#${block.number}'),
                  _buildDetailRow(context, 'Block Hash', block.hash, isMonospace: true, copyable: true),
                  _buildDetailRow(context, 'Parent Hash', block.parentHash, isMonospace: true, copyable: true),
                  _buildDetailRow(context, 'Validator', block.validator),
                  _buildDetailRow(context, 'Extrinsics / Txs', '${block.extrinsicCount} transactions'),
                  _buildDetailRow(context, 'Timestamp', DateFormat('yyyy-MM-dd HH:mm:ss').format(DateTime.fromMillisecondsSinceEpoch(block.timestamp))),
                  const SizedBox(height: 20),
                  Text('Extrinsics List', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  ...block.extrinsics.map((ext) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('${ext.module}.${ext.call}', style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold)),
                              Text(ext.hash, style: theme.textTheme.labelSmall?.copyWith(fontFamily: 'Monospace')),
                            ],
                          ),
                          Icon(
                            ext.isSuccess ? Icons.check_circle : Icons.cancel,
                            color: ext.isSuccess ? Colors.green : Colors.red,
                            size: 18,
                          ),
                        ],
                      ),
                    ),
                  ),),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildDetailRow(BuildContext context, String label, String value, {bool isMonospace = false, bool copyable = false}) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: theme.textTheme.labelMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
          const SizedBox(height: 4),
          Row(
            children: [
              Expanded(
                child: SelectableText(
                  value,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontFamily: isMonospace ? 'Monospace' : null,
                  ),
                ),
              ),
            ],
          ),
          const Divider(height: 16),
        ],
      ),
    );
  }

  String _shortenHash(String hash) {
    if (hash.length <= 16) return hash;
    return '${hash.substring(0, 10)}...${hash.substring(hash.length - 8)}';
  }

  String _formatTime(int ms) {
    final dt = DateTime.fromMillisecondsSinceEpoch(ms);
    final diff = DateTime.now().difference(dt);
    if (diff.inSeconds < 60) return '${diff.inSeconds}s ago';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return DateFormat('MMM d, HH:mm').format(dt);
  }
}
