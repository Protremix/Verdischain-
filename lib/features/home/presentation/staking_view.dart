// Staking View — shows real on-chain validators from TX Relay API
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class StakingView extends ConsumerStatefulWidget {
  const StakingView({super.key});

  @override
  ConsumerState<StakingView> createState() => _StakingViewState();
}

class _StakingViewState extends ConsumerState<StakingView> {
  List<dynamic> _validators = [];
  int _activeCount = 0;
  int _totalStaked = 0;
  bool _isLoading = true;
  String? _error;

  static const String _relayUrl = 'https://verdischain.com/api/tx-relay';

  @override
  void initState() {
    super.initState();
    _loadValidators();
  }

  Future<void> _loadValidators() async {
    try {
      final response = await http.get(
        Uri.parse('$_relayUrl/validators'),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['ok'] == true) {
          final vals = data['data']?['validators'] ?? [];
          int active = 0;
          int totalStake = 0;
          for (final v in vals) {
            if (v['isActive'] == true) active++;
            totalStake += (v['stake'] as num? ?? 0).toInt();
          }
          setState(() {
            _validators = vals;
            _activeCount = active;
            _totalStaked = totalStake;
            _isLoading = false;
          });
          return;
        }
      }
      setState(() { _isLoading = false; _error = 'Failed to load validators'; });
    } catch (e) {
      setState(() { _isLoading = false; _error = e.toString(); });
    }
  }

  String _formatStake(int plancks) {
    final vrdx = plancks / 1e9;
    if (vrdx >= 1e9) return '${(vrdx / 1e9).toStringAsFixed(2)}B';
    if (vrdx >= 1e6) return '${(vrdx / 1e6).toStringAsFixed(2)}M';
    if (vrdx >= 1e3) return '${(vrdx / 1e3).toStringAsFixed(2)}K';
    return vrdx.toStringAsFixed(2);
  }

  String _shortAddr(String addr) {
    if (addr.length <= 12) return addr;
    return '${addr.substring(0, 6)}...${addr.substring(addr.length - 6)}';
  }

  Color _scoreColor(int score) {
    switch (score) {
      case 4: return const Color(0xFF00FF88);
      case 3: return const Color(0xFF66CC66);
      case 2: return const Color(0xFFE6B800);
      case 1: return const Color(0xFFB8860B);
      default: return const Color(0xFF8B9D8B);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return RefreshIndicator(
      color: theme.colorScheme.primary,
      onRefresh: _loadValidators,
      child: _isLoading
        ? const Center(child: CircularProgressIndicator())
        : SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Staking & Validators', style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Text('DPoS consensus with green validator scoring', style: theme.textTheme.bodySmall),
                const SizedBox(height: 20),

                // Summary cards
                Row(
                  children: [
                    Expanded(
                      child: Card(
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                          side: BorderSide(color: theme.colorScheme.outline),
                        ),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Active Validators', style: theme.textTheme.bodySmall),
                              const SizedBox(height: 4),
                              Text('$_activeCount', style: theme.textTheme.headlineMedium?.copyWith(
                                fontWeight: FontWeight.bold, color: const Color(0xFF00FF88),
                              )),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Card(
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                          side: BorderSide(color: theme.colorScheme.outline),
                        ),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Total Staked', style: theme.textTheme.bodySmall),
                              const SizedBox(height: 4),
                              Text('${_formatStake(_totalStaked)} VRDX', style: theme.textTheme.headlineMedium?.copyWith(
                                fontWeight: FontWeight.bold, color: const Color(0xFF00FF88),
                              )),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // Validator list
                Text('Validators (${_validators.length})', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),

                if (_error != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: Text(_error!, style: TextStyle(color: theme.colorScheme.error, fontSize: 13)),
                  ),

                ..._validators.map((v) {
                  final validator = v as Map<String, dynamic>;
                  final name = validator['name'] ?? 'Unknown';
                  final address = validator['address'] ?? '';
                  final stake = (validator['stake'] as num? ?? 0).toInt();
                  final greenScore = (validator['greenScore'] as num? ?? 0).toInt();
                  final isActive = validator['isActive'] == true;

                  return Card(
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
                            width: 44,
                            height: 44,
                            decoration: BoxDecoration(
                              color: _scoreColor(greenScore).withOpacity(0.15),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(Icons.energy_savings_leaf, color: _scoreColor(greenScore), size: 24),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Text(name, style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                                    const SizedBox(width: 8),
                                    if (isActive)
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                        decoration: BoxDecoration(
                                          color: const Color(0xFF00FF88).withOpacity(0.15),
                                          borderRadius: BorderRadius.circular(6),
                                        ),
                                        child: const Text('Active', style: TextStyle(color: Color(0xFF00FF88), fontSize: 10, fontWeight: FontWeight.bold)),
                                      )
                                    else
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                        decoration: BoxDecoration(
                                          color: const Color(0xFF8B9D8B).withOpacity(0.15),
                                          borderRadius: BorderRadius.circular(6),
                                        ),
                                        child: const Text('Inactive', style: TextStyle(color: Color(0xFF8B9D8B), fontSize: 10)),
                                      ),
                                  ],
                                ),
                                const SizedBox(height: 4),
                                Text(_shortAddr(address), style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'monospace')),
                                const SizedBox(height: 4),
                                Row(
                                  children: [
                                    Text('${_formatStake(stake)} VRDX', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: theme.colorScheme.primary)),
                                    const SizedBox(width: 12),
                                    Row(
                                      children: [
                                        Icon(Icons.eco, size: 14, color: _scoreColor(greenScore)),
                                        const SizedBox(width: 4),
                                        Text('Green: $greenScore', style: TextStyle(fontSize: 11, color: _scoreColor(greenScore))),
                                      ],
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ],
            ),
          ),
    );
  }
}
