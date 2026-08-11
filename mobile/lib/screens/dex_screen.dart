import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/wallet_service.dart';
import '../widgets/verdis_button.dart';

class DexScreen extends StatefulWidget {
  const DexScreen({super.key});

  @override
  State<DexScreen> createState() => _DexScreenState();
}

class _DexScreenState extends State<DexScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  final TextEditingController _fromAmountController = TextEditingController();
  final TextEditingController _toAmountController = TextEditingController();

  String _fromToken = 'VRDX';
  String _toToken = 'VERD-ECO';
  double _estimatedPrice = 2.30; // 1 VRDX = 2.30 VERD-ECO
  final double _slippageTolerance = 0.5; // 0.5%
  String? _errorText;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _fromAmountController.addListener(_recalculateOutput);
  }

  void _recalculateOutput() {
    final input = double.tryParse(_fromAmountController.text.trim());
    if (input != null && input > 0) {
      final out = input * _estimatedPrice;
      _toAmountController.text = out.toStringAsFixed(4);
    } else {
      _toAmountController.clear();
    }
  }

  void _swapTokenPositions() {
    setState(() {
      final tempToken = _fromToken;
      _fromToken = _toToken;
      _toToken = tempToken;
      _estimatedPrice = 1.0 / _estimatedPrice;
      _fromAmountController.clear();
      _toAmountController.clear();
    });
  }

  Future<void> _executeSwap() async {
    final fromAmount = double.tryParse(_fromAmountController.text.trim());
    final toAmount = double.tryParse(_toAmountController.text.trim());

    if (fromAmount == null || fromAmount <= 0) {
      setState(() => _errorText = 'Enter a valid swap amount');
      return;
    }

    final wallet = Provider.of<WalletService>(context, listen: false);

    setState(() => _errorText = null);

    final success = await wallet.swapTokens(
      fromToken: _fromToken,
      toToken: _toToken,
      fromAmount: fromAmount,
      expectedOutput: toAmount ?? (fromAmount * _estimatedPrice),
    );

    if (mounted) {
      if (success) {
        _fromAmountController.clear();
        _toAmountController.clear();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Swap order executed on Verdis DEX'),
            backgroundColor: Color(0xFF0D1410),
          ),
        );
      } else {
        setState(() {
          _errorText = wallet.errorMessage ?? 'Swap execution failed';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final wallet = Provider.of<WalletService>(context);

    return Scaffold(
      backgroundColor: const Color(0xFF040806),
      appBar: AppBar(
        backgroundColor: const Color(0xFF040806),
        elevation: 0,
        title: const Text(
          'Verdis DEX',
          style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 16, fontWeight: FontWeight.bold),
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: const Color(0xFF16a34a),
          labelColor: const Color(0xFF16a34a),
          unselectedLabelColor: const Color(0xFF94a3b8),
          tabs: const [
            Tab(text: 'Swap'),
            Tab(text: 'Liquidity Pools'),
          ],
        ),
      ),
      body: SafeArea(
        child: TabBarView(
          controller: _tabController,
          children: [
            _buildSwapTab(wallet),
            _buildPoolsTab(wallet),
          ],
        ),
      ),
    );
  }

  Widget _buildSwapTab(WalletService wallet) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_errorText != null) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFEF4444).withOpacity(0.15),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFEF4444)),
              ),
              child: Text(
                _errorText!,
                style: const TextStyle(color: Color(0xFFEF4444), fontSize: 12),
              ),
            ),
            const SizedBox(height: 16),
          ],

          // Pay box
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF0D1410),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFF2E2E34)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('You Pay', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12)),
                    Text(
                      'Bal: ${_fromToken == "VRDX" ? wallet.vrdxBalance.toStringAsFixed(2) : wallet.carbonCredits.toStringAsFixed(2)} $_fromToken',
                      style: const TextStyle(color: Color(0xFF94a3b8), fontSize: 12),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _fromAmountController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 22, fontWeight: FontWeight.bold),
                        decoration: const InputDecoration(
                          hintText: '0.0',
                          hintStyle: TextStyle(color: Color(0xFF94a3b8)),
                          border: InputBorder.none,
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFF040806),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: const Color(0xFF2E2E34)),
                      ),
                      child: Text(
                        _fromToken,
                        style: const TextStyle(color: Color(0xFF16a34a), fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Swap icon button
          Center(
            child: Transform.translate(
              offset: const Offset(0, 0),
              child: IconButton(
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0D1410),
                    shape: BoxShape.circle,
                    border: Border.all(color: const Color(0xFF16a34a)),
                  ),
                  child: const Icon(Icons.swap_vert, color: Color(0xFF16a34a), size: 20),
                ),
                onPressed: _swapTokenPositions,
              ),
            ),
          ),

          // Receive box
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF0D1410),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFF2E2E34)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('You Receive (Estimated)', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12)),
                    Text(
                      'Bal: ${_toToken == "VRDX" ? wallet.vrdxBalance.toStringAsFixed(2) : wallet.carbonCredits.toStringAsFixed(2)} $_toToken',
                      style: const TextStyle(color: Color(0xFF94a3b8), fontSize: 12),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _toAmountController,
                        readOnly: true,
                        style: const TextStyle(color: Color(0xFF16a34a), fontSize: 22, fontWeight: FontWeight.bold),
                        decoration: const InputDecoration(
                          hintText: '0.0',
                          hintStyle: TextStyle(color: Color(0xFF94a3b8)),
                          border: InputBorder.none,
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFF040806),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: const Color(0xFF2E2E34)),
                      ),
                      child: Text(
                        _toToken,
                        style: const TextStyle(color: Color(0xFF16a34a), fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Swap details
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF0D1410),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFF2E2E34)),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Exchange Rate', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12)),
                    Text('1 $_fromToken ≈ ${_estimatedPrice.toStringAsFixed(4)} $_toToken', style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 12)),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Slippage Tolerance', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12)),
                    Text('$_slippageTolerance%', style: const TextStyle(color: Color(0xFF16a34a), fontSize: 12, fontWeight: FontWeight.bold)),
                  ],
                ),
                const SizedBox(height: 8),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Route', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12)),
                    Text('Verdis Direct Pool', style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 12)),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          VerdisButton(
            label: 'Swap Tokens',
            isLoading: wallet.isLoading,
            onPressed: _executeSwap,
          ),
        ],
      ),
    );
  }

  Widget _buildPoolsTab(WalletService wallet) {
    return ListView.separated(
      padding: const EdgeInsets.all(20),
      itemCount: wallet.dexPairs.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        final pair = wallet.dexPairs[index];
        return Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF0D1410),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: const Color(0xFF2E2E34)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    pair.symbol,
                    style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 15, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    '\$${pair.price.toStringAsFixed(2)}',
                    style: const TextStyle(color: Color(0xFF16a34a), fontSize: 15, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('24h Volume', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 11)),
                      const SizedBox(height: 2),
                      Text('\$${(pair.volume24h / 1000).toStringAsFixed(1)}k', style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 12)),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      const Text('Total Value Locked', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 11)),
                      const SizedBox(height: 2),
                      Text('\$${(pair.tvl / 1000000).toStringAsFixed(2)}M', style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 12)),
                    ],
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    _fromAmountController.dispose();
    _toAmountController.dispose();
    super.dispose();
  }
}
