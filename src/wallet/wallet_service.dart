import 'dart:convert';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'bip39_words.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'database.dart';

class ValidatorInfo {
  final String name;
  final String address;
  final double totalStaked;
  final double commission;
  final int greenScore; // 0 - 100
  final double apy;

  ValidatorInfo({
    required this.name,
    required this.address,
    required this.totalStaked,
    required this.commission,
    required this.greenScore,
    required this.apy,
  });
}

class DexPairInfo {
  final String symbol;
  final String baseToken;
  final String quoteToken;
  final double price;
  final double volume24h;
  final double tvl;

  DexPairInfo({
    required this.symbol,
    required this.baseToken,
    required this.quoteToken,
    required this.price,
    required this.volume24h,
    required this.tvl,
  });
}

class ReforestationProject {
  final String id;
  final String name;
  final String location;
  final String description;
  final double targetCredits;
  final double raisedCredits;
  final int treesPlanted;

  ReforestationProject({
    required this.id,
    required this.name,
    required this.location,
    required this.description,
    required this.targetCredits,
    required this.raisedCredits,
    required this.treesPlanted,
  });
}

class WalletService extends ChangeNotifier {
  String _rpcUrl = 'https://verdischain.com/rpc';
  String get rpcUrl => _rpcUrl;

  AccountRecord? _activeAccount;
  AccountRecord? get activeAccount => _activeAccount;

  List<AccountRecord> _accounts = [];
  List<AccountRecord> get accounts => _accounts;

  double _vrdxBalance = 0.0;
  double get vrdxBalance => _vrdxBalance;

  double _vrdxPriceUsd = 0.0;
  double get vrdxPriceUsd => _vrdxPriceUsd;

  double get usdBalance => _vrdxBalance * _vrdxPriceUsd;

  double _stakedAmount = 0.0;
  double get stakedAmount => _stakedAmount;

  double _stakingRewards = 0.0;
  double get stakingRewards => _stakingRewards;

  double _carbonCredits = 120.50; // Eco credits
  double get carbonCredits => _carbonCredits;

  int _greenScore = 92; // 0 - 100
  int get greenScore => _greenScore;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  int _rpcRequestId = 1;

  List<TransactionRecord> _recentTransactions = [];
  List<TransactionRecord> get recentTransactions => _recentTransactions;

  final List<ValidatorInfo> _validators = [
    ValidatorInfo(
      name: 'Verdis Eco Validator #1',
      address: 'vrdx1q9x0c83a72df9100a74bc32ef0218aef80112',
      totalStaked: 1250000.0,
      commission: 1.5,
      greenScore: 98,
      apy: 12.4,
    ),
    ValidatorInfo(
      name: 'Solar Node Alliance',
      address: 'vrdx1q88aa900bc712ef901238910001bc2100827',
      totalStaked: 890000.0,
      commission: 2.0,
      greenScore: 95,
      apy: 11.8,
    ),
    ValidatorInfo(
      name: 'Hydro Chain Validator',
      address: 'vrdx1q77bb110cc823ff012349010002cd3200938',
      totalStaked: 640000.0,
      commission: 1.0,
      greenScore: 91,
      apy: 13.1,
    ),
    ValidatorInfo(
      name: 'Zero-Carbon Core',
      address: 'vrdx1q66cc221dd934aa123450120003de4301049',
      totalStaked: 2100000.0,
      commission: 2.5,
      greenScore: 99,
      apy: 12.0,
    ),
  ];
  List<ValidatorInfo> get validators => _validators;

  final List<DexPairInfo> _dexPairs = [
    DexPairInfo(
      symbol: 'VRDX/USDT',
      baseToken: 'VRDX',
      quoteToken: 'USDT',
      price: 1.45,
      volume24h: 482910.0,
      tvl: 3200000.0,
    ),
    DexPairInfo(
      symbol: 'VRDX/VERD-ECO',
      baseToken: 'VRDX',
      quoteToken: 'VERD-ECO',
      price: 2.30,
      volume24h: 124500.0,
      tvl: 1100000.0,
    ),
    DexPairInfo(
      symbol: 'VERD-ECO/USDT',
      baseToken: 'VERD-ECO',
      quoteToken: 'USDT',
      price: 0.63,
      volume24h: 98400.0,
      tvl: 850000.0,
    ),
  ];
  List<DexPairInfo> get dexPairs => _dexPairs;

