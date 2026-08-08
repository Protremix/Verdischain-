import 'package:flutter/material.dart';
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
