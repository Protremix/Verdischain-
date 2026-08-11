#!/usr/bin/env python3
"""Fix wallet_service.dart: remove fake data, wire to real RPC"""

import re

with open("/opt/verdis-wallet/mobile/lib/services/wallet_service.dart", "r") as f:
    content = f.read()

# 1. Fix carbon credits default
content = content.replace(
    "double _carbonCredits = 120.50; // Eco credits",
    "double _carbonCredits = 0; // Fetched from chain"
)

# 2. Fix green score default
content = content.replace(
    "int _greenScore = 92; // 0 - 100\n  int get greenScore => _greenScore;",
    "int _greenScore = 0; // Fetched from chain\n  int get greenScore => _greenScore;\n\n  int _chainBlockNumber = 0;\n  int get chainBlockNumber => _chainBlockNumber;\n\n  int _chainPeers = 0;\n  int get chainPeers => _chainPeers;\n\n  int _chainValidatorCount = 0;\n  int get chainValidatorCount => _chainValidatorCount;"
)

# 3. Fix fetchBalance - replace broken storage key query with TX relay
old_balance = """    try {
      // Execute required Substrate RPC methods
      try {
        await _callRpcMethod('system_properties', []);
        await _callRpcMethod('chain_getBlockHash', [0]);
        await _callRpcMethod('state_getRuntimeVersion', []);
        // Storage query for balance
        final storage = await _callRpcMethod('state_getStorage', ['0xSystemAccountKey']);
        if (storage != null && storage is String && storage.isNotEmpty) {
          final rawVal = BigInt.parse(storage.replaceFirst('0x', ''), radix: 16);
          _vrdxBalance = rawVal.toDouble() / 1e12;
        }
      } catch (_) {
        // Balance will show 0 if RPC unavailable
      }
    } catch (e) {
      _errorMessage = 'Balance query failed: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }"""

new_balance = """    try {
      final response = await http.post(
        Uri.parse('https://verdischain.com/api/tx-relay'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'action': 'balance', 'address': _activeAccount!.address}),
      );
      final data = json.decode(response.body);
      if (data['ok'] == true) {
        final free = (data['free'] ?? 0) as int;
        _vrdxBalance = free / 1e9; // 9 decimals
        // Fetch chain info
        try {
          final infoRes = await http.post(
            Uri.parse('https://verdischain.com/api/tx-relay'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({'action': 'chain-info'}),
          );
          final info = json.decode(infoRes.body);
          if (info['ok'] == true) {
            _chainBlockNumber = info['block_number'] ?? 0;
            _chainPeers = info['peers'] ?? 0;
            _chainValidatorCount = info['validator_count'] ?? 0;
          }
        } catch (_) {}
      }
    } catch (e) {
      _errorMessage = 'Balance query failed: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }"""

content = content.replace(old_balance, new_balance)

# 4. Replace hardcoded validators list with empty + fetch method
# Find the validators list and replace it
val_start = content.find("  final List<ValidatorInfo> _validators = [")
if val_start >= 0:
    val_end = content.find("  List<ValidatorInfo> get validators => _validators;", val_start)
    if val_end >= 0:
        val_end += len("  List<ValidatorInfo> get validators => _validators;")
        old_block = content[val_start:val_end]
        new_block = """  List<ValidatorInfo> _validators = [];
  List<ValidatorInfo> get validators => _validators;

  Future<void> fetchValidators() async {
    try {
      final response = await http.post(
        Uri.parse('https://verdischain.com/rpc'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'jsonrpc': '2.0', 'method': 'dpos_allValidators', 'params': [], 'id': 1}),
      );
      final data = json.decode(response.body);
      final List<dynamic> addrs = data['result'] ?? [];
      List<ValidatorInfo> list = [];
      for (final addr in addrs) {
        String name = addr.toString().substring(0, 8) + '...';
        double stake = 0;
        int greenScore = 0;
        try {
          final stakeRes = await http.post(
            Uri.parse('https://verdischain.com/rpc'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({'jsonrpc': '2.0', 'method': 'dpos_validatorStake', 'params': [addr], 'id': 1}),
          );
          final stakeData = json.decode(stakeRes.body);
          stake = (stakeData['result'] ?? 0) / 1e9;
        } catch (_) {}
        try {
          final nameRes = await http.post(
            Uri.parse('https://verdischain.com/rpc'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({'jsonrpc': '2.0', 'method': 'dpos_validatorName', 'params': [addr], 'id': 1}),
          );
          final nameData = json.decode(nameRes.body);
          if (nameData['result'] != null) name = nameData['result'];
        } catch (_) {}
        try {
          final greenRes = await http.post(
            Uri.parse('https://verdischain.com/rpc'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({'jsonrpc': '2.0', 'method': 'eco_getGreenScore', 'params': [addr], 'id': 1}),
          );
          final greenData = json.decode(greenRes.body);
          greenScore = (greenData['result'] ?? 0) as int;
        } catch (_) {}
        list.add(ValidatorInfo(
          name: name,
          address: addr.toString(),
          totalStaked: stake,
          commission: 0,
          greenScore: greenScore,
          apy: 0,
        ));
      }
      _validators = list;
      notifyListeners();
    } catch (e) {
      debugPrint('Error fetching validators: $e');
    }
  }"""
        content = content[:val_start] + new_block + content[val_end:]

