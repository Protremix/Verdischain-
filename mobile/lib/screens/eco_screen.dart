import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/wallet_service.dart';
import '../widgets/verdis_button.dart';

class EcoScreen extends StatefulWidget {
  const EcoScreen({super.key});

  @override
  State<EcoScreen> createState() => _EcoScreenState();
}

class _EcoScreenState extends State<EcoScreen> {
  final TextEditingController _mintController = TextEditingController();
  final TextEditingController _retireController = TextEditingController();

  void _showMintModal(BuildContext context) {
    _mintController.clear();
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
                'Mint Carbon Credits',
                style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'Mint VERD-ECO credits by verifying renewable energy generation or verified offset certificates.',
                style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _mintController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 16),
                decoration: const InputDecoration(
                  labelText: 'Amount of VERD-ECO',
                  labelStyle: TextStyle(color: Color(0xFF94a3b8)),
                  filled: true,
                  fillColor: Color(0xFF040806),
                  enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF2E2E34))),
                  focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF16a34a))),
                ),
              ),
              const SizedBox(height: 20),
              Consumer<WalletService>(
                builder: (context, wallet, child) {
                  return VerdisButton(
                    label: 'Mint VERD-ECO',
                    isLoading: wallet.isLoading,
                    onPressed: () async {
                      final amt = double.tryParse(_mintController.text.trim());
                      if (amt == null || amt <= 0) return;
                      final success = await wallet.mintCarbonCredits(amt);
                      if (ctx.mounted) Navigator.pop(ctx);
                      if (success) {
                        if (!context.mounted) return;
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Minted $amt VERD-ECO carbon credits'),
                            backgroundColor: const Color(0xFF0D1410),
                          ),
                        );
                      }
                    },
                  );
                },
              ),
            ],
          ),
        );
      },
    );
  }

  void _showRetireModal(BuildContext context, ReforestationProject project) {
    _retireController.clear();
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
              Text(
                'Support ${project.name}',
                style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(
                'Location: ${project.location}',
                style: const TextStyle(color: Color(0xFF16a34a), fontSize: 12),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _retireController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 16),
                decoration: const InputDecoration(
                  labelText: 'Credits to Retire / Contribute',
                  labelStyle: TextStyle(color: Color(0xFF94a3b8)),
                  filled: true,
                  fillColor: Color(0xFF040806),
                  enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF2E2E34))),
                  focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFF16a34a))),
                ),
              ),
              const SizedBox(height: 20),
              Consumer<WalletService>(
                builder: (context, wallet, child) {
                  return VerdisButton(
                    label: 'Contribute & Retire Credits',
                    isLoading: wallet.isLoading,
                    onPressed: () async {
                      final amt = double.tryParse(_retireController.text.trim());
                      if (amt == null || amt <= 0) return;
                      final success = await wallet.retireCarbonCredits(project.id, amt);
                      if (ctx.mounted) Navigator.pop(ctx);
                      if (success) {
                        if (!context.mounted) return;
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Contributed $amt credits to ${project.name}'),
                            backgroundColor: const Color(0xFF0D1410),
                          ),
                        );
                      }
                    },
                  );
                },
              ),
            ],
          ),
        );
      },
    );
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
          'Verdis Eco Dashboard',
          style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Eco header card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF0D1410), Color(0xFF232A26)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF16a34a).withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Verified Carbon Credits',
                          style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFF16a34a).withOpacity(0.2),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Text(
                            'Verified On-Chain',
                            style: TextStyle(color: Color(0xFF16a34a), fontSize: 11, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.baseline,
                      textBaseline: TextBaseline.alphabetic,
                      children: [
                        Text(
                          wallet.carbonCredits.toStringAsFixed(2),
                          style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 26, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(width: 8),
                        const Text('VERD-ECO', style: TextStyle(color: Color(0xFF16a34a), fontSize: 14, fontWeight: FontWeight.bold)),
                      ],
                    ),
                    const SizedBox(height: 16),
                    const Text('Green Score Rating', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 11)),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        Expanded(
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(4),
                            child: LinearProgressIndicator(
                              value: wallet.greenScore / 100.0,
                              backgroundColor: const Color(0xFF040806),
                              valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF16a34a)),
                              minHeight: 8,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          '${wallet.greenScore}/100',
                          style: const TextStyle(color: Color(0xFF16a34a), fontWeight: FontWeight.bold, fontSize: 13),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    VerdisButton(
                      label: 'Mint Carbon Credits',
                      icon: Icons.add,
                      onPressed: () => _showMintModal(context),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              const Text(
                'Verified Reforestation Projects',
                style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 15, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              const Text(
                'Retire carbon credits directly to support high-impact ecosystem protection.',
                style: TextStyle(color: Color(0xFF94a3b8), fontSize: 12),
              ),
              const SizedBox(height: 16),

              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: wallet.reforestationProjects.length,
                separatorBuilder: (_, __) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final proj = wallet.reforestationProjects[index];
                  final progress = proj.raisedCredits / proj.targetCredits;

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
                              proj.name,
                              style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 14, fontWeight: FontWeight.bold),
                            ),
                            Text(
                              proj.location,
                              style: const TextStyle(color: Color(0xFF16a34a), fontSize: 11, fontWeight: FontWeight.w500),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(
                          proj.description,
                          style: const TextStyle(color: Color(0xFF94a3b8), fontSize: 12, height: 1.3),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              '${proj.treesPlanted.toString()} trees planted',
                              style: const TextStyle(color: Color(0xFFFFFFFF), fontSize: 11, fontWeight: FontWeight.w500),
                            ),
                            Text(
                              '${(progress * 100).toStringAsFixed(0)}% Funded',
                              style: const TextStyle(color: Color(0xFF94a3b8), fontSize: 11),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: progress.clamp(0.0, 1.0),
                            backgroundColor: const Color(0xFF040806),
                            valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF16a34a)),
                            minHeight: 6,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Align(
                          alignment: Alignment.centerRight,
                          child: OutlinedButton.icon(
                            style: OutlinedButton.styleFrom(
                              foregroundColor: const Color(0xFF16a34a),
                              side: const BorderSide(color: Color(0xFF16a34a)),
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            ),
                            icon: const Icon(Icons.nature_people, size: 16),
                            label: const Text('Support / Retire Credits', style: TextStyle(fontSize: 12)),
                            onPressed: () => _showRetireModal(context, proj),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _mintController.dispose();
    _retireController.dispose();
    super.dispose();
  }
}
