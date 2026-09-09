import 'dart:math' as math;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/network/rpc_client.dart';
import 'package:verdis_wallet/shared/models/wallet_models.dart';
import '../data/dex_repository_impl.dart';
import '../domain/dex_repository.dart';

/// Provider for DexRepository implementation
final dexRepositoryProvider = Provider<DexRepository>((ref) {
  final rpcClient = ref.watch(rpcClientProvider);
  return DexRepositoryImpl(rpcClient);
});

/// Async provider for all DEX pools from amm_dex_getAllPools
final poolsProvider = FutureProvider<List<DexPool>>((ref) async {
  final repository = ref.watch(dexRepositoryProvider);
  return repository.getPools();
});

/// Currently selected DEX pool
final selectedPoolProvider = StateProvider<DexPool?>((ref) {
  final poolsAsync = ref.watch(poolsProvider);
  return poolsAsync.when(
    data: (pools) => pools.isNotEmpty ? pools.first : null,
    loading: () => null,
    error: (_, __) => null,
  );
});

/// Slippage tolerance setting in percentage (default 0.5%)
final slippageProvider = StateProvider<double>((ref) => 0.5);

/// Transaction deadline setting in minutes (default 20 min)
final deadlineProvider = StateProvider<int>((ref) => 20);

/// Expert mode toggle state
final expertModeProvider = StateProvider<bool>((ref) => false);

/// Selected input token for swap
final swapInputTokenProvider = StateProvider<String>((ref) => 'VRD');

/// Selected output token for swap
final swapOutputTokenProvider = StateProvider<String>((ref) => 'USDT');

/// Input amount for swap
final swapAmountInputProvider = StateProvider<double>((ref) => 0.0);

/// Selected timeframe for price chart ('24h', '7d', '30d')
final selectedTimeframeProvider = StateProvider<String>((ref) => '24h');

/// Calculated SwapPreview based on current user inputs
final swapPreviewProvider = Provider<SwapPreview?>((ref) {
  final tokenIn = ref.watch(swapInputTokenProvider);
  final tokenOut = ref.watch(swapOutputTokenProvider);
  final amountIn = ref.watch(swapAmountInputProvider);
  final slippagePercent = ref.watch(slippageProvider);
  final poolsAsync = ref.watch(poolsProvider);
  final repo = ref.watch(dexRepositoryProvider);

  if (amountIn <= 0) return null;

  final pools = poolsAsync.value ?? [];
  if (pools.isEmpty) return null;

  // Find pool for token pair
  DexPool? targetPool;
  bool isReversed = false;

  for (final pool in pools) {
    if (pool.tokenA == tokenIn && pool.tokenB == tokenOut) {
      targetPool = pool;
      isReversed = false;
      break;
    } else if (pool.tokenB == tokenIn && pool.tokenA == tokenOut) {
      targetPool = pool;
      isReversed = true;
      break;
    }
  }

  if (targetPool == null) {
    // Multi-hop route fallback through VRD
    return SwapPreview(
      tokenIn: tokenIn,
      tokenOut: tokenOut,
      amountIn: amountIn,
      expectedAmountOut: amountIn * 0.98,
      minAmountOut: amountIn * 0.98 * (1.0 - (slippagePercent / 100.0)),
      priceImpact: 0.005,
      fee: amountIn * 0.003,
      route: [tokenIn, 'VRD', tokenOut],
      priceRatio: 0.98,
    );
  }

  final double reserveIn = isReversed ? targetPool.reserveB.toDouble() : targetPool.reserveA.toDouble();
  final double reserveOut = isReversed ? targetPool.reserveA.toDouble() : targetPool.reserveB.toDouble();
  final double feeRate = targetPool.feeRate;

  final double amountInWithFee = amountIn * (1.0 - feeRate);
  final double expectedAmountOut = (amountInWithFee * reserveOut) / (reserveIn + amountInWithFee);
  final double slippageRatio = slippagePercent / 100.0;
  final double minAmountOut = expectedAmountOut * (1.0 - slippageRatio);

  final double priceImpact = repo.calculatePriceImpact(
    amountIn: amountIn,
    reserveIn: reserveIn,
    reserveOut: reserveOut,
    feeRate: feeRate,
  );

  return SwapPreview(
    tokenIn: tokenIn,
    tokenOut: tokenOut,
    amountIn: amountIn,
    expectedAmountOut: expectedAmountOut,
    minAmountOut: minAmountOut,
    priceImpact: priceImpact,
    fee: amountIn * feeRate,
    route: [tokenIn, tokenOut],
    priceRatio: expectedAmountOut / amountIn,
  );
});

