import re

with open('/opt/verdis-wallet/lib/features/transactions/data/transaction_repository_impl.dart', 'r') as f:
    content = f.read()

# Replace the getTransactionHistory method with one that fetches from chain
old_method = """  @override
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
  }"""

new_method = """  @override
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
  }"""

content = content.replace(old_method, new_method)

# Add imports for WalletCrypto and Uint8List (if not already there)
if "import 'package:verdis_wallet/core/security/wallet_crypto.dart';" not in content:
    content = content.replace(
        "import 'package:verdis_wallet/core/network/rpc_client.dart';",
        "import 'package:verdis_wallet/core/network/rpc_client.dart';\nimport 'package:verdis_wallet/core/security/wallet_crypto.dart';"
    )

# Add the _BlockExtrinsics helper class at the end of the file
# Find the last closing brace of the class
class_end_marker = "  // === SS58 decoding ==="
if class_end_marker in content:
    # Add the helper class before the SS58 decoding section
    helper_class = """
/// Helper class for block extrinsics during async fetching
class _BlockExtrinsics {
  final int blockNumber;
  final String blockHash;
  final List<dynamic>? extrinsics;
  _BlockExtrinsics(this.blockNumber, this.blockHash, this.extrinsics);
}

"""

    content = content.replace(class_end_marker, helper_class + class_end_marker)

with open('/opt/verdis-wallet/lib/features/transactions/data/transaction_repository_impl.dart', 'w') as f:
    f.write(content)
print('transaction_repository_impl.dart updated with on-chain history.')
print(f'File size: {len(content)} chars')