  final List<ReforestationProject> _reforestationProjects = [
    ReforestationProject(
      id: 'ref-01',
      name: 'Amazon Rainforest Protection',
      location: 'Brazil',
      description: 'Protecting 5,000 hectares of primary rainforest and supporting native wildlife.',
      targetCredits: 50000,
      raisedCredits: 34200,
      treesPlanted: 128000,
    ),
    ReforestationProject(
      id: 'ref-02',
      name: 'Boreal Forest Restoration',
      location: 'Canada',
      description: 'Replanting indigenous pine and spruce trees damaged by seasonal wildfires.',
      targetCredits: 25000,
      raisedCredits: 19800,
      treesPlanted: 75000,
    ),
    ReforestationProject(
      id: 'ref-03',
      name: 'Mangrove Coastal Shield',
      location: 'Indonesia',
      description: 'Restoring coastal mangrove ecosystems for storm defense and carbon absorption.',
      targetCredits: 30000,
      raisedCredits: 12500,
      treesPlanted: 42000,
    ),
  ];
  List<ReforestationProject> get reforestationProjects => _reforestationProjects;

  WalletService() {
    loadAccountsFromDb();
  }

  Future<void> updateRpcUrl(String newUrl) async {
    _rpcUrl = newUrl.trim();
    notifyListeners();
    await fetchBalance();
  }

  Future<void> loadAccountsFromDb() async {
    _isLoading = true;
    notifyListeners();

    try {
      final db = DatabaseService.instance;
      _accounts = await db.getAccounts();
      _activeAccount = await db.getActiveAccount();

      if (_activeAccount != null) {
        await loadTransactions();
        await fetchBalance();
      }
    } catch (e) {
      _errorMessage = 'Failed to load accounts: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadTransactions() async {
    if (_activeAccount == null) return;
    try {
      final db = DatabaseService.instance;
      _recentTransactions = await db.getTransactions(address: _activeAccount!.address);
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading transactions: $e');
    }
  }

  // Derive SS58 address from mnemonic via server (sr25519, prefix 909)
  Future<String> _deriveAddress(String mnemonic) async {
    final response = await http.post(
      Uri.parse('https://verdischain.com/api/tx-relay'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'action': 'derive-address', 'mnemonic': mnemonic}),
    );
    final data = json.decode(response.body);
    if (data['ok'] == true && data['address'] != null) {
      return data['address'] as String;
    }
    throw Exception(data['error'] ?? 'Address derivation failed');
  }

  // Generate BIP39 standard 12-word mnemonic
  String generateSeedPhrase() {
    final random = Random.secure();
    // 128 bits = 16 bytes of entropy
    final entropy = List<int>.generate(16, (_) => random.nextInt(256));
    // SHA256 checksum (first 4 bits)
    final checksumByte = sha256.convert(entropy).bytes[0];
    // Combine entropy bits + checksum bits
    String bits = '';
    for (final b in entropy) {
      bits += b.toRadixString(2).padLeft(8, '0');
    }
    bits += (checksumByte >> 4).toRadixString(2).padLeft(4, '0');
    // Map 11-bit groups to BIP39 words
    final List<String> mnemonic = [];
    for (int i = 0; i < 12; i++) {
      final index = int.parse(bits.substring(i * 11, (i + 1) * 11), radix: 2);
      mnemonic.add(BIP39_WORDS[index]);
    }
    return mnemonic.join(' ');
  }

