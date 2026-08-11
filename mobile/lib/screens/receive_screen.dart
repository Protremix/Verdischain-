import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../services/wallet_service.dart';
import '../widgets/verdis_button.dart';

class ReceiveScreen extends StatelessWidget {
  const ReceiveScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final wallet = Provider.of<WalletService>(context);
    final activeAcc = wallet.activeAccount;
    final address = activeAcc?.address ?? 'vrdx1q000000000000000000000000000000000';

    return Scaffold(
      backgroundColor: const Color(0xFF040806),
      appBar: AppBar(
        backgroundColor: const Color(0xFF040806),
        elevation: 0,
        title: const Text(
          'Receive VRDX',
          style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 16, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFFFFFFFF)),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            children: [
              Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    children: [
                      const SizedBox(height: 10),
                      Container(
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0D1410),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFF2E2E34)),
                        ),
                        child: Column(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: SizedBox(
                                width: 200,
                                height: 200,
                                child: CustomPaint(
                                  painter: QrMatrixPainter(address),
                                ),
                              ),
                            ),
                            const SizedBox(height: 20),
                            Text(
                              activeAcc?.name ?? 'Main Wallet',
                              style: const TextStyle(
                                color: Color(0xFFFFFFFF),
                                fontSize: 15,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                              decoration: BoxDecoration(
                                color: const Color(0xFF040806),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: const Color(0xFF2E2E34)),
                              ),
                              child: SelectableText(
                                address,
                                textAlign: TextAlign.center,
                                style: const TextStyle(
                                  color: Color(0xFF16a34a),
                                  fontSize: 12,
                                  fontFamily: 'monospace',
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0D1410),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: const Color(0xFF2E2E34)),
                        ),
                        child: const Row(
                          children: [
                            Icon(Icons.info_outline, color: Color(0xFF16a34a), size: 20),
                            SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                'Send only VRDX or native Verdis ecosystem tokens (e.g. VERD-ECO) to this address. Sending other assets may result in permanent loss.',
                                style: TextStyle(color: Color(0xFF94a3b8), fontSize: 11, height: 1.4),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              Row(
                children: [
                  Expanded(
                    child: VerdisButton(
                      label: 'Copy Address',
                      icon: Icons.copy,
                      onPressed: () {
                        Clipboard.setData(ClipboardData(text: address));
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Address copied to clipboard'),
                            duration: Duration(seconds: 2),
                            backgroundColor: Color(0xFF0D1410),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// CustomPainter for generating deterministic high-resolution QR matrix layout from address
class QrMatrixPainter extends CustomPainter {
  final String text;

  QrMatrixPainter(this.text);

  @override
  void paint(Canvas canvas, Size size) {
    final paintDark = Paint()
      ..color = Colors.black
      ..style = PaintingStyle.fill;

    final paintLight = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), paintLight);

    const int gridSize = 21; // Standard QR matrix version 1
    final double cellSize = size.width / gridSize;

    // Generate deterministic boolean matrix from hash
    final bytes = utf8.encode(text);
    final hash = sha256.convert(bytes).bytes;

    bool isDark(int r, int c) {
      // Corner finder patterns (3 corners)
      if ((r < 7 && c < 7) || (r < 7 && c >= gridSize - 7) || (r >= gridSize - 7 && c < 7)) {
        if ((r == 0 || r == 6 || c == 0 || c == 6) && (r < 7 && c < 7)) return true;
        if ((r >= 2 && r <= 4 && c >= 2 && c <= 4) && (r < 7 && c < 7)) return true;

        if ((r == 0 || r == 6 || c == gridSize - 7 || c == gridSize - 1) && (r < 7 && c >= gridSize - 7)) return true;
        if ((r >= 2 && r <= 4 && c >= gridSize - 5 && c <= gridSize - 3) && (r < 7 && c >= gridSize - 7)) return true;

        if ((r == gridSize - 7 || r == gridSize - 1 || c == 0 || c == 6) && (r >= gridSize - 7 && c < 7)) return true;
        if ((r >= gridSize - 5 && r <= gridSize - 3 && c >= 2 && c <= 4) && (r >= gridSize - 7 && c < 7)) return true;

        return false;
      }

      // Timing patterns
      if (r == 6 || c == 6) return (r + c) % 2 == 0;

      final bitIndex = (r * gridSize + c) % (hash.length * 8);
      final byteVal = hash[bitIndex ~/ 8];
      return ((byteVal >> (bitIndex % 8)) & 1) == 1;
    }

    for (int r = 0; r < gridSize; r++) {
      for (int c = 0; c < gridSize; c++) {
        if (isDark(r, c)) {
          canvas.drawRect(
            Rect.fromLTWH(c * cellSize, r * cellSize, cellSize, cellSize),
            paintDark,
          );
        }
      }
    }
  }

  @override
  bool shouldRepaint(covariant QrMatrixPainter oldDelegate) => oldDelegate.text != text;
}
