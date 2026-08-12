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

  Future<void> _launchUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('About Verdis')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Brand logo — same asset used on the splash screen, for consistent branding
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

          // Links
          const _SectionTitle('Links'),
          VerdisCard(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.language),
                  title: const Text('verdischain.com'),
                  trailing: const Icon(Icons.open_in_new, size: 18),
                  onTap: () => _launchUrl('https://verdischain.com'),
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.menu_book),
                  title: const Text('Documentation'),
                  trailing: const Icon(Icons.open_in_new, size: 18),
                  onTap: () => _launchUrl('https://docs.verdischain.com'),
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.search),
                  title: const Text('Block Explorer'),
                  trailing: const Icon(Icons.open_in_new, size: 18),
                  onTap: () => _launchUrl(NetworkConfig.explorerUrl),
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.code),
                  title: const Text('GitHub'),
                  trailing: const Icon(Icons.open_in_new, size: 18),
                  onTap: () => _launchUrl('https://github.com/Protremix/Verdischain-'),
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.local_drink),
                  title: const Text('Faucet'),
                  trailing: const Icon(Icons.open_in_new, size: 18),
                  onTap: () => _launchUrl(NetworkConfig.faucetUrl),
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
                ListTile(
                  leading: const Icon(Icons.description),
                  title: const Text('Privacy Policy'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _launchUrl('https://verdischain.com/privacy'),
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.security),
                  title: const Text('Security'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _launchUrl('https://verdischain.com/security'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // About Verdis
          const _SectionTitle('About Verdis'),
          VerdisCard(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'The First Fully Green Blockchain Ecosystem',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Verdis is a carbon-negative blockchain ecosystem featuring on-chain carbon credits, '
                    'reforestation logging, and green validator scoring. Powered by BABE/GRANDPA consensus '
                    'with native DPoS, AMM DEX, and smart contract support.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Total Supply: ${NetworkConfig.totalSupply} ${NetworkConfig.tokenSymbol}',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                ],
              ),
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
        ],
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle(this.title);
  final String title;

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
