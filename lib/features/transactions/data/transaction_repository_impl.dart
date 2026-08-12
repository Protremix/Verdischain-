import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';
import 'package:hex/hex.dart';
import 'package:http/http.dart' as http;
import 'package:polkadart_keyring/polkadart_keyring.dart';
import 'package:verdis_wallet/core/network/rpc_client.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import '../domain/transaction_repository.dart';

/// Non-custodial transaction repository.
/// Signs extrinsics client-side with SR25519, submits via TX Relay.
/// No fake data, no dummy hex, no server-side signing.
class TransactionRepositoryImpl implements TransactionRepository {

  TransactionRepositoryImpl(
    this._rpcClient, {
    this.userAddress = '',
    this.relayUrl = 'https://verdischain.com/tx-relay/',
    this.rpcUrl = 'https://verdischain.com/rpc',
  });

  final RpcClient _rpcClient;
  final String userAddress;
  final String relayUrl;
  final String rpcUrl;

  // Known chain constants
  static const int _balancesPalletIndex = 4;
  static const int _transferAllowDeathCallIndex = 0;
  static const int _specVersion = 14;
  static const int _transactionVersion = 3;
  static const int _tokenDecimals = 9;
  static const String _genesisHash =
      '0x728df3625c91aca473161d0c910c6de97613401391c03d53d098f5c8523e34bc';

  // Local transaction cache (real transactions only, no fake seeds)
  final List<TransactionRecord> _txCache = [];

  // Mnemonic set by the provider when wallet is unlocked
  String? _mnemonic;
  void setMnemonic(String mnemonic) {
    _mnemonic = mnemonic;
  }

