// DEX View — shows real on-chain AMM pools from TX Relay API
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class DexView extends ConsumerStatefulWidget {
  const DexView({super.key});

  @override
  ConsumerState<DexView> createState() => _DexViewState();
}

class _DexViewState extends ConsumerState<DexView> {
  List<dynamic> _pools = [];
  bool _isLoading = true;
  String? _error;

  static const String _relayUrl = 'https://verdischain.com/api/tx-relay';

  @override
  void initState() {
    super.initState();
    _loadPools();
  }

  Future<void> _loadPools() async {
    try {
      final response = await http.post(
        Uri.parse(_relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'action': 'dex-pools'}),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['ok'] == true) {
          setState(() {
            _pools = data['data']?['pools'] ?? [];
            _isLoading = false;
          });
          return;
        }
      }
      setState(() { _isLoading = false; _error = 'Failed to load pools'; });
    } catch (e) {
      setState(() { _isLoading = false; _error = e.toString(); });
    }
  }

  String _formatReserve(int reserve) {
    final vrdx = reserve / 1e9;
    if (vrdx >= 1e9) return '${(vrdx / 1e9).toStringAsFixed(2)}B';
    if (vrdx >= 1e6) return '${(vrdx / 1e6).toStringAsFixed(2)}M';
    if (vrdx >= 1e3) return '${(vrdx / 1e3).toStringAsFixed(2)}K';
    return vrdx.toStringAsFixed(2);
  }

  String _poolTokenA(Map<String, dynamic> pool) {
    return pool['tokenA'] ?? pool['token_a']?.toString() ?? '???';
  }

  String _poolTokenB(Map<String, dynamic> pool) {
    return pool['tokenB'] ?? pool['token_b']?.toString() ?? '???';
  }

  int _poolReserveA(Map<String, dynamic> pool) {
    return pool['reserveA'] ?? pool['reserve_a'] ?? 0;
  }

  int _poolReserveB(Map<String, dynamic> pool) {
    return pool['reserveB'] ?? pool['reserve_b'] ?? 0;
  }

  double _poolFee(Map<String, dynamic> pool) {
    final num_ = pool['feeNumerator'] ?? pool['fee_numerator'] ?? 3;
    final den = pool['feeDenominator'] ?? pool['fee_denominator'] ?? 1000;
    return (num_ as int) / (den as int) * 100;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return RefreshIndicator(
      color: theme.colorScheme.primary,
      onRefresh: _loadPools,
      child: _isLoading
        ? const Center(child: CircularProgressIndicator())
        : SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Verdis DEX', style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFF00FF88).withOpacity(0.12),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text('${_pools.length} Pools', style: TextStyle(color: const Color(0xFF00FF88), fontSize: 12, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text('AMM liquidity pools on Verdis Chain', style: theme.textTheme.bodySmall),
                const SizedBox(height: 20),

                if (_error != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: Text(_error!, style: TextStyle(color: theme.colorScheme.error, fontSize: 13)),
                  ),

                if (_pools.isEmpty && _error == null)
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
                          Icon(Icons.water_drop_outlined, size: 40, color: Color(0xFF8B9D8B)),
                          SizedBox(height: 12),
                          Text('No liquidity pools found', style: TextStyle(color: Color(0xFF8B9D8B))),
                        ],
                      ),
                    ),
                  ),

                // Pool list
                ..._pools.map((pool) {
                  final p = pool as Map<String, dynamic>;
                  final tokenA = _poolTokenA(p);
                  final tokenB = _poolTokenB(p);
                  final reserveA = _poolReserveA(p);
                  final reserveB = _poolReserveB(p);
                  final fee = _poolFee(p);

                  // Calculate price ratio
                  String priceRatio = '';
                  if (reserveA > 0 && reserveB > 0) {
                    final ratio = reserveB / reserveA;
                    priceRatio = '1 $tokenA = ${ratio.toStringAsFixed(4)} $tokenB';
                  }

                  return Card(
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
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF00FF88).withOpacity(0.12),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  '$tokenA / $tokenB',
                                  style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF00FF88), fontSize: 14),
                                ),
                              ),
                              const Spacer(),
                              Text('${fee.toStringAsFixed(1)}% fee', style: theme.textTheme.bodySmall),
                            ],
                          ),
                          const SizedBox(height: 16),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              _reserveTile(tokenA, _formatReserve(reserveA)),
                              _reserveTile(tokenB, _formatReserve(reserveB)),
                            ],
                          ),
                          if (priceRatio.isNotEmpty) ...[
                            const SizedBox(height: 12),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                              decoration: BoxDecoration(
                                color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.5),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(priceRatio, style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'monospace')),
                            ),
                          ],
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

  Widget _reserveTile(String token, String reserve) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(token, style: const TextStyle(fontSize: 12, color: Color(0xFF8B9D8B))),
          const SizedBox(height: 4),
          Text(reserve, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, fontFamily: 'monospace')),
        ],
      ),
    );
  }
}