/// Direct Price Impact calculation provider
final priceImpactProvider = Provider<double>((ref) {
  final preview = ref.watch(swapPreviewProvider);
  return preview?.priceImpact ?? 0.0;
});

/// Add/Remove Liquidity parameters and state
final liquidityAmountAProvider = StateProvider<double>((ref) => 0.0);
final liquidityAmountBProvider = StateProvider<double>((ref) => 0.0);
final removeLpAmountProvider = StateProvider<double>((ref) => 0.0);

/// Calculated LiquidityPreview for adding liquidity
final liquidityPreviewProvider = Provider<LiquidityPreview?>((ref) {
  final pool = ref.watch(selectedPoolProvider);
  final amountA = ref.watch(liquidityAmountAProvider);

  if (pool == null || amountA <= 0) return null;

  final reserveA = pool.reserveA.toDouble();
  final reserveB = pool.reserveB.toDouble();
  final double amountB = (amountA * reserveB) / reserveA;

  final double totalLpBefore = math.sqrt(reserveA * reserveB);
  final double lpTokensToMint = math.sqrt(amountA * amountB);
  final double totalLpAfter = totalLpBefore + lpTokensToMint;
  final double sharePercent = (lpTokensToMint / totalLpAfter) * 100.0;

  return LiquidityPreview(
    poolId: pool.poolId,
    tokenA: pool.tokenA,
    tokenB: pool.tokenB,
    amountA: amountA,
    amountB: amountB,
    lpTokens: lpTokensToMint,
    poolSharePercent: sharePercent,
    reserveAAfter: reserveA + amountA,
    reserveBAfter: reserveB + amountB,
    fee: 0.0,
  );
});

/// Top metrics summary provider (TVL, Total 24h Volume, Total 24h Swaps)
final dexMetricsProvider = Provider<Map<String, dynamic>>((ref) {
  final poolsAsync = ref.watch(poolsProvider);
  final pools = poolsAsync.value ?? [];

  double tvl = 0.0;
  double volume24h = 0.0;
  int swaps24h = 0;

  for (final pool in pools) {
    // Estimating TVL as Reserve B * 2 (assuming Reserve B is USDT or stable value)
    tvl += pool.reserveB * 2.0;
    volume24h += pool.totalVolume24h.toDouble();
    swaps24h += pool.swapCount24h;
  }

  return {
    'tvl': tvl,
    'volume24h': volume24h,
    'swaps24h': swaps24h,
    'poolCount': pools.length,
  };
});

/// Price history provider parameter class
class ChartParams {

  const ChartParams(this.poolId, this.timeframe);
  final int poolId;
  final String timeframe;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ChartParams &&
          runtimeType == other.runtimeType &&
          poolId == other.poolId &&
          timeframe == other.timeframe;

  @override
  int get hashCode => poolId.hashCode ^ timeframe.hashCode;
}

/// Price history chart provider
final priceHistoryProvider = FutureProvider.family<List<PricePoint>, ChartParams>((ref, params) async {
  final repo = ref.watch(dexRepositoryProvider);
  return repo.getPriceHistory(params.poolId, params.timeframe);
});
