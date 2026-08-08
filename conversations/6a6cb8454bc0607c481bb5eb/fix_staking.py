with open('/opt/verdis-wallet/mobile/lib/services/wallet_service.dart', 'r') as f:
    content = f.read()

# Fix staking txHash scope: move declaration outside try, remove final inside
old = """      // Submit via TX Relay
      try {
        final relayRes = await http.post(
          Uri.parse('https://verdischain.com/api/tx-relay'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({'action': 'vote', 'validator': validatorAddress}),
        );
        final relayData = json.decode(relayRes.body);
        final txHash = relayData['extrinsic_hash'] ?? '0xpending';
      } catch (e) {
        throw Exception('Staking failed: $e');
      }

      final tx = TransactionRecord(
        hash: txHash,
        fromAddress: _activeAccount!.address,
        toAddress: validatorAddress,
        amount: amount,
        timestamp: DateTime.now().millisecondsSinceEpoch,
        status: 'Confirmed',
        txType: 'Stake',
      );"""

new = """      // Submit via TX Relay
      String txHash = '0xpending';
      try {
        final relayRes = await http.post(
          Uri.parse('https://verdischain.com/api/tx-relay'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({'action': 'vote', 'validator': validatorAddress}),
        );
        final relayData = json.decode(relayRes.body);
        if (relayData['ok'] == true) {
          txHash = relayData['extrinsic_hash'] ?? '0xpending';
        }
      } catch (e) {
        throw Exception('Staking failed: $e');
      }

      final tx = TransactionRecord(
        hash: txHash,
        fromAddress: _activeAccount!.address,
        toAddress: validatorAddress,
        amount: amount,
        timestamp: DateTime.now().millisecondsSinceEpoch,
        status: 'Confirmed',
        txType: 'Stake',
      );"""

if old in content:
    content = content.replace(old, new)
    print("Fixed staking txHash scope")
else:
    print("ERROR: Staking block not found")

with open('/opt/verdis-wallet/mobile/lib/services/wallet_service.dart', 'w') as f:
    f.write(content)
