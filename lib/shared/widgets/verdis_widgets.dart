import 'package:shimmer/shimmer.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// Verdis branded gradient button
class VerdisButton extends StatelessWidget {

  const VerdisButton({
    super.key,
    required this.label,
    this.onPressed,
    this.isLoading = false,
    this.isOutlined = false,
    this.icon,
    this.width,
  });
  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;
  final bool isOutlined;
  final IconData? icon;
  final double? width;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final button = isOutlined
        ? OutlinedButton.icon(
            onPressed: isLoading ? null : onPressed,
            icon: isLoading
                ? SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: theme.colorScheme.primary,
                    ),
                  )
                : Icon(icon ?? Icons.arrow_forward),
            label: Text(label),
          )
        : ElevatedButton.icon(
            onPressed: isLoading ? null : onPressed,
            icon: isLoading
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.black,
                    ),
                  )
                : Icon(icon ?? Icons.arrow_forward),
            label: Text(label),
          );

    return SizedBox(
      width: width ?? double.infinity,
      child: button.animate(target: onPressed != null ? 1 : 0)
          .shimmer(duration: 1200.ms, color: theme.colorScheme.primary.withOpacity(0.1)),
    );
  }
}

/// Verdis branded card with glassmorphism effect
class VerdisCard extends StatelessWidget {

  const VerdisCard({
    super.key,
    required this.child,
    this.padding,
    this.onTap,
    this.width,
  });
  final Widget child;
  final EdgeInsets? padding;
  final VoidCallback? onTap;
  final double? width;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          width: width,
          padding: padding ?? const EdgeInsets.all(16),
          child: child,
        ),
      ),
    );
  }
}

/// Stat tile for dashboard
class StatTile extends StatelessWidget {

  const StatTile({
    super.key,
    required this.label,
    required this.value,
    required this.icon,
    this.iconColor,
    this.onTap,
  });
  final String label;
  final String value;
  final IconData icon;
  final Color? iconColor;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return VerdisCard(
      padding: const EdgeInsets.all(16),
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Icon(icon, color: iconColor ?? theme.colorScheme.primary, size: 22),
              if (onTap != null)
                Icon(Icons.chevron_right, color: theme.colorScheme.onSurfaceVariant, size: 18),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: theme.textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}

/// Loading shimmer placeholder
class ShimmerPlaceholder extends StatelessWidget {

  const ShimmerPlaceholder({
    super.key,
    required this.height,
    this.width,
    this.borderRadius = 12,
  });
  final double height;
  final double? width;
  final double borderRadius;

  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: Theme.of(context).colorScheme.surface,
      highlightColor: Theme.of(context).colorScheme.surfaceContainerHighest,
      child: Container(
        height: height,
        width: width ?? double.infinity,
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          borderRadius: BorderRadius.circular(borderRadius),
        ),
      ),
    );
  }
}

/// Address chip with copy functionality
class AddressChip extends StatelessWidget {

  const AddressChip({
    super.key,
    required this.address,
    this.showCopy = true,
  });
  final String address;
  final bool showCopy;

  String get shortened {
    if (address.length <= 12) return address;
    return '${address.substring(0, 6)}...${address.substring(address.length - 6)}';
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.account_circle, size: 16, color: Theme.of(context).colorScheme.primary),
              const SizedBox(width: 6),
              Text(shortened, style: Theme.of(context).textTheme.labelMedium),
            ],
          ),
        ),
        if (showCopy) ...[
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.copy, size: 16),
            onPressed: () {
              // Clipboard copy
            },
            iconSize: 16,
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
          ),
        ],
      ],
    );
  }
}

/// Network status badge
class NetworkStatusBadge extends StatelessWidget {

  const NetworkStatusBadge({
    super.key,
    required this.isConnected,
    this.blockNumber,
  });
  final bool isConnected;
  final int? blockNumber;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: isConnected
            ? theme.colorScheme.primary.withOpacity(0.1)
            : theme.colorScheme.error.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isConnected ? theme.colorScheme.primary : theme.colorScheme.error,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            isConnected
                ? blockNumber != null ? 'Block #$blockNumber' : 'Connected'
                : 'Disconnected',
            style: theme.textTheme.labelSmall?.copyWith(
              color: isConnected ? theme.colorScheme.primary : theme.colorScheme.error,
            ),
          ),
        ],
      ),
    );
  }
}

/// Empty state widget
class EmptyState extends StatelessWidget {

  const EmptyState({
    super.key,
    required this.icon,
    required this.title,
    this.subtitle,
    this.actionLabel,
    this.onAction,
  });
  final IconData icon;
  final String title;
  final String? subtitle;
  final String? actionLabel;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 64, color: theme.colorScheme.onSurfaceVariant),
            const SizedBox(height: 16),
            Text(title, style: theme.textTheme.titleMedium),
            if (subtitle != null) ...[
              const SizedBox(height: 8),
              Text(subtitle!, style: theme.textTheme.bodySmall, textAlign: TextAlign.center),
            ],
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: 24),
              VerdisButton(label: actionLabel!, onPressed: onAction, isOutlined: true),
            ],
          ],
        ),
      ),
    );
  }
}

/// Animated balance display
class BalanceDisplay extends StatelessWidget {

  const BalanceDisplay({
    super.key,
    required this.amount,
    required this.symbol,
    this.decimals = 9, // Verdis uses 9 decimals
    this.fontSize,
  });
  final int amount;
  final String symbol;
  final int decimals;
  final double? fontSize;

  String get formatted {
    final value = amount / (1 * decimals);
    return value.toStringAsFixed(4);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.baseline,
      textBaseline: TextBaseline.alphabetic,
      children: [
        Text(
          formatted,
          style: theme.textTheme.displaySmall?.copyWith(
            fontSize: fontSize,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(width: 8),
        Text(symbol, style: theme.textTheme.titleMedium?.copyWith(
          color: theme.colorScheme.primary,
        ),),
      ],
    );
  }
}
