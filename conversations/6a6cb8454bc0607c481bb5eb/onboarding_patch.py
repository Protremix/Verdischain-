path = "/opt/verdis-wallet/mobile/lib/screens/onboarding_screen.dart"
with open(path) as f:
    content = f.read()

# 1. Add Clipboard import if missing
if "import 'package:flutter/services.dart';" not in content:
    content = content.replace(
        "import 'package:flutter/material.dart';",
        "import 'package:flutter/material.dart';\nimport 'package:flutter/services.dart';",
        1,
    )

old_block = """            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF152017), Color(0xFF0D1410)],
                ),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.3)),
              ),
              child: Text(
                mnemonic,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.white,
                  height: 1.8,
                  letterSpacing: 0.5,
                ),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Write down these 12 words and keep them safe. Never share them with anyone.',
              style: TextStyle(color: Color(0xFFEF4444), fontSize: 12),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(dialogContext);
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const DashboardScreen()),
              );
            },
            child: const Text('I Saved It', style: TextStyle(color: Color(0xFF16a34a))),
          ),
        ],
      ),
    );
  }"""

new_block = """            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF152017), Color(0xFF0D1410)],
                ),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.3)),
              ),
              child: SelectableText(
                mnemonic,
                style: const TextStyle(
                  fontSize: 14,
                  color: Colors.white,
                  height: 1.8,
                  letterSpacing: 0.5,
                ),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: mnemonic));
                  ScaffoldMessenger.of(dialogContext).showSnackBar(
                    const SnackBar(
                      content: Text('Mnemonic copied to clipboard'),
                      duration: Duration(seconds: 2),
                      backgroundColor: Color(0xFF0D1410),
                    ),
                  );
                },
                icon: const Icon(Icons.copy, size: 16, color: Color(0xFF16a34a)),
                label: const Text('Copy to clipboard', style: TextStyle(color: Color(0xFF16a34a))),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: Color(0xFF16a34a)),
                ),
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Write down these 12 words and keep them safe. Never share them with anyone.',
              style: TextStyle(color: Color(0xFFEF4444), fontSize: 12),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(dialogContext);
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const DashboardScreen()),
              );
            },
            child: const Text('I Saved It', style: TextStyle(color: Color(0xFF16a34a))),
          ),
        ],
      ),
    );
  }"""

assert old_block in content, "OLD BLOCK NOT FOUND"
content = content.replace(old_block, new_block)
print("onboarding_screen.dart patched OK")

with open(path, "w") as f:
    f.write(content)
