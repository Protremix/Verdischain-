import 'package:flutter/material.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';

class StakingInfoPage extends StatelessWidget {
  const StakingInfoPage({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Staking & DPoS Guide'),
        actions: [
          IconButton(
            icon: const Icon(Icons.share_outlined),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Guide link copied to clipboard')),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Banner Card
            VerdisCard(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary.withOpacity(0.15),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.eco_rounded,
                      color: theme.colorScheme.primary,
                      size: 32,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Verdis Eco-Staking',
                          style: theme.textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Earn up to 15% APY while securing the world’s first zero-carbon Substrate blockchain.',
                          style: theme.textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Section 1: What is Staking?
            const _InfoSectionCard(
              icon: Icons.help_outline_rounded,
              title: 'What is Staking?',
              description:
                  'Staking in Verdis is the process of locking your VRD tokens to support network security, consensus, and block validation. In return for locking your tokens and delegating to reputable validators, you earn automated block rewards.',
              points: [
                'Earn passive yield paid directly in VRD.',
                'Tokens stay under your ownership in non-custodial smart contracts.',
                'Unstake anytime with a standard 7-day unbonding period.',
              ],
            ),

            const SizedBox(height: 16),

            // Section 2: How DPoS works in Verdis
            const _InfoSectionCard(
              icon: Icons.account_tree_outlined,
              title: 'How DPoS works in Verdis',
              description:
                  'Verdis utilizes a Green Delegated Proof of Stake (G-DPoS) consensus algorithm. Instead of resource-intensive mining, VRD holders vote for validators by delegating their stake to them.',
              points: [
                'Top active validators are selected every era (24 hours) based on total stake and Green Score.',
                'Validators produce blocks and share rewards proportionally with nominators.',
                'Commission rates are set by validators for node operation costs.',
              ],
            ),

            const SizedBox(height: 16),

            // Section 3: Green Scoring System
            const _InfoSectionCard(
              icon: Icons.energy_savings_leaf_outlined,
              title: 'Green Scoring System',
              description:
                  'To ensure sustainability, Verdis audits validator power infrastructure and assigns a Green Score (0–100). Delegating to high-scoring eco-validators boosts your APY yield!',
              points: [
                'Solar, Wind, Hydro, and Geothermal energy sources earn highest Green Scores.',
                'Real-time telemetry and RE100 zero-carbon certification audits.',
                'Up to +2.5% APY bonus multiplier for delegating to 95+ Green Score nodes.',
              ],
            ),

            const SizedBox(height: 16),

            // Section 4: Slashing Conditions
            const _InfoSectionCard(
              icon: Icons.gavel_outlined,
              title: 'Slashing Conditions',
              description:
                  'Slashing protects the Verdis network against malicious behavior or severe negligence by penalizing validator stake.',
              points: [
                'Double Signing: Producing two conflicting blocks at the same height results in 100% slash.',
                'Unresponsiveness / Downtime: Extended node offline time results in a minor 0.1% slash.',
                'Delegators share proportional risk; choose highly reliable validators with strong uptime.',
              ],
            ),

            const SizedBox(height: 16),

            // Section 5: Validator Requirements
            const _InfoSectionCard(
              icon: Icons.hardware_outlined,
              title: 'Validator Requirements',
              description:
                  'Operating a Verdis validator node requires high-performance hardware and verified renewable energy powering.',
              points: [
                'Hardware: 8 Dedicated vCPUs, 32GB RAM, 500GB High-Speed NVMe SSD.',
                'Network: 1Gbps fiber connection with 99.9% uptime SLA.',
                'Self-Stake: Minimum 50,000 VRD self-bond required.',
                'Clean Power: Verified renewable energy provenance documentation.',
              ],
            ),

            const SizedBox(height: 16),

            // Section 6: How to Become a Validator
            const _InfoSectionCard(
              icon: Icons.rocket_launch_outlined,
              title: 'How to Become a Validator',
              description:
                  'Follow these steps to setup a full node and register as an active validator on Verdis:',
              points: [
                'Step 1: Deploy a Verdis node binary on Ubuntu 22.04 LTS.',
                'Step 2: Sync blockchain state and generate session keys (`author_rotateKeys`).',
                'Step 3: Submit `dpos.registerValidator` extrinsic with session keys and self-stake.',
                'Step 4: Upload renewable energy audit proof to the Verdis Sustainability Portal.',
              ],
            ),

            const SizedBox(height: 24),

            // CTA Button
            VerdisButton(
              label: 'Start Staking Now',
              icon: Icons.arrow_forward_rounded,
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

class _InfoSectionCard extends StatelessWidget {

  const _InfoSectionCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.points,
  });
  final IconData icon;
  final String title;
  final String description;
  final List<String> points;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return VerdisCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: theme.colorScheme.primary, size: 22),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  title,
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            description,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurface,
            ),
          ),
          if (points.isNotEmpty) ...[
            const SizedBox(height: 12),
            ...points.map(
              (p) => Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '• ',
                      style: TextStyle(
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Expanded(
                      child: Text(
                        p,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
