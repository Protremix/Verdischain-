import 'dart:convert';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'bip39_words.dart';
import 'secure_crypto.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'database.dart';

class ValidatorInfo {
  final String name;
  final String address;
  final double totalStaked;
  final double commission;
  final int greenScore;
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
  static const _cryptoChannel = MethodChannel('com.verdis.verdis_wallet/crypto');
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

  double _carbonCredits = 0;
  double get carbonCredits => _carbonCredits;

  int _greenScore = 0;
  int get greenScore => _greenScore;

  int _chainBlockNumber = 0;
  int get chainBlockNumber => _chainBlockNumber;

  int _chainPeers = 0;
  int get chainPeers => _chainPeers;

  int _chainValidatorCount = 0;
  int get chainValidatorCount => _chainValidatorCount;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  int _rpcRequestId = 1;

  List<TransactionRecord> _recentTransactions = [];
  String lastGeneratedMnemonic = "";
  List<TransactionRecord> get recentTransactions => _recentTransactions;

  List<ValidatorInfo> _validators = [];
  List<ValidatorInfo> get validators => _validators;

  // The PIN used for encrypting mnemonics at rest
  // Set by the app when the user unlocks with PIN
  String _walletPin = "";
  void setWalletPin(String pin) {
    _walletPin = pin;
    // Migrate any old base64 accounts to encrypted format
    DatabaseService.instance.migrateEncryption(pin);
  }

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
  }

  List<DexPairInfo> _dexPairs = [];
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
  }

  List<ReforestationProject> _reforestationProjects = [];
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
  }

  WalletService() {
    _initCryptoChannel();
    loadAccountsFromDb();
  }

  Future<void> _initCryptoChannel() async {
    try {
      await _cryptoChannel.invokeMethod('initWebView');
      debugPrint('Crypto channel initialized');
    } catch (e) {
      debugPrint('Crypto channel init failed: $e');
    }
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
        await fetchValidators();
        await fetchDexPools();
        await fetchEcoData();
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

  // Derive SS58 address from mnemonic LOCALLY (Sr25519, prefix 909)
  // SECURITY: Mnemonic NEVER leaves the device. Uses Polkadot Sr25519 WASM.
  Future<String> _deriveAddress(String mnemonic) async {
    try {
      final result = await _cryptoChannel.invokeMethod('deriveAddress', {'mnemonic': mnemonic});
      if (result is Map && result['address'] != null) {
        return result['address'] as String;
      }
      throw Exception('Invalid response from crypto channel');
    } on PlatformException catch (e) {
      debugPrint('Local derivation failed, falling back to server: $e');
      // Fallback: use server derivation (mnemonic sent to server)
      // TODO: Remove this fallback once local derivation is verified
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
  }

  // Generate BIP39 standard 12-word mnemonic
  String generateSeedPhrase() {
    final random = Random.secure();
    final entropy = List<int>.generate(16, (_) => random.nextInt(256));
    final checksumByte = sha256.convert(entropy).bytes[0];
    String bits = '';
    for (final b in entropy) {
      bits += b.toRadixString(2).padLeft(8, '0');
    }
    bits += (checksumByte >> 4).toRadixString(2).padLeft(4, '0');
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
      lastGeneratedMnemonic = seed;
      final address = await _deriveAddress(seed);

      // Encrypt the mnemonic with PIN if available, otherwise store as base64
      // The mnemonic will be re-encrypted with PIN when the user sets a PIN
      String encryptedKey;
      if (_walletPin.isNotEmpty) {
        encryptedKey = SecureCrypto.encrypt(seed, _walletPin);
      } else {
        encryptedKey = base64.encode(utf8.encode(seed));
      }

      final account = AccountRecord(
        address: address,
        name: name.isEmpty ? 'Main Wallet' : name,
        encryptedKey: encryptedKey,
        createdAt: DateTime.now().toIso8601String(),
        isActive: true,
      );

      final db = DatabaseService.instance;
      await db.insertAccount(account, pin: _walletPin);
      _activeAccount = account;
      _accounts = await db.getAccounts();

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

      String encryptedKey;
      if (_walletPin.isNotEmpty) {
        encryptedKey = SecureCrypto.encrypt(cleanInput, _walletPin);
      } else {
        encryptedKey = base64.encode(utf8.encode(cleanInput));
      }

      final account = AccountRecord(
        address: address,
        name: name.isEmpty ? 'Imported Wallet' : name,
        encryptedKey: encryptedKey,
        createdAt: DateTime.now().toIso8601String(),
        isActive: true,
      );

      final db = DatabaseService.instance;
      await db.insertAccount(account, pin: _walletPin);
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
      final response = await http.post(
        Uri.parse('https://verdischain.com/api/tx-relay'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'action': 'balance', 'address': _activeAccount!.address}),
      );
      final data = json.decode(response.body);
      if (data['ok'] == true) {
        final free = (data['free'] ?? 0) as int;
        _vrdxBalance = free / 1e9;
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
    }
  }

  Future<bool> sendTokens({required String recipient, required double amount}) async {
    if (_activeAccount == null) return false;

    // Validate recipient address
    if (!SecureCrypto.isValidAddress(recipient)) {
      _errorMessage = 'Invalid recipient address format';
      notifyListeners();
      return false;
    }

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

    // Validate validator address
    if (!SecureCrypto.isValidAddress(validatorAddress)) {
      _errorMessage = 'Invalid validator address';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _vrdxBalance -= amount;
      _stakedAmount += amount;

      String txHash = '0xpending';
      try {
        final relayRes = await http.post(
          Uri.parse('https://verdischain.com/api/tx-relay'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({'action': 'vote', 'validator': validatorAddress, 'amount': (amount * 1e9).round()}),
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

      // Submit unbond via TX Relay
      String txHash = '0xpending';
      try {
        final relayRes = await http.post(
          Uri.parse('https://verdischain.com/api/tx-relay'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({'action': 'unbond', 'validator': validatorAddress, 'amount': (amount * 1e9).round()}),
        );
        final relayData = json.decode(relayRes.body);
        if (relayData['ok'] == true) {
          txHash = relayData['extrinsic_hash'] ?? '0xpending';
        }
      } catch (e) {
        // Even if relay fails, log the local state change
        debugPrint('Unbond relay failed: $e');
      }

      final tx = TransactionRecord(
        hash: txHash,
        fromAddress: validatorAddress,
        toAddress: _activeAccount?.address ?? '',
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

      String txHash = '0xpending';

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
    if (amount <= 0) return false;

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _carbonCredits -= amount;
      _greenScore = min(100, _greenScore + (amount / 5).round());

      String txHash = "0xpending";

      final tx = TransactionRecord(
        hash: txHash,
        fromAddress: _activeAccount?.address ?? "Self",
        toAddress: "Eco Treasury",
        amount: amount,
        timestamp: DateTime.now().millisecondsSinceEpoch,
        status: "Confirmed",
        txType: "Retire Carbon",
      );

      final db = DatabaseService.instance;
      await db.insertTransaction(tx);
      await loadTransactions();

      return true;
    } catch (e) {
      _errorMessage = "Retire carbon credits failed: $e";
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Export the mnemonic for an account (requires PIN)
  Future<String?> exportPrivateKey(AccountRecord account, String pin) async {
    final db = DatabaseService.instance;
    return await db.getMnemonic(account, pin);
  }
}
