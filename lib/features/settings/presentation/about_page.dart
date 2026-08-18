import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:verdis_wallet/core/config/network_config.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';

class AboutPage extends ConsumerStatefulWidget {
  const AboutPage({super.key});

  @override
  ConsumerState<AboutPage> createState() => _AboutPageState();
}

class _AboutPageState extends ConsumerState<AboutPage> {
  String _version = AppConstants.appVersion;
  String _buildNumber = AppConstants.appBuild;

  @override
  void initState() {
    super.initState();
    _loadPackageInfo();
  }

  Future<void> _loadPackageInfo() async {
    try {
      final info = await PackageInfo.fromPlatform();
      setState(() {
        _version = info.version;
        _buildNumber = info.buildNumber;
      });
    } catch (_) {}
  }

  // Use launchUrl directly — canLaunchUrl returns false on Android 11+
  // without <queries> in manifest, even when the URL is launchable.
  Future<void> _launchUrl(String url) async {
    try {
      final uri = Uri.parse(url);
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } catch (_) {
      // Fallback: try in-app browser
      try {
        final uri = Uri.parse(url);
        await launchUrl(uri, mode: LaunchMode.inAppBrowserView);
      } catch (_) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Could not open: $url')),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('About Verdis')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Brand logo
          Center(
            child: Column(
              children: [
                Image.asset(
                  'assets/images/verdis-logo-white.png',
                  width: 96,
                  height: 96,
                  fit: BoxFit.contain,
                ),
                const SizedBox(height: 16),
                Text('Verdis Wallet', style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(height: 4),
                Text('v$_version+$_buildNumber', style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
          ),
          const SizedBox(height: 32),

          // About Verdis Chain — improved text
          const _SectionTitle('About Verdis Chain'),
          VerdisCard(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Energy-Efficient Blockchain Ecosystem',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: Theme.of(context).colorScheme.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Verdis Chain is a Substrate-based blockchain infrastructure designed for energy efficiency. '
                    'It features native DPoS consensus with BABE/GRANDPA finality, on-chain carbon credit tracking, '
                    'reforestation logging, and green validator scoring — incentivizing environmentally responsible '
                    'blockchain participation.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'The ecosystem includes a native AMM-based decentralized exchange (DEX), fungible token support, '
                    'governance, vesting, and presale pallets — all built as custom Substrate runtime modules.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 16),
                  // Key stats
                  _buildStatRow(context, 'Token', 'VRDX'),
                  _buildStatRow(context, 'Total Supply', '100,000,000,000 VRDX'),
                  _buildStatRow(context, 'Consensus', 'DPoS (BABE/GRANDPA)'),
                  _buildStatRow(context, 'Decimals', '9'),
                  _buildStatRow(context, 'Network Status', 'Testnet'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Links
          const _SectionTitle('Links'),
          VerdisCard(
            child: Column(
              children: [
                _buildLinkTile(
                  icon: Icons.language,
                  title: 'Website',
                  subtitle: 'verdischain.com',
                  url: 'https://verdischain.com',
                ),
                const Divider(height: 1),
                _buildLinkTile(
                  icon: Icons.explore,
                  title: 'Block Explorer',
                  subtitle: 'verdischain.com/explorer',
                  url: NetworkConfig.explorerUrl,
                ),
                const Divider(height: 1),
                _buildLinkTile(
                  icon: Icons.menu_book,
                  title: 'Documentation',
                  subtitle: 'docs.verdischain.com',
                  url: 'https://docs.verdischain.com',
                ),
                const Divider(height: 1),
                _buildLinkTile(
                  icon: Icons.local_drink,
                  title: 'Faucet',
                  subtitle: 'verdischain.com/faucet',
                  url: NetworkConfig.faucetUrl,
                ),
                const Divider(height: 1),
                _buildLinkTile(
                  icon: Icons.code,
                  title: 'GitHub',
                  subtitle: 'github.com/Protremix/Verdischain-',
                  url: 'https://github.com/Protremix/Verdischain-',
                ),
                const Divider(height: 1),
                _buildLinkTile(
                  icon: Icons.email,
                  title: 'Contact',
                  subtitle: 'info@verdischain.com',
                  url: 'mailto:info@verdischain.com',
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Legal
          const _SectionTitle('Legal'),
          VerdisCard(
            child: Column(
              children: [
                _buildLinkTile(
                  icon: Icons.description,
                  title: 'Privacy Policy',
                  subtitle: 'verdischain.com/privacy',
                  url: 'https://verdischain.com/privacy',
                ),
                const Divider(height: 1),
                _buildLinkTile(
                  icon: Icons.security,
                  title: 'Security',
                  subtitle: 'verdischain.com/security',
                  url: 'https://verdischain.com/security',
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Community
          const _SectionTitle('Community'),
          VerdisCard(
            child: Column(
              children: [
                _buildLinkTile(
                  icon: Icons.chat,
                  title: 'WhatsApp Support',
                  subtitle: '+44 7451 261353',
                  url: 'https://wa.me/447451261353',
                ),
                const Divider(height: 1),
                _buildLinkTile(
                  icon: Icons.article,
                  title: 'Whitepaper',
                  subtitle: 'verdischain.com/whitepaper',
                  url: 'https://verdischain.com/whitepaper',
                ),
                const Divider(height: 1),
                _buildLinkTile(
                  icon: Icons.swap_horiz,
                  title: 'DEX',
                  subtitle: 'verdischain.com/dex',
                  url: 'https://verdischain.com/dex',
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),

          Center(
            child: Text(
              '© 2026 Verdis Chain\nAll rights reserved',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildStatRow(BuildContext context, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLinkTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required String url,
  }) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      subtitle: Text(subtitle, style: const TextStyle(fontSize: 12)),
      trailing: const Icon(Icons.open_in_new, size: 18),
      onTap: () => _launchUrl(url),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle(this.title);
  final title;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, left: 4),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleSmall?.copyWith(
          color: Theme.of(context).colorScheme.primary,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
