#!/usr/bin/env python3
"""Fix BalanceCard and VerdisButton to support full API with new design."""

BASE = '/opt/verdis-wallet/mobile'

# Fix BalanceCard - support accountName, vrdxBalance, usdBalance
balance_card = '''import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class BalanceCard extends StatelessWidget {
  final String accountName;
  final String address;
  final double vrdxBalance;
  final double? usdBalance;
  final VoidCallback? onRefresh;

  const BalanceCard({
    super.key,
    required this.accountName,
    required this.address,
    required this.vrdxBalance,
    this.usdBalance,
    this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF0D1410), Color(0xFF152017), Color(0xFF0D1410)],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.15)),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF16a34a).withOpacity(0.08),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      accountName.toUpperCase(),
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                        color: const Color(0xFF94a3b8),
                        letterSpacing: 1.5,
                      ),
                    ),
                    const SizedBox(height: 8),
                    ShaderMask(
                      shaderCallback: (bounds) => const LinearGradient(
                        colors: [Color(0xFF16a34a), Color(0xFF84fe87), Color(0xFF00a86b)],
                      ).createShader(bounds),
                      child: Text(
                        vrdxBalance.toStringAsFixed(4),
                        style: GoogleFonts.spaceGrotesk(
                          fontSize: 36,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'VRDX',
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: const Color(0xFF16a34a),
                      ),
                    ),
                  ],
                ),
              ),
              if (onRefresh != null)
                GestureDetector(
                  onTap: onRefresh,
                  child: Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: const Color(0xFF16a34a).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(Icons.refresh, color: Color(0xFF16a34a), size: 20),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFF040806),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.1)),
            ),
            child: Row(
              children: [
                const Icon(Icons.account_circle, color: Color(0xFF16a34a), size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    address,
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 11,
                      color: const Color(0xFF94a3b8),
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
'''
open(f'{BASE}/lib/widgets/balance_card.dart', 'w').write(balance_card)
print("Fixed balance_card.dart with full API")

# Fix VerdisButton - support variant enum
verdis_btn = '''import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

enum VerdisButtonVariant { primary, secondary, danger }

class VerdisButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;
  final VerdisButtonVariant variant;
  final IconData? icon;
  final bool isLoading;

  const VerdisButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.variant = VerdisButtonVariant.primary,
    this.icon,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    final isPrimary = variant == VerdisButtonVariant.primary;
    final isDanger = variant == VerdisButtonVariant.danger;
    final isSecondary = variant == VerdisButtonVariant.secondary;

    if (isPrimary) {
      return Container(
        width: double.infinity,
        height: 52,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            begin: Alignment.centerLeft,
            end: Alignment.centerRight,
            colors: [Color(0xFF16a34a), Color(0xFF15803d)],
          ),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: const Color(0xFF16a34a).withOpacity(0.3),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: isLoading ? null : onPressed,
            borderRadius: BorderRadius.circular(12),
            child: Center(
              child: isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        if (icon != null) ...[
                          Icon(icon, color: Colors.white, size: 20),
                          const SizedBox(width: 8),
                        ],
                        Text(
                          label,
                          style: GoogleFonts.inter(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
            ),
          ),
        ),
      );
    }

    // Secondary or Danger
    final borderColor = isDanger
        ? const Color(0xFFEF4444).withOpacity(0.3)
        : const Color(0xFF16a34a).withOpacity(0.3);
    final textColor = isDanger ? const Color(0xFFEF4444) : const Color(0xFF16a34a);

    return Container(
      width: double.infinity,
      height: 52,
      decoration: BoxDecoration(
        color: const Color(0xFF0D1410),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: borderColor),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: isLoading ? null : onPressed,
          borderRadius: BorderRadius.circular(12),
          child: Center(
            child: isLoading
                ? SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: textColor,
                    ),
                  )
                : Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      if (icon != null) ...[
                        Icon(icon, color: textColor, size: 20),
                        const SizedBox(width: 8),
                      ],
                      Text(
                        label,
                        style: GoogleFonts.inter(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: textColor,
                        ),
                      ),
                    ],
                  ),
          ),
        ),
      ),
    );
  }
}
'''
open(f'{BASE}/lib/widgets/verdis_button.dart', 'w').write(verdis_btn)
print("Fixed verdis_button.dart with variant enum")