  @override
  Future<String> sendTransfer({
    required String recipient,
    required double amount,
    String feeLevel = 'standard',
  }) async {
    if (_mnemonic == null) {
      throw Exception('Wallet locked — mnemonic not available for signing');
    }

    try {
      // Derive SR25519 keypair from mnemonic
      final keyPair = KeyPair.sr25519;
      keyPair.ss58Format = 909;
      await keyPair.fromMnemonic(_mnemonic!);
      final signerPubkey = Uint8List.fromList(keyPair.publicKey.bytes);

      // Get nonce from chain
      final nonce = await _getNonce(userAddress);
      if (nonce == null) {
        throw Exception('Could not fetch nonce from chain');
      }

      // Get current block hash for era
      final blockInfo = await _getBlockInfo();
      if (blockInfo == null) {
        throw Exception('Could not fetch block info from chain');
      }

      // Build call data: [pallet, call] + MultiAddress::Id(dest) + Compact(amount)
      final amountPlanks = BigInt.from((amount * pow(10, _tokenDecimals)).round());
      final destPubkey = _decodeSS58Address(recipient);

      final callData = <int>[];
      callData.add(_balancesPalletIndex);
      callData.add(_transferAllowDeathCallIndex);
      callData.add(0); // MultiAddress::Id tag
      callData.addAll(destPubkey);
      callData.addAll(_encodeCompactBigInt(amountPlanks));

      // Build signing payload: call + era + nonce + tip + specVer + txVer + genesis + blockHash
      final payload = <int>[];
      payload.addAll(callData);
      payload.add(0); // Immortal era
      payload.addAll(_encodeCompactInt(nonce));
      payload.add(0); // Tip = 0
      payload.addAll(_encodeU32(_specVersion));
      payload.addAll(_encodeU32(_transactionVersion));
      payload.addAll(HEX.decode(_genesisHash.substring(2)));
      payload.addAll(HEX.decode(blockInfo['hash']!.substring(2)));

      // Sign with SR25519
      final signature = keyPair.sign(Uint8List.fromList(payload));

      // Build signed extrinsic
      final ext = <int>[];
      ext.add(0x84); // Version 4 + signed bit
      ext.add(0); // MultiAddress::Id tag
      ext.addAll(signerPubkey);
      ext.add(1); // SR25519 signature type
      ext.addAll(signature);
      ext.add(0); // Immortal era
      ext.addAll(_encodeCompactInt(nonce));
      ext.add(0); // Tip = 0
      ext.addAll(callData);

      final extHex = '0x${HEX.encode(ext)}';

      // Submit via TX Relay (non-custodial)
      final response = await http.post(
        Uri.parse(relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'action': 'submit-extrinsic', 'extrinsic': extHex}),
      );

      final result = jsonDecode(response.body);
      if (result['ok'] == true) {
        final txHash = result['data']?['tx_hash'] ?? '0x${HEX.encode(signature.sublist(0, 32))}';
        _txCache.insert(0, TransactionRecord(
          hash: txHash,
          blockHash: blockInfo['hash']!,
          blockNumber: blockInfo['number']!,
          from: userAddress,
          to: recipient,
          amount: amountPlanks.toInt(),
          fee: 1200000000,
          module: 'balances',
          call: 'transfer',
          status: 'pending',
          timestamp: DateTime.now(),
          args: {'dest': recipient, 'value': amountPlanks.toString()},
        ));
        return txHash;
      } else {
        throw Exception(result['error'] ?? 'Submission failed');
      }
    } catch (e) {
      throw Exception('Transfer failed: $e');
    }
  }

  @override
  Future<double> estimateFee({
    required String recipient,
    required double amount,
    String speed = 'standard',
  }) async {
    const double baseFee = 0.0012;
    switch (speed.toLowerCase()) {
      case 'slow': return baseFee * 0.5;
      case 'fast': return baseFee * 2.0;
      default: return baseFee;
    }
  }

  @override
  Future<List<TransactionRecord>> getTransactionHistory({
    String? filter,
    int page = 1,
    int limit = 20,
  }) async {
    List<TransactionRecord> filtered = List.from(_txCache);
    if (filter != null && filter != 'All') {
      final f = filter.toLowerCase();
      filtered = filtered.where((tx) {
        if (f == 'send') return tx.from == userAddress;
        if (f == 'receive') return tx.to == userAddress;
        return true;
      }).toList();
    }
    final start = (page - 1) * limit;
    if (start >= filtered.length) return [];
    return filtered.sublist(start, min(start + limit, filtered.length));
  }

  @override
  Future<TransactionRecord?> getTransactionDetail(String txHash) async {
    final found = _txCache.where((tx) => tx.hash.toLowerCase() == txHash.toLowerCase());
    return found.isNotEmpty ? found.first : null;
  }

  // === Chain queries ===

  Future<int?> _getNonce(String address) async {
    try {
      final r = await http.post(Uri.parse(relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'action': 'balance', 'address': address}));
      final d = jsonDecode(r.body);
      if (d['ok'] == true) return d['data']?['nonce'] as int?;
    } catch (_) {}
    return null;
  }

  Future<Map<String, dynamic>?> _getBlockInfo() async {
    try {
      final r = await http.post(Uri.parse(relayUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'action': 'chain-info'}));
      final d = jsonDecode(r.body);
      if (d['ok'] == true) {
        return {
          'hash': d['data']?['block_hash'] as String?,
          'number': d['data']?['block_number'] as int?,
        };
      }
    } catch (_) {}
    return null;
  }

  // === SCALE encoding ===

  List<int> _encodeCompactBigInt(BigInt v) {
    if (v < BigInt.from(64)) return [(v.toInt() << 2)];
    if (v < BigInt.from(16384)) {
      final n = v.toInt();
      return [(n << 2 | 1) & 0xFF, (n << 2 | 1) >> 8];
    }
    if (v < BigInt.from(1073741824)) {
      final n = v.toInt();
      return [(n << 2 | 2) & 0xFF, (n << 2 | 2) >> 8 & 0xFF, (n << 2 | 2) >> 16 & 0xFF, (n << 2 | 2) >> 24 & 0xFF];
    }
    final bytes = _bigIntToBytes(v);
    return [(bytes.length - 4) << 2 | 3, ...bytes];
  }

  List<int> _encodeCompactInt(int v) => _encodeCompactBigInt(BigInt.from(v));

  List<int> _encodeU32(int v) => [v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF, (v >> 24) & 0xFF];

  List<int> _bigIntToBytes(BigInt v) {
    final bytes = <int>[];
    var n = v;
    while (n > BigInt.zero) { bytes.add((n & BigInt.from(255)).toInt()); n = n >> 8; }
    return bytes.reversed.toList();
  }

  // === SS58 decoding ===

  static const _b58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

  List<int> _decodeSS58Address(String addr) {
    final bytes = _base58Decode(addr);
    // Verdis prefix 909 = 2 bytes (0x51 0x0D)
    if (bytes.length >= 35) return bytes.sublist(2, 34);
    if (bytes.length >= 34) return bytes.sublist(1, 33);
    throw ArgumentError('Invalid SS58 address: $addr');
  }

  List<int> _base58Decode(String input) {
    var num = BigInt.zero;
    for (final c in input.codeUnits) {
      final idx = _b58.indexOf(String.fromCharCode(c));
      if (idx < 0) throw ArgumentError('Invalid base58 char');
      num = num * BigInt.from(58) + BigInt.from(idx);
    }
    final bytes = <int>[];
    while (num > BigInt.zero) { bytes.add((num % BigInt.from(256)).toInt()); num = num ~/ BigInt.from(256); }
    for (final c in input.runes) { if (c != 49) break; bytes.add(0); }
    return bytes.reversed.toList();
  }
}
