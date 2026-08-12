#!/usr/bin/env python3
"""Patch settings_screen.dart to add email backup option"""

filepath = "/opt/verdis-wallet/mobile/lib/screens/settings_screen.dart"

with open(filepath, "r") as f:
    content = f.read()

# 1. Add import for email recovery service
old_import = "import '../widgets/verdis_button.dart';"
new_import = """import '../widgets/verdis_button.dart';
import '../services/email_recovery_service.dart';"""

content = content.replace(old_import, new_import, 1)

# 2. Add "Backup to Email" ListTile after the Export ListTile
old_export_tile = """                    ListTile(
                      title: const Text('Export Private Key / Seed', style: TextStyle(color: Color(0xFFEF4444), fontSize: 13, fontWeight: FontWeight.w600)),
                      onTap: _showExportWalletModal,
                    ),"""

new_tiles = """                    ListTile(
                      title: const Text('Export Private Key / Seed', style: TextStyle(color: Color(0xFFEF4444), fontSize: 13, fontWeight: FontWeight.w600)),
                      onTap: _showExportWalletModal,
                    ),
                    ListTile(
                      title: const Text('Backup to Email', style: TextStyle(color: Color(0xFF16a34a), fontSize: 13, fontWeight: FontWeight.w600)),
                      subtitle: const Text('Encrypt & store wallet recovery on server', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 11)),
                      onTap: _showEmailBackupModal,
                    ),"""

if old_export_tile in content:
    content = content.replace(old_export_tile, new_tiles, 1)
    print("Added backup ListTile")
else:
    print("ERROR: Could not find export tile")

# 3. Add _showEmailBackupModal method before dispose()
backup_method = """
  void _showEmailBackupModal() {
    final emailController = TextEditingController();
    final passwordController = TextEditingController();
    final confirmController = TextEditingController();
    bool isLoading = false;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF0D1410),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setState) {
            return Padding(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).viewInsets.bottom + 20,
                top: 20,
                left: 20,
                right: 20,
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.email_outlined, color: Color(0xFF16a34a), size: 24),
                      SizedBox(width: 8),
                      Text(
                        'Backup Wallet to Email',
                        style: TextStyle(color: Color(0xFF16a34a), fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Your mnemonic will be encrypted locally with your password and stored on the server. The server never sees your mnemonic or password. You can recover your wallet using your email + password.',
                    style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12, height: 1.4),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: emailController,
                    keyboardType: TextInputType.emailAddress,
                    style: const TextStyle(color: Color(0xFFFFFFFF)),
                    decoration: const InputDecoration(
                      labelText: 'Email Address',
                      labelStyle: TextStyle(color: Color(0xFF94a3b8)),
                      filled: true,
                      fillColor: Color(0xFF040806),
                      enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF2E2E34))),
                      focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF16a34a))),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: passwordController,
                    obscureText: true,
                    style: const TextStyle(color: Color(0xFFFFFFFF)),
                    decoration: const InputDecoration(
                      labelText: 'Password (min 6 chars)',
                      labelStyle: TextStyle(color: Color(0xFF94a3b8)),
                      filled: true,
                      fillColor: Color(0xFF040806),
                      enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF2E2E34))),
                      focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF16a34a))),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: confirmController,
                    obscureText: true,
                    style: const TextStyle(color: Color(0xFFFFFFFF)),
                    decoration: const InputDecoration(
                      labelText: 'Confirm Password',
                      labelStyle: TextStyle(color: Color(0xFF94a3b8)),
                      filled: true,
                      fillColor: Color(0xFF040806),
                      enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF2E2E34))),
                      focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF16a34a))),
                    ),
                  ),
                  const SizedBox(height: 20),
                  if (isLoading)
                    const Center(child: CircularProgressIndicator(color: Color(0xFF16a34a)))
                  else
                    VerdisButton(
                      label: 'Encrypt & Backup',
                      onPressed: () async {
                        final email = emailController.text.trim();
                        final password = passwordController.text;
                        final confirm = confirmController.text;

                        if (email.isEmpty || !email.contains('@')) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Enter a valid email')),
                          );
                          return;
                        }
                        if (password.length < 6) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Password must be at least 6 characters')),
                          );
                          return;
                        }
                        if (password != confirm) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Passwords do not match')),
                          );
                          return;
                        }

                        setState(() => isLoading = true);

                        try {
                          final wallet = Provider.of<WalletService>(context, listen: false);
                          if (wallet.activeAccount == null) {
                            throw Exception('No active wallet');
                          }

                          // Decrypt mnemonic using wallet PIN
                          // We need the user's PIN to decrypt the stored mnemonic
                          // For now, use the export function which requires PIN
                          final pinController = TextEditingController();
                          final pinResult = await showDialog<String>(
                            context: context,
                            builder: (pinCtx) => AlertDialog(
                              backgroundColor: const Color(0xFF0D1410),
                              title: const Text('Enter PIN', style: TextStyle(color: Colors.white)),
                              content: TextField(
                                controller: pinController,
                                obscureText: true,
                                keyboardType: TextInputType.number,
                                maxLength: 6,
                                style: const TextStyle(color: Colors.white),
                                decoration: const InputDecoration(
                                  labelText: 'Wallet PIN',
                                  labelStyle: TextStyle(color: Color(0xFF94a3b8)),
                                  filled: true,
                                  fillColor: Color(0xFF040806),
                                ),
                              ),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.pop(pinCtx, null),
                                  child: const Text('Cancel', style: TextStyle(color: Color(0xFF94a3b8))),
                                ),
                                TextButton(
                                  onPressed: () => Navigator.pop(pinCtx, pinController.text.trim()),
                                  child: const Text('Confirm', style: TextStyle(color: Color(0xFF16a34a))),
                                ),
                              ],
                            ),
                          );

                          if (pinResult == null) {
                            setState(() => isLoading = false);
                            return;
                          }

                          final mnemonic = await wallet.exportPrivateKey(
                            wallet.activeAccount!,
                            pinResult,
                          );

                          if (mnemonic == null || mnemonic.isEmpty) {
                            throw Exception('Failed to decrypt mnemonic');
                          }

                          await EmailRecoveryService.backupWallet(
                            email: email,
                            password: password,
                            mnemonic: mnemonic,
                            address: wallet.activeAccount!.address,
                          );

                          if (ctx.mounted) Navigator.pop(ctx);
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Wallet backed up to email successfully!'),
                                backgroundColor: Color(0xFF16a34a),
                              ),
                            );
                          }
                        } catch (e) {
                          setState(() => isLoading = false);
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(e.toString().replaceAll('Exception: ', '')),
                                backgroundColor: const Color(0xFFEF4444),
                              ),
                            );
                          }
                        }
                      },
                    ),
                ],
              ),
            );
          },
        );
      },
    );
  }

"""

# Insert before dispose method
old_dispose = "  @override\n  void dispose() {"
if old_dispose in content:
    content = content.replace(old_dispose, backup_method + old_dispose, 1)
    print("Added _showEmailBackupModal method")
else:
    print("ERROR: Could not find dispose method")

with open(filepath, "w") as f:
    f.write(content)

print("Done patching settings_screen.dart")
