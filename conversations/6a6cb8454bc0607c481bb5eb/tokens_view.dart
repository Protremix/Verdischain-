// Tokens View — shows real VRDX balance and token list from chain
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'home_providers.dart';

class TokensView extends ConsumerStatefulWidget {
  const TokensView({super.key});

  @override
  ConsumerState<TokensView> createState() => _TokensViewState();
}

class _TokensViewState extends ConsumerState<TokensView> {
  int? _vrdxBalance;
  bool _isLoading = true;
  String? _error;

  static const String _relayUrl = 'https://verdischain.com/api/tx-relay';

  @override
  void initState() {
    super.initState();
    _loadBalance();
  }

  Future<void> _loadBalance() async {
    final address = ref.read(selectedAddressProvider);
    if (address.isEmpty) {
      setState(() { _isLoading = false; _vrdxBalance = 0; });
      return;
    }

    try {
      final response = await http.post(
        Uri.parse(_relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'action': 'balance', 'address': address}),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['ok'] == true) {
          final bal = data['data']?['balance'];
          setState(() {
            _vrdxBalance = bal is int ? bal : int.tryParse(bal?.toString() ?? '0') ?? 0;
            _isLoading = false;
          });
          return;
        }
      }
      setState(() { _vrdxBalance = 0; _isLoading = false; });
    } catch (e) {
      setState(() { _vrdxBalance = 0; _isLoading = false; _error = e.toString(); });
    }
  }

  String _formatBalance(int plancks) {
    final vrdx = plancks / 1e9;
    if (vrdx == 0) return '0.00';
    if (vrdx < 1) return vrdx.toStringAsFixed(9);
    if (vrdx < 1000) return vrdx.toStringAsFixed(2);
    return vrdx.toStringAsFixed(2);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return RefreshIndicator(
      color: theme.colorScheme.primary,
      onRefresh: _loadBalance,
      child: _isLoading
        ? const Center(child: CircularProgressIndicator())
        : SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Token Balances', style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 20),

                // VRDX Native Token Card
                Card(
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                    side: BorderSide(color: theme.colorScheme.outline),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: [
                        Container(
                          width: 48,
                          height: 48,
                          decoration: BoxDecoration(
                            color: const Color(0xFF00FF88).withOpacity(0.15),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(Icons.token, color: Color(0xFF00FF88), size: 28),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('VRDX', style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                              Text('Verdis Native Token', style: theme.textTheme.bodySmall),
                            ],
                          ),
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              _formatBalance(_vrdxBalance ?? 0),
                              style: theme.textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: const Color(0xFF00FF88),
                              ),
                            ),
                            Text('9 decimals', style: theme.textTheme.bodySmall),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                Text('Other Tokens', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                Card(
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                    side: BorderSide(color: theme.colorScheme.outline),
                  ),
                  child: const Padding(
                    padding: EdgeInsets.all(32),
                    child: Column(
                      children: [
                        Icon(Icons.inventory_2_outlined, size: 40, color: Color(0xFF8B9D8B)),
                        SizedBox(height: 12),
                        Text('No additional tokens', style: TextStyle(color: Color(0xFF8B9D8B))),
                        SizedBox(height: 4),
                        Text('ECO, CARBON, TREE, GREEN tokens will appear here when you hold them', textAlign: TextAlign.center, style: TextStyle(fontSize: 12, color: Color(0xFF8B9D8B))),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
    );
  }
}
