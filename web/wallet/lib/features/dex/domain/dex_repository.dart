import 'package:verdis_wallet/shared/models/wallet_models.dart';

/// Preview details for a token swap transaction
class SwapPreview {

  const SwapPreview({
    required this.tokenIn,
    required this.tokenOut,
    required this.amountIn,
    required this.expectedAmountOut,
    required this.minAmountOut,
    required this.priceImpact,
    required this.fee,
    required this.route,
    required this.priceRatio,
  });
  final String tokenIn;
  final String tokenOut;
  final double amountIn;
  final double expectedAmountOut;
  final double minAmountOut;
  final double priceImpact;
  final double fee;
  final List<String> route;
  final double priceRatio;
}

/// Preview details for liquidity provisioning/removal
class LiquidityPreview {

  const LiquidityPreview({
    required this.poolId,
    required this.tokenA,
    required this.tokenB,
    required this.amountA,
    required this.amountB,
    required this.lpTokens,
    required this.poolSharePercent,
    required this.reserveAAfter,
    required this.reserveBAfter,
    required this.fee,
  });
  final int poolId;
  final String tokenA;
  final String tokenB;
  final double amountA;
  final double amountB;
  final double lpTokens;
  final double poolSharePercent;
  final double reserveAAfter;
  final double reserveBAfter;
  final double fee;
}

/// Historical price data point for charts
class PricePoint {

  const PricePoint({
    required this.timestamp,
    required this.price,
    required this.volume,
    required this.high,
    required this.low,
  });
  final DateTime timestamp;
  final double price;
  final double volume;
  final double high;
  final double low;
}

/// Abstract Repository for Verdis DEX Operations
abstract class DexRepository {
  /// Fetches all active DEX liquidity pools via amm_dex_getAllPools
  Future<List<DexPool>> getPools();

  /// Fetches detailed pool info by ID via amm_dex_getPool
  Future<DexPool> getPoolDetail(int poolId);

  /// Fetches current token price in pool via amm_dex_getPrice
  Future<double> getPrice(int poolId);

  /// Fetches liquidity reserves and LP supply via amm_dex_getLiquidity
  Future<Map<String, dynamic>> getLiquidity(int poolId);

  /// Executes token swap extrinsic (amm_dex.swap)
  Future<String> swap({
    required int poolId,
    required String tokenIn,
    required String tokenOut,
    required double amountIn,
    required double minAmountOut,
    required String recipient,
  });

  /// Adds liquidity to a pool extrinsic (amm_dex.addLiquidity)
  Future<String> addLiquidity({
    required int poolId,
    required double amountA,
    required double amountB,
    required double minAmountA,
    required double minAmountB,
  });

  /// Removes liquidity from a pool extrinsic (amm_dex.removeLiquidity)
  Future<String> removeLiquidity({
    required int poolId,
    required double lpAmount,
    required double minAmountA,
    required double minAmountB,
  });

  /// Calculates price impact using constant product formula:
  /// impact = 1 - (reserveB_after / reserveB_before)
  double calculatePriceImpact({
    required double amountIn,
    required double reserveIn,
    required double reserveOut,
    double feeRate = 0.003,
  });

  /// Calculates slippage based on expected output vs minimum received
  double calculateSlippage({
    required double expectedAmount,
    required double minReceived,
  });

  /// Fetches price history data points for charting (24h, 7d, 30d)
  Future<List<PricePoint>> getPriceHistory(int poolId, String timeframe);
}
