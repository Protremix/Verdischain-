import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../../domain/nft_repository.dart';

/// Card widget displaying an NFT thumbnail, collection label, and token name/ID
class NftCard extends StatelessWidget {

  const NftCard({
    super.key,
    required this.asset,
    this.onTap,
  });
  final NftAssetModel asset;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return VerdisCard(
      onTap: onTap,
      padding: EdgeInsets.zero,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. NFT Image Preview with AspectRatio 1:1
          ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
            child: AspectRatio(
              aspectRatio: 1.0,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  CachedNetworkImage(
                    imageUrl: asset.imageUrl,
                    fit: BoxFit.cover,
                    placeholder: (context, url) => Container(
                      color: theme.colorScheme.surfaceContainerHighest,
                      child: const Center(
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                    ),
                    errorWidget: (context, url, error) => Container(
                      decoration: const BoxDecoration(
                        gradient: LinearGradient(
                          colors: [Color(0xFF00FF88), Color(0xFF00E5FF)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                      ),
                      child: const Center(
                        child: Icon(
                          Icons.image_not_supported_outlined,
                          color: Colors.black54,
                          size: 32,
                        ),
                      ),
                    ),
                  ),

                  // Rarity Tag Badge
                  if (asset.rarityRank != null)
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.75),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: theme.colorScheme.primary.withOpacity(0.6),
                            width: 1,
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.bolt,
                              size: 12,
                              color: theme.colorScheme.primary,
                            ),
                            const SizedBox(width: 2),
                            Text(
                              'Rank #${asset.rarityRank}',
                              style: theme.textTheme.labelSmall?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 10,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),

          // 2. Collection & Asset Metadata
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  asset.collectionName,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                    fontSize: 11,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  asset.name,
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 6),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        '#${asset.assetId}',
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.primary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    Icon(
                      Icons.arrow_forward_ios,
                      size: 12,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
