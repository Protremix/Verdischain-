import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/config/network_config.dart';
import 'package:verdis_wallet/core/network/rpc_client.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';

class NetworkSettingsPage extends ConsumerStatefulWidget {
  const NetworkSettingsPage({super.key});

  @override
  ConsumerState<NetworkSettingsPage> createState() => _NetworkSettingsPageState();
}

class _NetworkSettingsPageState extends ConsumerState<NetworkSettingsPage> {
  String _selectedEndpoint = NetworkConfig.rpcUrl;
  bool _isTesting = false;
  Map<String, dynamic>? _testResult;
  int? _latencyMs;

  final List<String> _endpoints = [
    NetworkConfig.rpcUrl,
    'https://rpc2.verdischain.com',
    'https://testnet.verdischain.com',
  ];

  Future<void> _testConnection() async {
    setState(() {
      _isTesting = true;
      _testResult = null;
      _latencyMs = null;
    });

    try {
      final rpc = ref.read(rpcClientProvider);
      final stopwatch = Stopwatch()..start();

      final health = await rpc.getHealth();
      final chainName = await rpc.getChainName();
      final version = await rpc.getRuntimeVersion();

      stopwatch.stop();

      setState(() {
        _testResult = {
          'health': health,
          'chainName': chainName,
          'version': version,
        };
        _latencyMs = stopwatch.elapsedMilliseconds;
      });
    } catch (e) {
      setState(() {
        _testResult = {'error': e.toString()};
      });
    } finally {
      setState(() => _isTesting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Network & RPC')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Current endpoint
          VerdisCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('RPC Endpoint', style: Theme.of(context).textTheme.titleSmall),
                const SizedBox(height: 12),
                ...List.generate(_endpoints.length, (index) {
                  final endpoint = _endpoints[index];
                  return RadioListTile<String>(
                    title: Text(endpoint),
                    value: endpoint,
                    groupValue: _selectedEndpoint,
                    onChanged: (value) {
                      if (value != null) {
                        setState(() => _selectedEndpoint = value);
                      }
                    },
                    dense: true,
                  );
                }),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.add),
                  title: const Text('Add Custom Endpoint'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    // Show custom endpoint dialog
                    _showCustomEndpointDialog();
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Connection test
          VerdisCard(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Connection Test', style: Theme.of(context).textTheme.titleSmall),
                      ElevatedButton(
                        onPressed: _isTesting ? null : _testConnection,
                        child: _isTesting
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Text('Test'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  if (_latencyMs != null) ...[
                    _InfoRow('Latency', '${_latencyMs}ms'),
                    const SizedBox(height: 8),
                    _InfoRow('Status',
                      _latencyMs! < 500 ? 'Excellent' : _latencyMs! < 1500 ? 'Good' : 'Slow',
                    ),
                  ],
                  if (_testResult != null && _testResult!['error'] == null) ...[
                    const SizedBox(height: 12),
                    const Divider(),
                    const SizedBox(height: 12),
                    _InfoRow('Chain', _testResult!['chainName']?.toString() ?? 'Unknown'),
                    const SizedBox(height: 8),
                    _InfoRow('Peers', _testResult!['health']?['peers']?.toString() ?? '0'),
                    const SizedBox(height: 8),
                    _InfoRow('Is Syncing', _testResult!['health']?['isSyncing']?.toString() ?? 'Unknown'),
                  ],
                  if (_testResult != null && _testResult!['error'] != null) ...[
                    const SizedBox(height: 12),
                    Text('Error: ${_testResult!['error']}',
                      style: TextStyle(color: Theme.of(context).colorScheme.error),
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Chain info
          VerdisCard(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Chain Info', style: Theme.of(context).textTheme.titleSmall),
                  const SizedBox(height: 12),
                  const _InfoRow('Name', NetworkConfig.chainName),
                  const SizedBox(height: 8),
                  const _InfoRow('Type', NetworkConfig.chainType),
                  const SizedBox(height: 8),
                  const _InfoRow('Consensus', NetworkConfig.consensus),
                  const SizedBox(height: 8),
                  _InfoRow('Chain ID', NetworkConfig.chainId.toString()),
                  const SizedBox(height: 8),
                  const _InfoRow('Token', '${NetworkConfig.tokenName} (${NetworkConfig.tokenSymbol})'),
                  const SizedBox(height: 8),
                  const _InfoRow('Supply', '${NetworkConfig.totalSupply} ${NetworkConfig.tokenSymbol}'),
                  const SizedBox(height: 8),
                  const _InfoRow('Validators', '${NetworkConfig.validatorCount} active / ${NetworkConfig.totalNodes} total'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showCustomEndpointDialog() {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Custom Endpoint'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'RPC URL',
            hintText: 'https://custom-node.example.com',
          ),
          keyboardType: TextInputType.url,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final url = controller.text.trim();
              if (url.isNotEmpty) {
                setState(() {
                  _endpoints.add(url);
                  _selectedEndpoint = url;
                });
                Navigator.pop(context);
              }
            },
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {

  const _InfoRow(this.label, this.value);
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: Theme.of(context).textTheme.bodySmall),
        Text(value, style: Theme.of(context).textTheme.bodyMedium?.copyWith(
          fontWeight: FontWeight.w500,
        ),),
      ],
    );
  }
}
