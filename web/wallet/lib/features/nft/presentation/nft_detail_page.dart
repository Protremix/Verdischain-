import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:verdis_wallet/core/config/network_config.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../domain/nft_repository.dart';
import 'nft_providers.dart';

/// Detailed NFT view featuring full artwork preview, attributes list,
/// owner history, transfer sheet modal, and explorer link
class NftDetailPage extends ConsumerStatefulWidget {

  const NftDetailPage({
    super.key,
    required this.collectionId,
    required this.assetId,
  });
  final String collectionId;
  final String assetId;

  @override
  ConsumerState<NftDetailPage> createState() => _NftDetailPageState();
}

class _NftDetailPageState extends ConsumerState<NftDetailPage> {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final assetAsync = ref.watch(
      nftDetailProvider((
        collectionId: widget.collectionId,
        assetId: widget.assetId,
      ),),
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('NFT Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.open_in_new),
            tooltip: 'View on Explorer',
            onPressed: () => _openExplorer(context),
          ),
        ],
      ),
      body: assetAsync.when(
        data: (asset) {
          if (asset == null) {
            return const EmptyState(
              icon: Icons.error_outline,
              title: 'NFT Metadata Not Found',
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 1. Large Image Artwork
                ClipRRect(
                  borderRadius: BorderRadius.circular(20),
                  child: AspectRatio(
                    aspectRatio: 1.0,
                    child: CachedNetworkImage(
                      imageUrl: asset.imageUrl,
                      fit: BoxFit.cover,
                      placeholder: (_, __) => Container(
                        color: theme.colorScheme.surfaceContainerHighest,
                        child: const Center(
                          child: CircularProgressIndicator(),
                        ),
                      ),
                      errorWidget: (_, __, ___) => Container(
                        color: theme.colorScheme.surfaceContainerHighest,
                        child: const Icon(Icons.broken_image, size: 64),
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 20),

                // 2. Collection Label & NFT Title
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      asset.collectionName,
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    if (asset.rarityRank != null)
                      Chip(
                        avatar: Icon(
                          Icons.bolt,
                          size: 16,
                          color: theme.colorScheme.primary,
                        ),
                        label: Text('Rarity #${asset.rarityRank}'),
                      ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  asset.name,
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),

                const SizedBox(height: 16),

                // 3. Owner & Creator Chips
                VerdisCard(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Owner', style: theme.textTheme.bodySmall),
                          AddressChip(address: asset.ownerAddress, showCopy: true),
                        ],
                      ),
                      const SizedBox(height: 12),
                      const Divider(),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Creator', style: theme.textTheme.bodySmall),
                          AddressChip(address: asset.creatorAddress, showCopy: true),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),

                // 4. Description Section
                if (asset.description.isNotEmpty) ...[
                  Text(
                    'Description',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    asset.description,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 24),
                ],

                // 5. Attributes / Traits Grid
                if (asset.attributes.isNotEmpty) ...[
                  Text(
                    'Attributes & Traits',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      childAspectRatio: 2.2,
                      crossAxisSpacing: 10,
                      mainAxisSpacing: 10,
                    ),
                    itemCount: asset.attributes.length,
                    itemBuilder: (context, index) {
                      final attr = asset.attributes[index];
                      return Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: theme.colorScheme.outline),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              attr.traitType.toUpperCase(),
                              style: theme.textTheme.labelSmall?.copyWith(
                                color: theme.colorScheme.primary,
                                fontSize: 10,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              attr.value,
                              style: theme.textTheme.titleSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            if (attr.rarityPercent != null)
                              Text(
                                '${attr.rarityPercent}% have this trait',
                                style: theme.textTheme.labelSmall,
                              ),
                          ],
                        ),
                      );
                    },
                  ),
                  const SizedBox(height: 24),
                ],

                // 6. Action Toolbar
                Row(
                  children: [
                    Expanded(
                      child: VerdisButton(
                        label: 'Transfer NFT',
                        icon: Icons.send_rounded,
                        onPressed: asset.isTransferable
                            ? () => _openTransferSheet(context, asset)
                            : null,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: VerdisButton(
                        label: 'Explorer',
                        icon: Icons.open_in_new,
                        isOutlined: true,
                        onPressed: () => _openExplorer(context),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, __) => Center(child: Text('Error: $err')),
      ),
    );
  }

  void _openTransferSheet(BuildContext context, NftAssetModel asset) {
    final recipientCtrl = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (modalCtx) => Consumer(
        builder: (context, ref, _) {
          final transferState = ref.watch(nftTransferNotifierProvider);
          final notifier = ref.read(nftTransferNotifierProvider.notifier);

          return Padding(
            padding: EdgeInsets.only(
              left: 20,
              right: 20,
              top: 24,
              bottom: MediaQuery.of(modalCtx).viewInsets.bottom + 24,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Transfer ${asset.name}',
                  style: Theme.of(modalCtx).textTheme.headlineSmall,
                ),
                const SizedBox(height: 8),
                Text(
                  'Collection: ${asset.collectionName} (#${asset.assetId})',
                  style: Theme.of(modalCtx).textTheme.bodySmall,
                ),
                const SizedBox(height: 20),
                TextField(
                  controller: recipientCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Recipient Address',
                    hintText: 'Enter 0x... or Verdis address',
                    prefixIcon: Icon(Icons.person_outline),
                  ),
                ),
                if (transferState.errorMessage != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    transferState.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(modalCtx).colorScheme.error,
                      fontSize: 12,
                    ),
                  ),
                ],
                const SizedBox(height: 24),
                VerdisButton(
                  label: 'Confirm Transfer',
                  icon: Icons.send,
                  isLoading: transferState.isLoading,
                  onPressed: () async {
                    final recipient = recipientCtrl.text.trim();
                    if (recipient.isEmpty) return;

                    final ok = await notifier.transferNft(
                      collectionId: asset.collectionId,
                      assetId: asset.assetId,
                      recipient: recipient,
                    );

                    if (ok && modalCtx.mounted) {
                      Navigator.pop(modalCtx);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            '${asset.name} successfully transferred to ${recipient.substring(0, 8)}...',
                          ),
                          backgroundColor:
                              Theme.of(context).colorScheme.primary,
                        ),
                      );
                    }
                  },
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _openExplorer(BuildContext context) async {
    final url =
        '${NetworkConfig.explorerUrl}/nfts/${widget.collectionId}/${widget.assetId}';
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Explorer URL: $url')),
        );
      }
    }
  }
}
