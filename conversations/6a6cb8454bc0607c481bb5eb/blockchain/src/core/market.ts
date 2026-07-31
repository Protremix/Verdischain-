/**
 * Token Market Data & Volume Tracking
 * 
 * Extends DEX with volume tracking, price history, and market data.
 * Makes VRS a live, tradable token with real market activity.
 */

import { DEX } from './dex';

export interface SwapRecord {
  timestamp: number;
  trader: string;
  tokenIn: string;
  tokenOut: string;
  amountIn: number;
  amountOut: number;
  fee: number;
  poolId: string;
  blockNumber: number;
}

export interface PricePoint {
  timestamp: number;
  blockNumber: number;
  price: number;
  poolId: string;
  pair: string;
}

export interface MarketStats {
  symbol: string;
  priceUSD: number;
  priceChange24h: number;
  volume24h: number;
  totalVolume: number;
  totalSwaps: number;
  liquidity: number;
  marketCap: number;
  circulatingSupply: number;
  pools: Array<{
    pair: string;
    price: number;
    reserves: { tokenA: string; tokenB: string; reserveA: number; reserveB: number };
    tvl: number;
    volume24h: number;
    swaps24h: number;
  }>;
  recentSwaps: SwapRecord[];
  priceHistory: PricePoint[];
}

/**
 * Wraps the DEX to add market data tracking.
 * Must be called on every swap to record the trade.
 */
export class MarketTracker {
  private swapHistory: SwapRecord[] = [];
  private priceHistory: PricePoint[] = [];
  private totalVolumeAllTime: number = 0;
  private totalSwapCount: number = 0;

  constructor(private dex: DEX) {}

  /**
   * Records a swap after it executes. Called by the API layer.
   */
  recordSwap(
    trader: string,
    tokenIn: string,
    tokenOut: string,
    amountIn: number,
    amountOut: number,
    fee: number,
    poolId: string,
    blockNumber: number
  ): void {
    const record: SwapRecord = {
      timestamp: Date.now(),
      trader,
      tokenIn,
      tokenOut,
      amountIn,
      amountOut,
      fee,
      poolId,
      blockNumber,
    };
    this.swapHistory.push(record);
    this.totalVolumeAllTime += amountIn;
    this.totalSwapCount++;

    // Record price point
    const pool = this.dex.getPool(poolId);
    if (pool) {
      const price = pool.reserveA > 0 ? pool.reserveB / pool.reserveA : 0;
      this.priceHistory.push({
        timestamp: Date.now(),
        blockNumber,
        price,
        poolId,
        pair: `${pool.tokenA}/${pool.tokenB}`,
      });
    }

    // Keep last 1000 records
    if (this.swapHistory.length > 1000) {
      this.swapHistory = this.swapHistory.slice(-500);
    }
    if (this.priceHistory.length > 1000) {
      this.priceHistory = this.priceHistory.slice(-500);
    }
  }

  /**
   * Records a price snapshot for all pools.
   */
  recordPrices(blockNumber: number): void {
    const pools = this.dex.getAllPools();
    for (const pool of pools) {
      const price = pool.reserveA > 0 ? pool.reserveB / pool.reserveA : 0;
      this.priceHistory.push({
        timestamp: Date.now(),
        blockNumber,
        price,
        poolId: pool.id,
        pair: `${pool.tokenA}/${pool.tokenB}`,
      });
    }
    if (this.priceHistory.length > 1000) {
      this.priceHistory = this.priceHistory.slice(-500);
    }
  }

  /**
   * Returns comprehensive market statistics for a given token.
   */
  getMarketStats(tokenSymbol: string, circulatingSupply: number, maxSupply: number): MarketStats {
    const pools = this.dex.getAllPools();
    const now = Date.now();
    const dayAgo = now - 24 * 60 * 60 * 1000;

    // Filter swaps in last 24h
    const swaps24h = this.swapHistory.filter(s => s.timestamp >= dayAgo);
    const volume24h = swaps24h.reduce((sum, s) => sum + s.amountIn, 0);

    // Find the primary price pool (highest liquidity involving this token)
    let primaryPrice = 0;
    let bestPool: { tvl: number; price: number } | null = null;
    const poolStats = pools.map(pool => {
      const involvesToken = pool.tokenA === tokenSymbol || pool.tokenB === tokenSymbol;
      const price = pool.reserveA > 0 ? pool.reserveB / pool.reserveA : 0;
      const tvl = pool.reserveA > 0 && pool.reserveB > 0 ? Math.max(pool.reserveA, pool.reserveB) * 2 : 0;
      const poolSwaps24h = swaps24h.filter(s => s.poolId === pool.id);
      const poolVol24h = poolSwaps24h.reduce((sum, s) => sum + s.amountIn, 0);

      if (involvesToken && tvl > (bestPool?.tvl || 0)) {
        bestPool = { tvl, price };
        if (pool.tokenA === tokenSymbol) {
          primaryPrice = price; // price of token in terms of tokenB
        } else {
          primaryPrice = 1 / price; // invert if token is tokenB
        }
      }

      return {
        pair: `${pool.tokenA}/${pool.tokenB}`,
        price,
        reserves: {
          tokenA: pool.tokenA,
          tokenB: pool.tokenB,
          reserveA: pool.reserveA,
          reserveB: pool.reserveB,
        },
        tvl,
        volume24h: poolVol24h,
        swaps24h: poolSwaps24h.length,
      };
    });

    // Calculate 24h price change
    let priceChange24h = 0;
    const pricePoints24h = this.priceHistory.filter(p => p.timestamp >= dayAgo);
    if (pricePoints24h.length >= 2) {
      const first = pricePoints24h[0].price;
      const last = pricePoints24h[pricePoints24h.length - 1].price;
      if (first > 0) {
        priceChange24h = ((last - first) / first) * 100;
      }
    }

    const recentSwaps = this.swapHistory.slice(-20).reverse();

    return {
      symbol: tokenSymbol,
      priceUSD: primaryPrice,
      priceChange24h,
      volume24h,
      totalVolume: this.totalVolumeAllTime,
      totalSwaps: this.totalSwapCount,
      liquidity: poolStats.reduce((sum, p) => sum + p.tvl, 0),
      marketCap: primaryPrice * circulatingSupply,
      circulatingSupply,
      pools: poolStats,
      recentSwaps,
      priceHistory: this.priceHistory.slice(-100),
    };
  }

  /**
   * Returns recent swap history.
   */
  getSwapHistory(limit: number = 50): SwapRecord[] {
    return this.swapHistory.slice(-limit).reverse();
  }

  /**
   * Returns price history for a pool.
   */
  getPriceHistory(poolId: string, limit: number = 100): PricePoint[] {
    return this.priceHistory.filter(p => p.poolId === poolId).slice(-limit).reverse();
  }

  /**
   * Serializes market data for persistence.
   */
  exportData(): any {
    return {
      swapHistory: this.swapHistory.slice(-200),
      priceHistory: this.priceHistory.slice(-200),
      totalVolumeAllTime: this.totalVolumeAllTime,
      totalSwapCount: this.totalSwapCount,
    };
  }

  /**
   * Restores market data from persistence.
   */
  importData(data: any): void {
    if (data.swapHistory) this.swapHistory = data.swapHistory;
    if (data.priceHistory) this.priceHistory = data.priceHistory;
    if (data.totalVolumeAllTime) this.totalVolumeAllTime = data.totalVolumeAllTime;
    if (data.totalSwapCount) this.totalSwapCount = data.totalSwapCount;
  }
}
