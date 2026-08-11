import 'package:verdis_wallet/shared/models/wallet_models.dart';

/// Abstract repository defining transaction operations for Verdis network.
abstract class TransactionRepository {
  /// Submit a transfer extrinsic (balances.transfer)
  Future<String> sendTransfer({
    required String recipient,
    required double amount,
    String feeLevel = 'standard',
  });

  /// Estimate network fee for a transfer (payment_queryInfo)
  Future<double> estimateFee({
    required String recipient,
    required double amount,
    String speed = 'standard',
  });

  /// Fetch full transaction history with optional filter & pagination
  Future<List<TransactionRecord>> getTransactionHistory({
    String? filter, // 'All' | 'Send' | 'Receive' | 'Swap' | 'Stake'
    int page = 1,
    int limit = 20,
  });

  /// Get details for a single transaction by its hash
  Future<TransactionRecord?> getTransactionDetail(String txHash);
}