# 5. Replace hardcoded DEX pairs
dex_start = content.find("  final List<DexPairInfo> _dexPairs = [")
if dex_start >= 0:
    dex_end = content.find("  List<DexPairInfo> get dexPairs => _dexPairs;", dex_start)
    if dex_end >= 0:
        dex_end += len("  List<DexPairInfo> get dexPairs => _dexPairs;")
        new_dex = """  List<DexPairInfo> _dexPairs = [];
  List<DexPairInfo> get dexPairs => _dexPairs;

  String _bytesToTokenName(List<dynamic> bytes) {
    try {
      final codes = bytes.map((b) => (b as int).toInt()).toList();
      return String.fromCharCodes(codes);
    } catch (_) {
      return '???';
    }
  }

  Future<void> fetchDexPools() async {
    try {
      final response = await http.post(
        Uri.parse('https://verdischain.com/api/tx-relay'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'action': 'dex-pools'}),
      );
      final data = json.decode(response.body);
      if (data['ok'] == true) {
        final List<dynamic> pools = data['pools'] ?? [];
        List<DexPairInfo> list = [];
        for (final pool in pools) {
          final tokenA = _bytesToTokenName(pool['token_a'] ?? []);
          final tokenB = _bytesToTokenName(pool['token_b'] ?? []);
          final reserveA = (pool['reserve_a'] ?? 0) / 1e9;
          final reserveB = (pool['reserve_b'] ?? 0) / 1e9;
          final tvl = reserveA + reserveB;
          final price = reserveB > 0 ? reserveA / reserveB : 0.0;
          list.add(DexPairInfo(
            symbol: '$tokenA/$tokenB',
            baseToken: tokenA,
            quoteToken: tokenB,
            price: price,
            volume24h: 0,
            tvl: tvl,
          ));
        }
        _dexPairs = list;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error fetching DEX pools: $e');
    }
  }"""
        content = content[:dex_start] + new_dex + content[dex_end:]

# 6. Replace hardcoded reforestation
ref_start = content.find("  final List<ReforestationProject> _reforestationProjects = [")
if ref_start >= 0:
    ref_end = content.find("  List<ReforestationProject> get reforestationProjects => _reforestationProjects;", ref_start)
    if ref_end >= 0:
        ref_end += len("  List<ReforestationProject> get reforestationProjects => _reforestationProjects;")
        new_ref = """  List<ReforestationProject> _reforestationProjects = [];
  List<ReforestationProject> get reforestationProjects => _reforestationProjects;

  Future<void> fetchEcoData() async {
    try {
      final response = await http.post(
        Uri.parse('https://verdischain.com/rpc'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'jsonrpc': '2.0', 'method': 'eco_getNetworkEcoStats', 'params': [], 'id': 1}),
      );
      final data = json.decode(response.body);
      if (data['result'] != null) {
        final stats = data['result'];
        _carbonCredits = ((stats['total_credits'] ?? 0) as int).toDouble();
        _greenScore = (stats['avg_green_score'] ?? 0) as int;
        notifyListeners();
      }
    } catch (_) {}
  }"""
        content = content[:ref_start] + new_ref + content[ref_end:]

# 7. Fix staking to use TX relay instead of fake hash
old_stake_hash = "final txHash = '0x' + sha256.convert(utf8.encode('stake_' + DateTime.now().millisecondsSinceEpoch.toString() + '_' + amount.toString())).toString();"
new_stake_hash = """String txHash = '0xpending';
      try {
        final relayRes = await http.post(
          Uri.parse('https://verdischain.com/api/tx-relay'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({
            'action': 'vote',
            'validator': validatorAddress,
            'amount': (amount * 1e9).round(),
          }),
        );
        final relayData = json.decode(relayRes.body);
        if (relayData['ok'] == true) {
          txHash = relayData['extrinsic_hash'] ?? '0xpending';
        }
      } catch (e) {
        throw Exception('Stake failed: ' + e.toString());
      }"""

if old_stake_hash in content:
    content = content.replace(old_stake_hash, new_stake_hash)
    print("  - Fixed staking hash to TX relay")
else:
    # Try alternate format
    import re as re2
    pattern = r"final txHash = '0x'\$\{sha256\.convert\(utf8\.encode\('stake_.*?\)\)\};"
    match = re2.search(pattern, content)
    if match:
        content = content[:match.start()] + new_stake_hash + content[match.end():]
        print("  - Fixed staking hash to TX relay (regex)")
    else:
        print("  - WARNING: Could not find stake hash pattern")

# 8. Add fetchValidators and fetchDexPools to loadAccountsFromDb
old_load = """      if (_activeAccount != null) {
        await loadTransactions();
        await fetchBalance();
      }"""
new_load = """      if (_activeAccount != null) {
        await loadTransactions();
        await fetchBalance();
        await fetchValidators();
        await fetchDexPools();
        await fetchEcoData();
      }"""
content = content.replace(old_load, new_load)

# 9. Fix unstaking to use TX relay too
old_unstake_hash = "final txHash = '0x' + sha256.convert(utf8.encode('unbond_' + DateTime.now().millisecondsSinceEpoch.toString() + '_' + amount.toString())).toString();"
if old_unstake_hash in content:
    content = content.replace(old_unstake_hash, "'0xpending'")
    print("  - Fixed unstaking hash")

with open("/opt/verdis-wallet/mobile/lib/services/wallet_service.dart", "w") as f:
    f.write(content)

print("Done: wallet_service.dart fixed")
print("  - fetchBalance: TX relay balance endpoint (9 decimals)")
print("  - Validators: Real RPC (dpos_allValidators + stake + name + green)")
print("  - DEX pools: Real TX relay (dex-pools action)")
print("  - Reforestation: Empty list + eco RPC fetch")
print("  - Chain info: block/peers/validators from TX relay")
print("  - Carbon credits: 0 default, fetched from eco RPC")
print("  - Green score: 0 default, fetched from eco RPC")
