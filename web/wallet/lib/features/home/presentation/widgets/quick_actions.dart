import 'package:flutter/material.dart';

/// Action type callback handler enum
enum QuickActionType { send, receive, swap, stake }

/// Row of 4 quick action buttons: Send, Receive, Swap, Stake
class QuickActions extends StatelessWidget {

  const QuickActions({
    super.key,
    this.onActionTap,
  });
  final Function(QuickActionType type)? onActionTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildActionButton(
          context,
          icon: Icons.send,
          label: 'Send',
          color: theme.colorScheme.primary,
          onTap: () => onActionTap?.call(QuickActionType.send),
        ),
        _buildActionButton(
          context,
          icon: Icons.download,
          label: 'Receive',
          color: const Color(0xFF00FF88),
          onTap: () => onActionTap?.call(QuickActionType.receive),
        ),
        _buildActionButton(
          context,
          icon: Icons.swap_horiz,
          label: 'Swap',
          color: const Color(0xFF40C4FF),
          onTap: () => onActionTap?.call(QuickActionType.swap),
        ),
        _buildActionButton(
          context,
          icon: Icons.energy_savings_leaf,
          label: 'Stake',
          color: const Color(0xFFFFB300),
          onTap: () => onActionTap?.call(QuickActionType.stake),
        ),
      ],
    );
  }

  Widget _buildActionButton(
    BuildContext context, {
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          child: Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: color.withOpacity(0.12),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: color.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Center(
              child: Icon(
                icon,
                color: color,
                size: 26,
              ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: theme.textTheme.labelMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}
