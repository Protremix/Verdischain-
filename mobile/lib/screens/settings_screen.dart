import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/wallet_service.dart';
import '../services/auth_service.dart';
import '../widgets/verdis_button.dart';
import '../services/email_recovery_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final TextEditingController _rpcController = TextEditingController();
  final TextEditingController _pinConfirmController = TextEditingController();
  final TextEditingController _newPinController = TextEditingController();

  @override
  void initState() {
    super.initState();
    final wallet = Provider.of<WalletService>(context, listen: false);
    _rpcController.text = wallet.rpcUrl;
  }

  void _updateRpcUrl() async {
    final wallet = Provider.of<WalletService>(context, listen: false);
    await wallet.updateRpcUrl(_rpcController.text.trim());
    if (mounted) {
      // ignore: use_build_context_synchronously
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('RPC URL updated'),
          backgroundColor: Color(0xFF0D1410),
        ),
      );
    }
  }

  void _showChangePinModal() {
    _pinConfirmController.clear();
    _newPinController.clear();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF0D1410),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        return Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
            top: 20,
            left: 20,
            right: 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Change 6-Digit PIN',
                style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _pinConfirmController,
                obscureText: true,
                keyboardType: TextInputType.number,
                maxLength: 6,
                style: const TextStyle(color: Color(0xFFFFFFFF)),
                decoration: const InputDecoration(
                  labelText: 'Current PIN',
                  labelStyle: TextStyle(color: Color(0xFF94a3b8)),
                  filled: true,
                  fillColor: Color(0xFF040806),
                  enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF2E2E34))),
                  focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF16a34a))),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _newPinController,
                obscureText: true,
                keyboardType: TextInputType.number,
                maxLength: 6,
                style: const TextStyle(color: Color(0xFFFFFFFF)),
                decoration: const InputDecoration(
                  labelText: 'New 6-Digit PIN',
                  labelStyle: TextStyle(color: Color(0xFF94a3b8)),
                  filled: true,
                  fillColor: Color(0xFF040806),
                  enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF2E2E34))),
                  focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF16a34a))),
                ),
              ),
              const SizedBox(height: 20),
              VerdisButton(
                label: 'Update PIN',
                onPressed: () async {
                  final auth = Provider.of<AuthService>(context, listen: false);
                  final valid = await auth.verifyPin(_pinConfirmController.text.trim());
                  if (valid) {
                    final newPin = _newPinController.text.trim();
                    if (newPin.length == 6) {
                      await auth.setPin(newPin);
                      final walletSvc = Provider.of<WalletService>(context, listen: false);
                      walletSvc.setWalletPin(newPin);
                      if (ctx.mounted) Navigator.pop(ctx);
                      if (!context.mounted) return;
                      // ignore: use_build_context_synchronously
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('PIN updated successfully')),
                      );
                    }
                  } else {
                    if (!context.mounted) return;
                    // ignore: use_build_context_synchronously
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Incorrect current PIN')),
                    );
                  }
                },
              ),
            ],
          ),
        );
      },
    );
  }

  void _showExportWalletModal() {
    _pinConfirmController.clear();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF0D1410),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        String? decryptedKey;
        bool isUnlocked = false;

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
                      Icon(Icons.warning_amber_rounded, color: Color(0xFFEF4444), size: 24),
                      SizedBox(width: 8),
                      Text(
                        'Export Wallet Key',
                        style: TextStyle(color: Color(0xFFEF4444), fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'NEVER share your private key or seed phrase with anyone. Anyone with access to this key can permanently steal your assets.',
                    style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12, height: 1.4),
                  ),
                  const SizedBox(height: 16),
                  if (!isUnlocked) ...[
                    TextField(
                      controller: _pinConfirmController,
                      obscureText: true,
                      keyboardType: TextInputType.number,
                      maxLength: 6,
                      style: const TextStyle(color: Color(0xFFFFFFFF)),
                      decoration: const InputDecoration(
                        labelText: 'Enter PIN to confirm',
                        labelStyle: TextStyle(color: Color(0xFF94a3b8)),
                        filled: true,
                        fillColor: Color(0xFF040806),
                        enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF2E2E34))),
                        focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF16a34a))),
                      ),
                    ),
                    const SizedBox(height: 16),
                    VerdisButton(
                      label: 'Verify PIN & Reveal',
                      variant: VerdisButtonVariant.danger,
                      onPressed: () async {
                        final auth = Provider.of<AuthService>(context, listen: false);
                        final wallet = Provider.of<WalletService>(context, listen: false);
                        final isValid = await auth.verifyPin(_pinConfirmController.text.trim());

                        if (isValid && wallet.activeAccount != null) {
                          try {
                            final pinText = _pinConfirmController.text.trim();
                            final decrypted = await wallet.exportPrivateKey(wallet.activeAccount!, pinText);
                            setState(() {
                              decryptedKey = decrypted ?? "Unable to decrypt";
                              isUnlocked = true;
                            });
                          } catch (_) {
                            setState(() {
                              decryptedKey = "Decryption failed";
                              isUnlocked = true;
                            });
                          }
                        } else {
                          if (!context.mounted) return;
                          // ignore: use_build_context_synchronously
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Invalid PIN')),
                          );
                        }
                      },
                    ),
                  ] else ...[
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF040806),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFF16a34a)),
                      ),
                      child: SelectableText(
                        decryptedKey ?? 'Key unavailable',
                        style: const TextStyle(color: Color(0xFF16a34a), fontFamily: 'monospace', fontSize: 12),
                      ),
                    ),
                    const SizedBox(height: 16),
                    VerdisButton(
                      label: 'Close',
                      onPressed: () => Navigator.pop(ctx),
                    ),
                  ],
                ],
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthService>(context);

    return Scaffold(
      backgroundColor: const Color(0xFF040806),
      appBar: AppBar(
        backgroundColor: const Color(0xFF040806),
        elevation: 0,
        title: const Text(
          'Settings',
          style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // RPC settings
              const Text('Network & RPC', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF0D1410),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFF2E2E34)),
                ),
                child: Column(
                  children: [
                    TextField(
                      controller: _rpcController,
                      style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 13),
                      decoration: const InputDecoration(
                        labelText: 'Substrate RPC Endpoint',
                        labelStyle: TextStyle(color: Color(0xFF94a3b8), fontSize: 12),
                        filled: true,
                        fillColor: Color(0xFF040806),
                        enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF2E2E34))),
                        focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF16a34a))),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        TextButton(
                          onPressed: () {
                            _rpcController.text = 'https://verdischain.com/rpc';
                            _updateRpcUrl();
                          },
                          child: const Text('Reset Default', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12)),
                        ),
                        const SizedBox(width: 8),
                        ElevatedButton(
                          style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF16a34a), foregroundColor: const Color(0xFF040806)),
                          onPressed: _updateRpcUrl,
                          child: const Text('Save RPC', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Security section
              const Text('Security & Auth', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF0D1410),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFF2E2E34)),
                ),
                child: Column(
                  children: [
                    SwitchListTile(
                      activeColor: const Color(0xFF16a34a),
                      title: const Text('Biometric Authentication', style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 13)),
                      subtitle: const Text('Unlock with Face ID / Fingerprint', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 11)),
                      value: auth.biometricEnabled,
                      onChanged: (val) => auth.setBiometricEnabled(val),
                    ),
                    const Divider(color: Color(0xFF2E2E34), height: 1),
                    ListTile(
                      title: const Text('Change Security PIN', style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 13)),
                      trailing: const Icon(Icons.chevron_right, color: Color(0xFF94a3b8)),
                      onTap: _showChangePinModal,
                    ),
                    const Divider(color: Color(0xFF2E2E34), height: 1),
                    ListTile(
                      title: const Text('Export Private Key / Seed', style: TextStyle(color: Color(0xFFEF4444), fontSize: 13, fontWeight: FontWeight.w600)),
                      trailing: const Icon(Icons.key, color: Color(0xFFEF4444), size: 18),
                      onTap: _showExportWalletModal,
                    ),
                    const Divider(color: Color(0xFF2E2E34), height: 1),
                    ListTile(
                      title: const Text('Backup to Email', style: TextStyle(color: Color(0xFF16a34a), fontSize: 13, fontWeight: FontWeight.w600)),
                      subtitle: const Text('Encrypt & store wallet recovery on server', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 11)),
                      trailing: const Icon(Icons.email_outlined, color: Color(0xFF16a34a), size: 18),
                      onTap: _showEmailBackupModal,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // About section
              const Text('About Verdis', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF0D1410),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFF2E2E34)),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('App Version', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12)),
                        Text('v1.0.0 (Verdis Wallet)', style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 12)),
                      ],
                    ),
                    SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Shared Core', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12)),
                        Text('verdis-core (Rust/flutter_rust_bridge)', style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 12)),
                      ],
                    ),
                    SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Consensus', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12)),
                        Text('Substrate BABE / GRANDPA', style: TextStyle(color: Color(0xFF16a34a), fontSize: 12)),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }


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

  @override
  void dispose() {
    _rpcController.dispose();
    _pinConfirmController.dispose();
    _newPinController.dispose();
    super.dispose();
  }
}