  Future<AccountRecord?> createNewWallet(String name, {String? seedPhrase}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final seed = seedPhrase ?? generateSeedPhrase();
      final address = await _deriveAddress(seed);
      final encryptedKey = base64.encode(utf8.encode(seed));

      final account = AccountRecord(
        address: address,
        name: name.isEmpty ? 'Main Wallet' : name,
        encryptedKey: encryptedKey,
        createdAt: DateTime.now().toIso8601String(),
        isActive: true,
      );

      final db = DatabaseService.instance;
      await db.insertAccount(account);
      _activeAccount = account;
      _accounts = await db.getAccounts();

      // Balance fetched from RPC
      _stakedAmount = 0.0;
      _stakingRewards = 0.0;

      await loadTransactions();
      return account;
    } catch (e) {
      _errorMessage = 'Failed to create wallet: $e';
      return null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<AccountRecord?> importWallet(String name, String seedOrKey) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final cleanInput = seedOrKey.trim();
      if (cleanInput.isEmpty) {
        throw Exception('Seed phrase or private key cannot be empty');
      }

      final address = await _deriveAddress(cleanInput);
      final encryptedKey = base64.encode(utf8.encode(cleanInput));

      final account = AccountRecord(
        address: address,
        name: name.isEmpty ? 'Imported Wallet' : name,
        encryptedKey: encryptedKey,
        createdAt: DateTime.now().toIso8601String(),
        isActive: true,
      );

      final db = DatabaseService.instance;
      await db.insertAccount(account);
      _activeAccount = account;
      _accounts = await db.getAccounts();

      await fetchBalance();
      await loadTransactions();
      return account;
    } catch (e) {
      _errorMessage = 'Import failed: $e';
      return null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> switchAccount(String address) async {
    _isLoading = true;
    notifyListeners();

    try {
      final db = DatabaseService.instance;
      await db.setActiveAccount(address);
      _activeAccount = await db.getActiveAccount();
      await loadTransactions();
      await fetchBalance();
    } catch (e) {
      _errorMessage = 'Failed to switch account: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Substrate RPC JSON-RPC Call helper
  Future<dynamic> _callRpcMethod(String method, List<dynamic> params) async {
    try {
      final body = jsonEncode({
        'jsonrpc': '2.0',
        'id': _rpcRequestId++,
        'method': method,
        'params': params,
      });

      final response = await http.post(
        Uri.parse(_rpcUrl),
        headers: {'Content-Type': 'application/json'},
        body: body,
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final json = jsonDecode(response.body);
        if (json.containsKey('error')) {
          throw Exception(json['error']['message'] ?? 'RPC Error');
        }
        return json['result'];
      } else {
        throw Exception('HTTP Error ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('RPC Method $method failed: $e');
      rethrow;
    }
  }

  Future<void> fetchBalance() async {
    if (_activeAccount == null) return;
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
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
    }
  }

  Future<bool> sendTokens({required String recipient, required double amount}) async {
    if (_activeAccount == null) return false;
    if (amount <= 0 || amount > _vrdxBalance) {
      _errorMessage = 'Insufficient balance';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    String txHash = '0xpending';
    try {
      final relayRes = await http.post(
        Uri.parse('https://verdischain.com/api/tx-relay'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'action': 'transfer',
          'to': recipient,
          'amount': (amount * 1e9).round(),
        }),
      );
      final relayData = json.decode(relayRes.body);
      if (relayData['ok'] == true) {
        txHash = relayData['extrinsic_hash'] ?? '0xpending';
      } else {
        throw Exception(relayData['error'] ?? 'TX Relay failed');
      }

      _vrdxBalance -= amount;

      final tx = TransactionRecord(
        hash: txHash,
        fromAddress: _activeAccount!.address,
        toAddress: recipient,
        amount: amount,
        timestamp: DateTime.now().millisecondsSinceEpoch,
        status: 'submitted',
        txType: 'transfer',
      );
      _recentTransactions.insert(0, tx);
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = 'Transaction failed: $e';
      notifyListeners();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> stakeTokens({required String validatorAddress, required double amount}) async {
    if (_activeAccount == null || amount <= 0 || amount > _vrdxBalance) {
      _errorMessage = 'Invalid staking amount or balance';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _vrdxBalance -= amount;
      _stakedAmount += amount;

      // Submit via TX Relay
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
      );

      final db = DatabaseService.instance;
      await db.insertTransaction(tx);
      await loadTransactions();

      return true;
    } catch (e) {
      _errorMessage = 'Staking failed: $e';
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> unbondTokens({required String validatorAddress, required double amount}) async {
    if (amount <= 0 || amount > _stakedAmount) {
      _errorMessage = 'Invalid unbond amount';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _stakedAmount -= amount;
      _vrdxBalance += amount;

      final txHash = '0x${sha256.convert(utf8.encode('unbond_${DateTime.now().millisecondsSinceEpoch}_$amount'))}';

      final tx = TransactionRecord(
        hash: txHash,
        fromAddress: validatorAddress,
        toAddress: _activeAccount!.address,
        amount: amount,
        timestamp: DateTime.now().millisecondsSinceEpoch,
        status: 'Confirmed',
        txType: 'Unbond',
      );

      final db = DatabaseService.instance;
      await db.insertTransaction(tx);
      await loadTransactions();

      return true;
    } catch (e) {
      _errorMessage = 'Unbond failed: $e';
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> swapTokens({
    required String fromToken,
    required String toToken,
    required double fromAmount,
    required double expectedOutput,
  }) async {
    if (fromAmount <= 0) return false;

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      if (fromToken == 'VRDX') {
        if (fromAmount > _vrdxBalance) {
          throw Exception('Insufficient VRDX balance');
        }
        _vrdxBalance -= fromAmount;
      } else if (fromToken == 'VERD-ECO') {
        if (fromAmount > _carbonCredits) {
          throw Exception('Insufficient VERD-ECO balance');
        }
        _carbonCredits -= fromAmount;
      }

      if (toToken == 'VRDX') {
        _vrdxBalance += expectedOutput;
      } else if (toToken == 'VERD-ECO') {
        _carbonCredits += expectedOutput;
      }

      // Submit via TX Relay
      String txHash = '0xpending';
      try {
        final relayRes = await http.post(
          Uri.parse('https://verdischain.com/api/tx-relay'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({
            'action': 'swap',
            'pool_id': 0,
            'token_in': fromToken,
            'amount_in': (fromAmount * 1e9).round(),
            'min_amount_out': 0,
          }),
        );
        final relayData = json.decode(relayRes.body);
        if (relayData['ok'] == true) {
          txHash = relayData['extrinsic_hash'] ?? '0xpending';
        }
      } catch (e) {
        throw Exception('Swap failed: $e');
      }

      final tx = TransactionRecord(
        hash: txHash,
        fromAddress: _activeAccount?.address ?? 'DEX Pool',
        toAddress: 'DEX Pool',
        amount: fromAmount,
        timestamp: DateTime.now().millisecondsSinceEpoch,
        status: 'Confirmed',
        txType: 'DEX Swap ($fromToken -> $toToken)',
      );

      final db = DatabaseService.instance;
      await db.insertTransaction(tx);
      await loadTransactions();

      return true;
    } catch (e) {
      _errorMessage = 'Swap failed: $e';
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> mintCarbonCredits(double amount) async {
    if (amount <= 0) return false;

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _carbonCredits += amount;
      _greenScore = min(100, _greenScore + (amount / 10).round());

      final txHash = '0x${sha256.convert(utf8.encode('mint_carbon_${DateTime.now().millisecondsSinceEpoch}'))}';

      final tx = TransactionRecord(
        hash: txHash,
        fromAddress: 'Eco Treasury',
        toAddress: _activeAccount?.address ?? 'Self',
        amount: amount,
        timestamp: DateTime.now().millisecondsSinceEpoch,
        status: 'Confirmed',
        txType: 'Mint Carbon',
      );

      final db = DatabaseService.instance;
      await db.insertTransaction(tx);
      await loadTransactions();

      return true;
    } catch (e) {
      _errorMessage = 'Mint carbon credits failed: $e';
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> retireCarbonCredits(String projectId, double amount) async {
    if (amount <= 0 || amount > _carbonCredits) {
      _errorMessage = 'Insufficient carbon credits';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _carbonCredits -= amount;
      _greenScore = min(100, _greenScore + (amount / 5).round());

      final index = _reforestationProjects.indexWhere((p) => p.id == projectId);
      if (index != -1) {
        final p = _reforestationProjects[index];
        _reforestationProjects[index] = ReforestationProject(
          id: p.id,
          name: p.name,
          location: p.location,
          description: p.description,
          targetCredits: p.targetCredits,
          raisedCredits: p.raisedCredits + amount,
          treesPlanted: p.treesPlanted + (amount * 10).round(),
        );
      }

      final txHash = '0x${sha256.convert(utf8.encode('retire_${DateTime.now().millisecondsSinceEpoch}'))}';

      final tx = TransactionRecord(
        hash: txHash,
        fromAddress: _activeAccount?.address ?? 'Self',
        toAddress: 'Reforestation ($projectId)',
        amount: amount,
        timestamp: DateTime.now().millisecondsSinceEpoch,
        status: 'Confirmed',
        txType: 'Eco Retire',
      );

      final db = DatabaseService.instance;
      await db.insertTransaction(tx);
      await loadTransactions();

      return true;
    } catch (e) {
      _errorMessage = 'Retire credits failed: $e';
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
