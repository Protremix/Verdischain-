#!/usr/bin/env python3
"""Patch onboarding_screen.dart to add email recovery option"""

filepath = "/opt/verdis-wallet/mobile/lib/screens/onboarding_screen.dart"

with open(filepath, "r") as f:
    content = f.read()

# 1. Add import for email recovery service
old_import = "import 'dashboard_screen.dart';"
new_import = """import 'dashboard_screen.dart';
import '../services/email_recovery_service.dart';"""

content = content.replace(old_import, new_import, 1)

# 2. Add "Recover with Email" card after the Import card
old_import_card = """                    const SizedBox(height: 32),
                    Text(
                      'Powered by sr25519 \\u2022 SS58 909 \\u2022 BIP39',"""

new_section = """                    const SizedBox(height: 16),
                    _buildActionCard(
                      icon: Icons.email_outlined,
                      title: 'Recover with Email',
                      subtitle: 'Restore wallet using email + password',
                      onTap: () => _showEmailRecovery(context),
                    ),
                    const SizedBox(height: 32),
                    Text(
                      'Powered by sr25519 \\u2022 SS58 909 \\u2022 BIP39',"""

# Try both possible representations of the unicode
import re

# Find the "Powered by" text
pattern = r'                    const SizedBox\(height: 32\),\n                    Text\(\s*\n\s*\'Powered by sr25519.*?BIP39\','
match = re.search(pattern, content, re.DOTALL)
if match:
    content = content[:match.start()] + new_section + content[match.end():]
    print("Added email recovery card")
else:
    # Try simpler pattern
    old_bottom = "                    const SizedBox(height: 32),\n                    Text(\n                      'Powered by sr25519"
    if old_bottom in content:
        content = content.replace(old_bottom, new_section.replace("                    Text(\n                      'Powered by sr2559", "                    Text(\n                      'Powered by sr2559"), 1)
        print("Added email recovery card (simple match)")
    else:
        print("WARNING: Could not find insertion point for email recovery card")

# 3. Add _showEmailRecovery method before the closing brace of the class
# Find the last method (_showImportWallet) and add after it
old_end = """  void _showImportWallet(BuildContext context) {"""

# Find the position just before the final closing brace
# The class ends with a single "}" on the last line
# We need to add our method before that

# Find _showImportWallet method and add after it
recovery_method = """
  void _showEmailRecovery(BuildContext context) {
    final emailController = TextEditingController();
    final passwordController = TextEditingController();
    bool isLoading = false;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => StatefulBuilder(
        builder: (ctx, setState) => AlertDialog(
          backgroundColor: const Color(0xFF0D1410),
          title: Text('Recover with Email', style: TextStyle(color: Colors.white)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Enter your email and password used during backup',
                style: TextStyle(color: const Color(0xFF94a3b8), fontSize: 13),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: emailController,
                keyboardType: TextInputType.emailAddress,
                style: TextStyle(fontSize: 14, color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'you@example.com',
                  hintStyle: TextStyle(color: const Color(0xFF475569), fontSize: 13),
                  filled: true,
                  fillColor: const Color(0xFF152017),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: const Color(0xFF16a34a).withOpacity(0.3)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF16a34a)),
                  ),
                  prefixIcon: Icon(Icons.email_outlined, color: Color(0xFF16a34a), size: 20),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: passwordController,
                obscureText: true,
                style: TextStyle(fontSize: 14, color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'Password',
                  hintStyle: TextStyle(color: const Color(0xFF475569), fontSize: 13),
                  filled: true,
                  fillColor: const Color(0xFF152017),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: const Color(0xFF16a34a).withOpacity(0.3)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF16a34a)),
                  ),
                  prefixIcon: Icon(Icons.lock_outline, color: Color(0xFF16a34a), size: 20),
                ),
              ),
              if (isLoading) ...[
                const SizedBox(height: 16),
                const CircularProgressIndicator(color: Color(0xFF16a34a)),
              ],
            ],
          ),
          actions: [
            TextButton(
              onPressed: isLoading ? null : () => Navigator.pop(dialogContext),
              child: const Text('Cancel', style: TextStyle(color: Color(0xFF94a3b8))),
            ),
            TextButton(
              onPressed: isLoading
                  ? null
                  : () async {
                      final email = emailController.text.trim();
                      final password = passwordController.text;

                      if (email.isEmpty || !email.contains('@')) {
                        ScaffoldMessenger.of(ctx).showSnackBar(
                          const SnackBar(
                            content: Text('Enter a valid email'),
                            backgroundColor: Color(0xFFEF4444),
                          ),
                        );
                        return;
                      }
                      if (password.length < 6) {
                        ScaffoldMessenger.of(ctx).showSnackBar(
                          const SnackBar(
                            content: Text('Password must be at least 6 characters'),
                            backgroundColor: Color(0xFFEF4444),
                          ),
                        );
                        return;
                      }

                      setState(() => isLoading = true);

                      try {
                        final mnemonic = await EmailRecoveryService.recoverWallet(
                          email: email,
                          password: password,
                        );

                        if (!ctx.mounted) return;
                        Navigator.pop(dialogContext);

                        final walletService = Provider.of<WalletService>(context, listen: false);
                        final account = await walletService.importWallet('Recovered', mnemonic);

                        if (account != null && context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Wallet recovered successfully!'),
                              backgroundColor: Color(0xFF16a34a),
                            ),
                          );
                          Navigator.pushReplacement(
                            context,
                            MaterialPageRoute(builder: (_) => const DashboardScreen()),
                          );
                        }
                      } catch (e) {
                        setState(() => isLoading = false);
                        if (ctx.mounted) {
                          ScaffoldMessenger.of(ctx).showSnackBar(
                            SnackBar(
                              content: Text(e.toString().replaceAll('Exception: ', '')),
                              backgroundColor: const Color(0xFFEF4444),
                            ),
                          );
                        }
                      }
                    },
              child: const Text('Recover', style: TextStyle(color: Color(0xFF16a34a))),
            ),
          ],
        ),
      ),
    );
  }
"""

# Find the end of _showImportWallet method and add after it
# The class ends with a single "}" at the end of the file
# Find "  }" followed by "\n}" at the end
last_brace_pos = content.rstrip().rfind("}")
if last_brace_pos > 0:
    # Insert the recovery method before the last closing brace
    content = content[:last_brace_pos] + recovery_method + "\n" + content[last_brace_pos:]
    print("Added _showEmailRecovery method")
else:
    print("ERROR: Could not find class closing brace")

with open(filepath, "w") as f:
    f.write(content)

print("Done patching onboarding_screen.dart")
