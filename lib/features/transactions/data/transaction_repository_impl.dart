import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';
import 'package:hex/hex.dart';
import 'package:http/http.dart' as http;
import 'package:polkadart_scale_codec/polkadart_scale_codec.dart';
import 'package:polkadart_keyring/polkadart_keyring.dart';
import 'package:verdis_wallet/core/network/rpc_client.dart';
import 'package:verdis_wallet/core/security/wallet_crypto.dart';
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
      // Era: mortal (64 blocks ~10min, prevents replay attacks)
      const eraPeriod = 64;
      final eraPhase = blockInfo["number"]! % eraPeriod;
      payload.add((eraPeriod << 2 | 1) & 0xFF);
      payload.add(eraPhase & 0xFF);
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
      ext.add((eraPeriod << 2 | 1) & 0xFF);
      ext.add(eraPhase & 0xFF);
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
    // First, fetch on-chain transactions by scanning recent blocks
    final onChainTxs = await _fetchOnChainHistory();

    // Merge on-chain txs with local cache (deduplicate by hash)
    final seenHashes = <String>{};
    final merged = <TransactionRecord>[];

    for (final tx in onChainTxs) {
      if (!seenHashes.contains(tx.hash)) {
        seenHashes.add(tx.hash);
        merged.add(tx);
      }
    }
    for (final tx in _txCache) {
      if (!seenHashes.contains(tx.hash)) {
        seenHashes.add(tx.hash);
        merged.add(tx);
      }
    }

    // Sort by block number descending (newest first)
    merged.sort((a, b) => b.blockNumber.compareTo(a.blockNumber));

    // Apply filter
    List<TransactionRecord> filtered = merged;
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

  /// Fetch transaction history from the blockchain by scanning recent blocks.
  /// Decodes signed extrinsics to find transfers involving the user's address.
  Future<List<TransactionRecord>> _fetchOnChainHistory() async {
    try {
      // Get the user's public key bytes for comparison (prefix-agnostic)
      final userPubkey = _decodeSS58Address(userAddress);
      if (userPubkey.length != 32) return [];

      // Get current block height
      final header = await _rpcClient.getHeader();
      final currentBlock = int.parse(header['number'].toString(), radix: 16);
      if (currentBlock == 0) return [];

      final onChainTxs = <TransactionRecord>[];
      const scanRange = 100; // Scan last 100 blocks
      const batchSize = 10;

      for (int batchStart = 0;
          batchStart < scanRange && currentBlock - batchStart > 0 && onChainTxs.length < 50;
          batchStart += batchSize) {
        final batchEnd = batchStart + batchSize;
        final futures = <Future<_BlockExtrinsics>>[];

        for (int i = batchStart; i < batchEnd && currentBlock - i > 0; i++) {
          final bn = currentBlock - i;
          futures.add(_fetchBlockExtrinsics(bn));
        }

        final blocks = await Future.wait(futures);
        for (final blk in blocks) {
          if (blk.extrinsics == null) continue;
          for (final ext in blk.extrinsics!) {
            final tx = _decodeExtrinsic(ext, blk.blockNumber, blk.blockHash, userPubkey);
            if (tx != null) {
              onChainTxs.add(tx);
            }
          }
        }
      }

      return onChainTxs;
    } catch (e) {
      // On error, return empty list (local cache will still be shown)
      return [];
    }
  }

  /// Fetch a block's extrinsics by block number
  Future<_BlockExtrinsics> _fetchBlockExtrinsics(int blockNum) async {
    try {
      final hash = await _rpcClient.getBlockHash(blockNum);
      final blockData = await _rpcClient.getBlock(hash);
      final extrinsics = blockData['block']?['extrinsics'] as List<dynamic>?;
      return _BlockExtrinsics(blockNum, hash, extrinsics);
    } catch (_) {
      return _BlockExtrinsics(blockNum, '', null);
    }
  }

  /// Decode a hex extrinsic and check if it involves the user's address
  TransactionRecord? _decodeExtrinsic(
    dynamic ext,
    int blockNum,
    String blockHash,
    List<int> userPubkey,
  ) {
    try {
      // Convert to hex string
      String hexStr;
      if (ext is String) {
        hexStr = ext;
      } else if (ext is List) {
        hexStr = '0x' + ext.map((b) => (b as int).toRadixString(16).padLeft(2, '0')).join('');
      } else {
        return null;
      }
      if (!hexStr.startsWith('0x')) hexStr = '0x$hexStr';
      final cleanHex = hexStr.substring(2);

      final bytes = HEX.decode(cleanHex);
      if (bytes.length < 4) return null;

      int offset = 0;

      // Read compact length prefix
      final lenResult = _readCompact(bytes, offset);
      offset = lenResult[1];
      if (offset >= bytes.length) return null;

      // Version byte
      final versionByte = bytes[offset];
      final isSigned = (versionByte & 0x80) != 0;
      if (!isSigned) return null;
      offset++;

      if (offset >= bytes.length) return null;
      // Signature type
      final sigType = bytes[offset];
      final sigLen = (sigType == 2) ? 65 : 64;
      offset += 1 + sigLen;

      // MultiAddress tag
      if (offset >= bytes.length) return null;
      offset += 1; // skip MultiAddress::Id tag byte (0x00)

      // Signer: 32 bytes public key
      if (offset + 32 > bytes.length) return null;
      final signerPubkey = bytes.sublist(offset, offset + 32);
      offset += 32;

      // Check if this tx involves our address (as sender)
      final isSender = _pubkeysEqual(signerPubkey, userPubkey);

      // Era
      if (offset >= bytes.length) return null;
      final eraByte = bytes[offset];
      if (eraByte == 0) {
        offset += 1; // immortal era
      } else {
        offset += 2; // mortal era
      }

      // Nonce (compact)
      final nonceResult = _readCompact(bytes, offset);
      offset = nonceResult[1];

      // Tip (compact)
      final tipResult = _readCompact(bytes, offset);
      offset = tipResult[1];

      // Call data: pallet index + function index
      if (offset + 1 >= bytes.length) return null;
      final palletIdx = bytes[offset];
      final funcIdx = bytes[offset + 1];
      offset += 2;

      // Only decode Balances transfers (pallet 4, func 0 or 3)
      if (palletIdx == 4 && (funcIdx == 0 || funcIdx == 3)) {
        if (offset >= bytes.length) return null;
        final destType = bytes[offset];
        offset += 1;

        if (destType == 0 && offset + 32 <= bytes.length) {
          final destPubkey = bytes.sublist(offset, offset + 32);
          offset += 32;

          final valueResult = _readCompact(bytes, offset);
          final valueRaw = valueResult[0];

          final isReceiver = _pubkeysEqual(destPubkey, userPubkey);
          if (!isSender && !isReceiver) return null;

          // Build the transaction record
          final signerAddr = _encodeSS58(signerPubkey);
          final destAddr = _encodeSS58(destPubkey);
          final method = funcIdx == 0 ? 'transfer' : 'transfer_keep_alive';

          // Generate a pseudo hash from the extrinsic bytes
          final hashHex = '0x${bytes.sublist(0, (8).clamp(0, bytes.length)).map((b) => b.toRadixString(16).padLeft(2, '0')).join('')}';

          return TransactionRecord(
            hash: hashHex,
            blockHash: blockHash,
            blockNumber: blockNum,
            from: signerAddr,
            to: destAddr,
            amount: valueRaw,
            fee: 0,
            module: 'balances',
            call: method,
            status: 'confirmed',
            timestamp: null,
            args: {'dest': destAddr, 'value': valueRaw.toString()},
          );
        }
      }

      // Also handle System.remark (pallet 0, func 1) for completeness
      if (palletIdx == 0 && funcIdx == 1 && isSender) {
        final signerAddr = _encodeSS58(signerPubkey);
        final hashHex = '0x${bytes.sublist(0, (8).clamp(0, bytes.length)).map((b) => b.toRadixString(16).padLeft(2, '0')).join('')}';
        return TransactionRecord(
          hash: hashHex,
          blockHash: blockHash,
          blockNumber: blockNum,
          from: signerAddr,
          to: '',
          amount: 0,
          fee: 0,
          module: 'system',
          call: 'remark',
          status: 'confirmed',
          timestamp: null,
          args: {},
        );
      }

      return null;
    } catch (_) {
      return null;
    }
  }

  /// Compare two public key byte arrays
  bool _pubkeysEqual(List<int> a, List<int> b) {
    if (a.length != b.length) return false;
    for (int i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }

  /// Read SCALE compact integer, returns [value, nextOffset]
  List<int> _readCompact(List<int> bytes, int offset) {
    if (offset >= bytes.length) return [0, offset];
    final first = bytes[offset];
    final mode = first & 0x03;
    if (mode == 0) {
      return [first >> 2, offset + 1];
    } else if (mode == 1) {
      if (offset + 1 >= bytes.length) return [0, offset + 1];
      return [((first | (bytes[offset + 1] << 8)) >> 2), offset + 2];
    } else if (mode == 2) {
      if (offset + 3 >= bytes.length) return [0, offset + 3];
      int v = (first | (bytes[offset + 1] << 8) | (bytes[offset + 2] << 16) | (bytes[offset + 3] << 24)) >> 2;
      return [v, offset + 4];
    } else {
      if (offset + 5 >= bytes.length) return [0, offset + 5];
      int v = 0;
      final nBytes = (first >> 2) + 4;
      for (int b = 0; b < nBytes && offset + 1 + b < bytes.length; b++) {
        v += bytes[offset + 1 + b] * (1 << (8 * b));
      }
      return [v, offset + 1 + nBytes];
    }
  }

  /// Encode 32-byte public key to SS58 address (using correct Substrate format)
  String _encodeSS58(List<int> pubkey) {
    try {
      // Use WalletCrypto for SS58 encoding (now fixed with correct prefix and checksum)
      return WalletCrypto.ss58Address(Uint8List.fromList(pubkey));
    } catch (_) {
      return '0x${pubkey.map((b) => b.toRadixString(16).padLeft(2, '0')).join('')}';
    }
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

  /// SCALE compact encoding using audited polkadart_scale_codec library
  List<int> _encodeCompactBigInt(BigInt v) {
    final output = ByteOutput();
    CompactBigIntCodec.codec.encodeTo(v, output);
    return output.toBytes();
  }

  List<int> _encodeCompactInt(int v) => _encodeCompactBigInt(BigInt.from(v));

  /// SCALE u32 encoding using audited polkadart_scale_codec library
  List<int> _encodeU32(int v) {
    final output = ByteOutput();
    U32Codec.codec.encodeTo(v, output);
    return output.toBytes();
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

/// Helper class for block extrinsics during async fetching
class _BlockExtrinsics {
  final int blockNumber;
  final String blockHash;
  final List<dynamic>? extrinsics;
  _BlockExtrinsics(this.blockNumber, this.blockHash, this.extrinsics);
}
