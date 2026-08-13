import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import '../../domain/nft_repository.dart';
import '../nft_detail_page.dart';
import 'nft_card.dart';

/// Grid view of NFTs with staggered flutter_animate animations
class NftGallery extends StatelessWidget {

  const NftGallery({
    super.key,
    required this.assets,
    this.isLoading = false,
    this.onRefresh,
  });
  final List<NftAssetModel> assets;
  final bool isLoading;
  final VoidCallback? onRefresh;

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          childAspectRatio: 0.72,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
        ),
        itemCount: 4,
        itemBuilder: (_, __) => const ShimmerPlaceholder(
          height: 240,
          borderRadius: 16,
        ),
      );
    }

    if (assets.isEmpty) {
      return EmptyState(
        icon: Icons.grid_off_outlined,
        title: 'No NFTs Found',
        subtitle: 'No collectibles matched your selected collection filter or search query.',
        actionLabel: 'Refresh Gallery',
        onAction: onRefresh,
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        // Responsive grid columns: 2 columns on phones, 3+ on larger tablets
        final crossAxisCount = constraints.maxWidth > 600 ? 3 : 2;

        return RefreshIndicator(
          onRefresh: () async {
            if (onRefresh != null) onRefresh!();
          },
          child: GridView.builder(
            padding: const EdgeInsets.all(16),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: crossAxisCount,
              childAspectRatio: 0.72,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
            ),
            itemCount: assets.length,
            itemBuilder: (context, index) {
              final asset = assets[index];

              return NftCard(
                asset: asset,
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => NftDetailPage(
                        collectionId: asset.collectionId,
                        assetId: asset.assetId,
                      ),
                    ),
                  );
                },
              )
                  .animate()
                  .fadeIn(
                    duration: 350.ms,
                    delay: Duration(milliseconds: (index % 6) * 60),
                  )
                  .slideY(
                    begin: 0.15,
                    end: 0,
                    curve: Curves.easeOutCubic,
                    duration: 350.ms,
                    delay: Duration(milliseconds: (index % 6) * 60),
                  );
            },
          ),
        );
      },
    );
  }
}
