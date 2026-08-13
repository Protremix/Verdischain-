import 'dart:math' as math;
import 'package:flutter/material.dart';

/// Verdis branded animated logo — hexagonal V with leaf accent
class VerdisLogo extends StatefulWidget {

  const VerdisLogo({super.key, this.size = 48, this.color, this.animate = true});
  final double size;
  final Color? color;
  final bool animate;

  @override
  State<VerdisLogo> createState() => _VerdisLogoState();
}

class _VerdisLogoState extends State<VerdisLogo>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _hexProgress;
  late Animation<double> _vProgress;
  late Animation<double> _glowPulse;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    _hexProgress = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.4, curve: Curves.easeOut),
      ),
    );

    _vProgress = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.35, 0.75, curve: Curves.easeOut),
      ),
    );

    _glowPulse = Tween<double>(begin: 0.3, end: 0.7).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.75, 1.0, curve: Curves.easeInOut),
      ),
    );

    if (widget.animate) {
      _controller.forward();
      _controller.addStatusListener((status) {
        if (status == AnimationStatus.completed) {
          _controller.repeat(reverse: true, min: 0.75, max: 1.0);
        }
      });
    } else {
      _controller.value = 1.0;
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final logoColor = widget.color ?? const Color(0xFF00FF88);
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return SizedBox(
          width: widget.size,
          height: widget.size,
          child: CustomPaint(
            painter: _AnimatedVHexPainter(
              logoColor,
              _hexProgress.value,
              _vProgress.value,
              widget.animate ? _glowPulse.value : 0.5,
            ),
          ),
        );
      },
    );
  }
}

class _AnimatedVHexPainter extends CustomPainter {

  _AnimatedVHexPainter(this.color, this.hexProgress, this.vProgress, this.glowOpacity);
  final Color color;
  final double hexProgress;
  final double vProgress;
  final double glowOpacity;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width * 0.42;

    // === HEXAGON OUTLINE (animated draw) ===
    final hexPath = Path();
    final points = <Offset>[];
    for (int i = 0; i < 6; i++) {
      final angle = (i * 60 - 30) * math.pi / 180;
      points.add(Offset(
        center.dx + radius * math.cos(angle),
        center.dy + radius * math.sin(angle),
      ),);
    }
    for (int i = 0; i <= 6; i++) {
      final p = points[i % 6];
      if (i == 0) {
        hexPath.moveTo(p.dx, p.dy);
      } else {
        hexPath.lineTo(p.dx, p.dy);
      }
    }
    hexPath.close();

    // Glow background
    if (hexProgress > 0.3) {
      final glowAlpha = (hexProgress - 0.3) / 0.7 * 0.08 * glowOpacity;
      final bgPaint = Paint()
        ..color = color.withOpacity(glowAlpha)
        ..style = PaintingStyle.fill;
      canvas.drawPath(hexPath, bgPaint);
    }

    // Draw hexagon stroke progressively
    final hexMetrics = hexPath.computeMetrics();
    final hexPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    for (final metric in hexMetrics) {
      final extract = metric.extractPath(0, metric.length * hexProgress);
      canvas.drawPath(extract, hexPaint);
    }

    // === V SHAPE (animated draw) ===
    final vPath = Path();
    vPath.moveTo(center.dx - radius * 0.45, center.dy - radius * 0.35);
    vPath.lineTo(center.dx, center.dy + radius * 0.4);
    vPath.moveTo(center.dx + radius * 0.45, center.dy - radius * 0.35);
    vPath.lineTo(center.dx, center.dy + radius * 0.4);

    final vPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.0
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    for (final metric in vPath.computeMetrics()) {
      final extract = metric.extractPath(0, metric.length * vProgress);
      canvas.drawPath(extract, vPaint);
    }

    // === LEAF ACCENT ===
    if (vProgress > 0.8) {
      final leafOpacity = (vProgress - 0.8) / 0.2;
      final leafPaint = Paint()
        ..color = color.withOpacity(0.3 * leafOpacity)
        ..style = PaintingStyle.fill;

      final leafPath = Path();
      final lr = radius * 0.15;
      leafPath.moveTo(center.dx, center.dy - radius * 0.15);
      leafPath.quadraticBezierTo(
        center.dx + lr, center.dy,
        center.dx, center.dy + radius * 0.15,
      );
      leafPath.quadraticBezierTo(
        center.dx - lr, center.dy,
        center.dx, center.dy - radius * 0.15,
      );
      leafPath.close();
      canvas.drawPath(leafPath, leafPaint);
    }

    // === PULSE GLOW ===
    if (glowOpacity > 0.4) {
      final glowPaint = Paint()
        ..color = color.withOpacity((glowOpacity - 0.4) * 0.15)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 8);
      canvas.drawPath(hexPath, glowPaint);
    }
  }

  @override
  bool shouldRepaint(covariant _AnimatedVHexPainter oldDelegate) =>
      oldDelegate.hexProgress != hexProgress ||
      oldDelegate.vProgress != vProgress ||
      oldDelegate.glowOpacity != glowOpacity;
}

/// Static non-animated version for inline use
class VerdisLogoStatic extends StatelessWidget {

  const VerdisLogoStatic({super.key, this.size = 48, this.color});
  final double size;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final logoColor = color ?? const Color(0xFF00FF88);
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _StaticVHexPainter(logoColor),
      ),
    );
  }
}

class _StaticVHexPainter extends CustomPainter {
  _StaticVHexPainter(this.color);
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width * 0.42;

    // Hexagon
    final hexPath = Path();
    for (int i = 0; i < 6; i++) {
      final angle = (i * 60 - 30) * math.pi / 180;
      final p = Offset(center.dx + radius * math.cos(angle), center.dy + radius * math.sin(angle));
      if (i == 0) {
        hexPath.moveTo(p.dx, p.dy);
      } else {
        hexPath.lineTo(p.dx, p.dy);
      }
    }
    hexPath.close();

    canvas.drawPath(hexPath, Paint()
      ..color = color.withOpacity(0.08)
      ..style = PaintingStyle.fill,);
    canvas.drawPath(hexPath, Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeJoin = StrokeJoin.round,);

    // V shape
    final vPath = Path()
      ..moveTo(center.dx - radius * 0.45, center.dy - radius * 0.35)
      ..lineTo(center.dx, center.dy + radius * 0.4)
      ..moveTo(center.dx + radius * 0.45, center.dy - radius * 0.35)
      ..lineTo(center.dx, center.dy + radius * 0.4);

    canvas.drawPath(vPath, Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.0
      ..strokeCap = StrokeCap.round,);

    // Leaf accent
    final leafPath = Path();
    final lr = radius * 0.15;
    leafPath.moveTo(center.dx, center.dy - radius * 0.15);
    leafPath.quadraticBezierTo(center.dx + lr, center.dy, center.dx, center.dy + radius * 0.15);
    leafPath.quadraticBezierTo(center.dx - lr, center.dy, center.dx, center.dy - radius * 0.15);
    leafPath.close();
    canvas.drawPath(leafPath, Paint()
      ..color = color.withOpacity(0.3)
      ..style = PaintingStyle.fill,);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
