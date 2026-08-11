import 'package:verdis_wallet/shared/models/wallet_models.dart';

/// Detailed network information for Explorer
class NetworkInfoData { // Last 10 data points for TPS chart

  const NetworkInfoData({
    required this.chainName,
    required this.chainType,
    required this.consensus,
    required this.runtimeVersion,
    required this.specVersion,
    required this.genesisHash,
    required this.peers,
    required this.bestBlock,
    required this.finalizedBlock,
    required this.currentTps,
    required this.peakTps,
    required this.tpsHistory,
  });
  final String chainName;
  final String chainType;
  final String consensus;
  final String runtimeVersion;
  final int specVersion;
  final String genesisHash;
  final int peers;
  final int bestBlock;
  final int finalizedBlock;
  final double currentTps;
  final double peakTps;
  final List<double> tpsHistory;
}

/// Search result wrapper for Explorer
enum SearchResultType { block, transaction, validator, account, notFound }

class SearchResultData {

  const SearchResultData({
    required this.query,
    required this.type,
    this.block,
    this.transaction,
    this.validator,
    this.accountAddress,
  });
  final String query;
  final SearchResultType type;
  final BlockInfo? block;
  final TransactionRecord? transaction;
  final ValidatorInfo? validator;
  final String? accountAddress;
}

/// Abstract repository interface for Verdis Explorer
abstract class ExplorerRepository {
  /// Fetch recent blocks with pagination
  Future<List<BlockInfo>> getLatestBlocks({int page = 0, int limit = 20});

  /// Fetch block details by hash or block number
  Future<BlockInfo?> getBlockDetail(String hashOrNumber);

  /// Fetch recent transactions across blocks with pagination
  Future<List<TransactionRecord>> getLatestTransactions({int page = 0, int limit = 20});

  /// Fetch list of network validators
  Future<List<ValidatorInfo>> getValidators();

  /// Fetch full network health, consensus, and block height statistics
  Future<NetworkInfoData> getNetworkInfo();

  /// Search by block height, block hash, transaction hash, or account address
  Future<SearchResultData> search(String query);
}
